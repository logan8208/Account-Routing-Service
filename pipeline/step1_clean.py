"""Step 1 - ingest, clean, de-duplicate, link hierarchies, decide eligibility.

Reads the pristine backup of accounts-XLSX.xlsx, and writes accounts-XLSX.xlsx with:
  * the 12 original columns untouched (A-L),
  * "after" copies of every original column (suffix _clean) plus derived columns, in a
    different color, ending with an Agent Notes column explaining each edit,
  * extra sheets: summary, exclusions, entities (merge groups), hierarchy, review_flags,
    column_guide.
Also writes output/step1_accounts.json for the later pipeline steps.

Run:  python pipeline/step1_clean.py
"""
import json
import re
import sys
from collections import Counter, defaultdict

import openpyxl
import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from config import *  # noqa: E402,F401,F403

STATUS_ELIGIBLE = "eligible"
STATUS_EXCLUDED = "excluded"
STATUS_MERGED = "merged_duplicate"


# ---------------------------------------------------------------- field cleaning
def norm_host(website):
    """'https://WWW.Foo.com/en/home' -> ('foo.com', '/en/home')."""
    w = website.strip().lower()
    w = re.sub(r"^https?://", "", w)
    host, _, path = w.partition("/")
    host = re.sub(r"^www\.", "", host).rstrip(".")
    return host, path.strip("/")


def classify_website(website):
    host, path = norm_host(website)
    if host in PROFILE_HOSTS:
        return {"website_clean": f"{host}/{path}" if path else host, "domain_key": "",
                "website_type": "social_profile"}
    labels = host.split(".")
    wtype = "subdomain" if len(labels) > 2 else "company_domain"
    return {"website_clean": host, "domain_key": host, "website_type": wtype,
            "root_domain": ".".join(labels[-2:])}


def fix_mojibake(text):
    """Repair UTF-8 text that was decoded as Latin-1 ('SÃ£o Paulo' -> 'São Paulo'). Only applied
    when the text has the tell-tale 'Ã'/'Â' pattern and the repair decodes cleanly."""
    if not re.search("[ÃÂ][\u0080-¿]", text):
        return text
    try:
        return text.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text


def to_int(v):
    v = str(v).strip()
    return int(float(v)) if v not in ("", "nan", "None") else None


def load_raw():
    df = pd.read_excel(RAW_ACCOUNTS, dtype=str, keep_default_na=False)
    assert list(df.columns) == ORIGINAL_COLUMNS, df.columns
    assert df.account_id.is_unique
    return [dict(r) for r in df.to_dict("records")]


class UnionFind:
    def __init__(self):
        self.p = {}

    def find(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        self.p[self.find(a)] = self.find(b)


def main():
    raw = load_raw()
    rows = []
    for r in raw:
        c = {"account_id": r["account_id"], "raw": r, "agent_notes": [], "flags": []}
        c["company_name_clean"] = " ".join(r["company_name"].split())
        if c["company_name_clean"] != r["company_name"]:
            c["agent_notes"].append("Trimmed extra whitespace in company name.")
        c.update(classify_website(r["website"]))
        if c["website_clean"] != r["website"]:
            c["agent_notes"].append(
                "Website normalized to bare domain (lowercase, no http/www/path).")
        if c["website_type"] == "social_profile":
            c["flags"].append("website_is_profile_page")
            c["agent_notes"].append(
                "Website is a social/profile page, not the company's domain; never merged on this "
                "URL alone (D22). The real company domain needs to be updated via enrichment.")
        c["city_clean"] = fix_mojibake(r["city"].strip())
        if c["city_clean"] != r["city"].strip():
            c["agent_notes"].append(
                f"City '{r['city']}' had an encoding error in the XLSX export (UTF-8 read as "
                f"Latin-1); repaired to '{c['city_clean']}', which matches accounts.csv.")
        c["state_clean"] = r["state"].strip().upper()
        c["country_clean"] = r["country"].strip()
        c["employee_count_clean"] = to_int(r["employee_count"])
        c["funding_stage_clean"] = r["funding_stage"].strip()
        c["last_funding_year_clean"] = to_int(r["last_funding_year"])
        c["industry_clean"] = r["industry"].strip()
        c["spend_clean"] = to_int(r["existing_spend_usd_t12m"]) or 0
        c["notes_clean"] = r["notes"].strip()
        rows.append(c)
    by_id = {c["account_id"]: c for c in rows}

    # ------------------------------------------------------------ location (D13)
    city_states = defaultdict(set)
    for c in rows:
        if c["state_clean"] in REGION_BY_STATE:
            city_states[c["city_clean"].lower()].add(c["state_clean"])
    for c in rows:
        if not c["state_clean"]:
            cands = city_states.get(c["city_clean"].lower(), set())
            if len(cands) == 1:
                c["state_clean"] = next(iter(cands))
                c["flags"].append("state_inferred_from_city")
                c["agent_notes"].append(
                    f"State was blank; filled '{c['state_clean']}' because every other "
                    f"'{c['city_clean']}' row in the file has that state. Double-check state "
                    f"enrichment later.")
        st = c["state_clean"]
        c["region"] = REGION_BY_STATE.get(st, "NOT_COVERED")
        derived_country = ("United States" if st in US_STATES else
                           "Canada" if st in CANADA_PROVINCES else c["country_clean"])
        if derived_country != c["country_clean"]:
            c["agent_notes"].append(
                f"Country was '{c['country_clean'] or 'blank'}'; set to '{derived_country}' from "
                f"the state/province (rules.md: do not trust the country column).")
            c["country_clean"] = derived_country
        if c["region"] == "NOT_COVERED":
            if st == "KA":
                c["agent_notes"].append(
                    "State 'KA' is Karnataka (Bangalore, India), not Kansas (KS).")
            where = ", ".join(x for x in (c["city_clean"], st, c["country_clean"]) if x)
            c["region_detail"] = f"HQ {where} is outside the team's US/Canada territory"

    # ------------------------------------------------------------ same-entity merges (D8)
    uf = UnionFind()
    name_index = defaultdict(list)
    for c in rows:
        name_index[c["company_name_clean"].lower()].append(c["account_id"])
        uf.find(c["account_id"])
    merge_evidence = defaultdict(list)  # account_id -> evidence strings
    by_domain = defaultdict(list)
    for c in rows:
        if c["domain_key"]:
            by_domain[c["domain_key"]].append(c["account_id"])
    for dom, ids in by_domain.items():
        for i in ids[1:]:
            uf.union(i, ids[0])
        if len(ids) > 1:
            for i in ids:
                merge_evidence[i].append(f"same website domain '{dom}'")

    note_links = []  # (kind, child_id, target_id)
    unresolved_targets = []
    for c in rows:
        n = c["notes_clean"]
        for kind, pat in (("same_entity", SAME_ENTITY_NOTE), ("child", CHILD_NOTE),
                          ("acquired", ACQUIRED_NOTE)):
            m = pat.match(n)
            if not m:
                continue
            tgt = m.group("target").strip()
            hits = name_index.get(tgt.lower(), [])
            if len(hits) != 1:
                unresolved_targets.append((c["account_id"], kind, tgt, len(hits)))
                c["flags"].append("relationship_target_not_found")
                c["agent_notes"].append(
                    f"Note names '{tgt}' but {len(hits)} matching records were found; "
                    f"relationship left unresolved.")
                continue
            note_links.append((kind, c["account_id"], hits[0]))
            if kind == "same_entity":
                uf.union(c["account_id"], hits[0])
                merge_evidence[c["account_id"]].append(f"note: \"{n}\"")
                merge_evidence[hits[0]].append(
                    f"{c['account_id']}'s note says it is the same company")

    groups = defaultdict(list)
    for c in rows:
        groups[uf.find(c["account_id"])].append(c["account_id"])

    note_targets = {t for k, _, t in note_links if k == "same_entity"}

    def primary_rank(aid):
        c = by_id[aid]
        filled = sum(1 for k in ("employee_count", "last_funding_year", "state", "notes")
                     if c["raw"][k].strip())
        return (aid in note_targets, c["employee_count_clean"] is not None,
                not DUPLICATE_Q_NOTE.match(c["notes_clean"]), filled, -int(aid[4:]))

    entities = {}
    for members in groups.values():
        members.sort()
        primary = max(members, key=primary_rank)
        eid = f"ENT-{primary[4:]}"
        entities[eid] = {"entity_id": eid, "primary": primary, "members": members}
        for aid in members:
            by_id[aid]["entity_id"] = eid
            by_id[aid]["is_primary"] = aid == primary

    # consolidate each multi-record entity onto its primary record
    for ent in entities.values():
        p = by_id[ent["primary"]]
        others = [by_id[a] for a in ent["members"] if a != ent["primary"]]
        ent["total_spend"] = sum(by_id[a]["spend_clean"] for a in ent["members"])
        notes = []
        for a in [ent["primary"]] + [o["account_id"] for o in others]:
            n = by_id[a]["notes_clean"]
            if n and not SAME_ENTITY_NOTE.match(n) and n not in notes:
                notes.append(n)
        ent["notes_combined"] = notes
        if not others:
            continue
        for fld in ("employee_count_clean", "last_funding_year_clean", "funding_stage_clean",
                    "industry_clean", "state_clean", "city_clean"):
            # "Unknown" funding stage is a placeholder, not a competing value
            vals = {o[fld] for o in [p] + others if o[fld] not in (None, "", "Unknown")}
            if len(vals) > 1:
                p["flags"].append("merge_field_conflict")
                p["agent_notes"].append(
                    f"Merged records disagree on {fld.replace('_clean', '')}: {sorted(map(str, vals))}; "
                    f"kept this record's value.")
            if p[fld] in (None, "", "Unknown") and vals:
                donor = next(o for o in others if o[fld] in vals)
                p[fld] = donor[fld]
                p["agent_notes"].append(
                    f"{fld.replace('_clean', '')} was blank; filled '{p[fld]}' from duplicate "
                    f"{donor['account_id']}.")
        ids = ", ".join(o["account_id"] for o in others)
        p["agent_notes"].append(f"Primary record for entity {ent['entity_id']}; merged {ids} "
                                f"into it (same company).")
        if ent["total_spend"] != p["spend_clean"]:
            p["agent_notes"].append(
                f"Entity spend across merged records is ${ent['total_spend']:,} "
                f"(this row alone: ${p['spend_clean']:,}).")
        for o in others:
            ev = "; ".join(dict.fromkeys(merge_evidence[o["account_id"]])) or "linked records"
            o["merge_reason"] = (f"Duplicate of {p['account_id']} ({p['company_name_clean']}) - "
                                 f"same company: {ev}.")
            o["agent_notes"].append(o["merge_reason"])
        # region must be re-derived if a state was filled from a duplicate
        p["region"] = REGION_BY_STATE.get(p["state_clean"], "NOT_COVERED")

    # ------------------------------------------------------------ hierarchy + acquisitions
    hierarchy = []
    for kind, child, target in note_links:
        tgt_primary = by_id[by_id[target]["entity_id"].replace("ENT-", "ACC-")]
        if kind == "child":
            by_id[child]["parent_account_id"] = tgt_primary["account_id"]
            by_id[child]["agent_notes"].append(
                f"Business unit of {tgt_primary['company_name_clean']} "
                f"({tgt_primary['account_id']}). Kept as its own account; routes to the parent's "
                f"owner (D8).")
            hierarchy.append({"child_account_id": child, "relationship": "business_unit_of",
                              "parent_account_id": tgt_primary["account_id"]})
        elif kind == "acquired":
            by_id[child]["acquirer_account_id"] = tgt_primary["account_id"]
            hierarchy.append({"child_account_id": child, "relationship": "acquired_by",
                              "parent_account_id": tgt_primary["account_id"]})

    # ------------------------------------------------------------ eligibility per entity
    ent_status = {}
    for ent in entities.values():
        p = by_id[ent["primary"]]
        reasons = []
        notes = ent["notes_combined"]
        for n in notes:
            m = ACQUIRED_NOTE.match(n)
            if m:
                acq = p.get("acquirer_account_id")
                reasons.append(("no_longer_exists",
                                f"Acquired by {m.group('target')} in {m.group('year')}; site "
                                f"redirects to the acquirer" + (f" ({acq})" if acq else "")))
            elif DEFUNCT_NOTE.match(n):
                reasons.append(("no_longer_exists", f"Notes: \"{n}\""))
            if COMPETITOR_NOTE.match(n):
                reasons.append(("competitor", f"Core product is a speech engine. Notes: \"{n}\""))
        if ent["total_spend"] > 0:
            src = [a for a in ent["members"] if by_id[a]["spend_clean"] > 0]
            reasons.append(("existing_customer",
                            f"Spent ${ent['total_spend']:,} with us in the last 12 months"
                            + ("" if src == [p["account_id"]] else
                               f" (spend is on {', '.join(src)})")
                            + "; owned by account management."))
            if any(CHURNED_NOTE.match(n) for n in notes):
                p["flags"].append("data_conflict_churned_but_has_spend")
                p["agent_notes"].append(
                    "Data conflict: notes say churned, but trailing-12-month spend is above $0. "
                    "Treated as a customer per rules.md (spend = customer).")
        if p["region"] == "NOT_COVERED":
            reasons.append(("territory_not_covered", p.get("region_detail") or
                            f"State '{p['state_clean']}' not in the team's territory"))
        emp = p["employee_count_clean"]
        if emp is not None and emp < MIN_EMPLOYEES:
            reasons.append(("under_20_employees", f"{emp} employees (minimum is 20)"))
        ent["reasons"] = reasons
        ent_status[ent["entity_id"]] = STATUS_EXCLUDED if reasons else STATUS_ELIGIBLE

    # children of customer parents follow the parent's owner = account management (D8 + D6)
    for h in hierarchy:
        if h["relationship"] != "business_unit_of":
            continue
        child_ent = entities[by_id[h["child_account_id"]]["entity_id"]]
        parent_ent = entities[by_id[h["parent_account_id"]]["entity_id"]]
        if any(k == "existing_customer" for k, _ in parent_ent["reasons"]):
            child_ent["reasons"].append(
                ("parent_is_customer",
                 f"Business unit of {h['parent_account_id']}, which is an existing customer; the "
                 f"parent's owner (account management) owns this account too."))
            ent_status[child_ent["entity_id"]] = STATUS_EXCLUDED
            by_id[h["child_account_id"]]["flags"].append("owner_decision_child_of_customer")
        elif ent_status[parent_ent["entity_id"]] == STATUS_EXCLUDED:
            by_id[h["child_account_id"]]["flags"].append("parent_excluded_child_evaluated_alone")

    # ------------------------------------------------------------ per-row status + segment
    for c in rows:
        ent = entities[c["entity_id"]]
        if not c["is_primary"]:
            c["status"] = STATUS_MERGED
            tail = ""
            if ent_status[ent["entity_id"]] == STATUS_EXCLUDED:
                tail = " That account is excluded: " + "; ".join(d for _, d in ent["reasons"])
            c["exclusion_reason"] = c["merge_reason"] + tail
            c["exclusion_codes"] = "duplicate_merged"
        else:
            c["status"] = ent_status[ent["entity_id"]]
            c["exclusion_codes"] = "; ".join(dict.fromkeys(k for k, _ in ent["reasons"]))
            c["exclusion_reason"] = "; ".join(d for _, d in ent["reasons"])
        emp = c["employee_count_clean"]
        if c["status"] == STATUS_ELIGIBLE:
            if c["funding_stage_clean"] in ENTERPRISE_STAGES or (emp or 0) >= ENTERPRISE_EMPLOYEES:
                c["segment"] = "Enterprise"
            else:
                c["segment"] = "Mid-Market"
            if emp is None:
                c["flags"].append("employee_count_unknown")
                c["agent_notes"].append(
                    "Employee count blank; kept eligible, segment "
                    f"{c['segment']} ({'funding stage' if c['segment'] == 'Enterprise' else 'default'})"
                    ", size flagged unknown (D11).")
            if any(DUPLICATE_Q_NOTE.match(by_id[a]["notes_clean"]) for a in ent["members"]):
                if len(ent["members"]) > 1:
                    c["agent_notes"].append(
                        "'Duplicate?' note resolved: the duplicate was found and merged (no "
                        "score penalty, D15).")
                else:
                    c["flags"].append("duplicate_note_unresolved")
                    c["agent_notes"].append(
                        "'Duplicate?' note but no duplicate found in the data (small score "
                        "penalty, D15).")
        else:
            c["segment"] = ""
        m = AGENTS_NOTE.search(" ".join(ent["notes_combined"])) if c["is_primary"] else None
        if m and emp is not None and int(m.group("n")) > emp:
            c["flags"].append("employee_count_vs_notes_conflict")
            c["agent_notes"].append(
                f"Notes mention ~{m.group('n')} contact-center agents but employee_count is "
                f"{emp}; kept employee_count (agents may not be FTEs) (D12)"
                + (" - excluded as under 20 employees: even with many contact-center agents, the "
                   "company size does not meet our targeting criteria (owner decision D24)."
                   if emp < MIN_EMPLOYEES else "."))

    write_outputs(rows, by_id, entities, hierarchy, unresolved_targets)


# ---------------------------------------------------------------- output
AFTER_COLUMNS = [
    # (header, getter, guide text)
    ("account_id_clean", lambda c: c["account_id"], "Copy of account_id (unchanged)."),
    ("company_name_clean", lambda c: c["company_name_clean"], "Name with whitespace trimmed."),
    ("website_clean", lambda c: c["website_clean"],
     "Bare lowercase domain (no http/www/path). Profile pages keep their path."),
    ("country_clean", lambda c: c["country_clean"],
     "Derived from state/province when it is a US state or Canadian province."),
    ("city_clean", lambda c: c["city_clean"], "Trimmed city."),
    ("state_clean", lambda c: c["state_clean"],
     "Uppercased. Blank states filled from city only when the city maps to one state."),
    ("employee_count_clean", lambda c: c["employee_count_clean"],
     "Numeric. On a merged primary record, blanks are filled from its duplicates."),
    ("funding_stage_clean", lambda c: c["funding_stage_clean"], "Unchanged unless merged-filled."),
    ("last_funding_year_clean", lambda c: c["last_funding_year_clean"],
     "Numeric year. On a merged primary record, blanks are filled from its duplicates."),
    ("industry_clean", lambda c: c["industry_clean"], "Unchanged unless merged-filled."),
    ("existing_spend_usd_t12m_clean", lambda c: c["spend_clean"],
     "This row's own spend (blank = 0). See entity_total_spend for the company total."),
    ("notes_clean", lambda c: c["notes_clean"], "Notes text, unchanged."),
    ("website_type", lambda c: c["website_type"],
     "company_domain | subdomain (business-unit site) | social_profile (not a real domain)."),
    ("entity_id", lambda c: c["entity_id"],
     "One ID per real company. Rows sharing an entity_id are the same company."),
    ("is_primary_record", lambda c: "yes" if c["is_primary"] else "no",
     "The row that represents the company. Other rows of the entity are merged into it."),
    ("entity_total_spend", lambda c: c["_ent"]["total_spend"],
     "Sum of spend across every record of the same company."),
    ("parent_account_id", lambda c: c.get("parent_account_id", ""),
     "For business units: the parent company's account. Child routes to the parent's owner."),
    ("acquirer_account_id", lambda c: c.get("acquirer_account_id", ""),
     "For acquired companies: the acquirer's account."),
    ("region", lambda c: c["region"], "EAST / CENTRAL / WEST per rules.md appendix, else NOT_COVERED."),
    ("segment", lambda c: c["segment"],
     "Eligible rows only. Enterprise = 500+ employees or Public / Private Equity."),
    ("status", lambda c: c["status"], "eligible | excluded | merged_duplicate."),
    ("exclusion_codes", lambda c: c["exclusion_codes"], "Machine-readable reason codes."),
    ("exclusion_reason", lambda c: c["exclusion_reason"], "Plain-English reason for exclusion."),
    ("review_flags", lambda c: "; ".join(dict.fromkeys(c["flags"])),
     "Things a human should double-check (see review_flags sheet)."),
    # step 2 columns: blank until pipeline/step2_classify.py has run
    ("use_case", lambda c: c.get("uc", {}).get("use_case", ""),
     "Step 2: one use case per eligible company (see docs/step2_classification_proposal.md)."),
    ("use_case_evidence", lambda c: c.get("uc", {}).get("evidence", ""),
     "Step 2: the exact note / industry text the use case rests on (blank = no signal)."),
    ("use_case_confidence", lambda c: c.get("uc", {}).get("confidence", ""),
     "Step 2: high / medium / low."),
    ("use_case_rationale", lambda c: c.get("uc", {}).get("rationale", ""),
     "Step 2: one sentence a rep can read."),
    # step 3 columns: blank until pipeline/step3_route.py has run
    ("fit_score", lambda c: c.get("asg", {}).get("fit_score", ""),
     "Step 3: 0-100 fit score (docs/step3_scoring_proposal.md)."),
    ("score_breakdown", lambda c: c.get("asg", {}).get("score_breakdown", ""),
     "Step 3: how the fit score adds up."),
    ("assignment_status", lambda c: c.get("asg", {}).get("status", ""),
     "Step 3: assigned | left_over (rep's book full). Blank = not eligible."),
    ("assigned_rep", lambda c: c.get("asg", {}).get("assigned_rep", ""),
     "Step 3: the rep who now owns this account."),
    ("pool_rank", lambda c: (f"{c['asg']['pool_rank']} of {c['asg']['pool_size']}"
                             if c.get("asg") else ""),
     "Step 3: rank within the region + segment pool."),
    ("assignment_reason", lambda c: c.get("asg", {}).get("reason", ""),
     "Step 3: the reason a rep reads, built only from this account's data."),
    ("Agent Notes", lambda c: " ".join(dict.fromkeys(c["agent_notes"])),
     "Claude's short notes on every edit made to the after-columns and why."),
]

HEADER_AFTER = PatternFill("solid", fgColor="1F6F4A")
BODY_AFTER = PatternFill("solid", fgColor="E2F0D9")
HEADER_SHEET = PatternFill("solid", fgColor="305496")


def write_sheet(wb, title, header, data, widths=None):
    ws = wb.create_sheet(title)
    ws.append(header)
    for row in data:
        ws.append(row)
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = HEADER_SHEET
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    for i, w in enumerate(widths or [], start=1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w
    return ws


DEFAULT_WIDTHS = {"Agent Notes": 90, "exclusion_reason": 60, "notes_clean": 50, "review_flags": 35,
                  "assignment_reason": 90, "score_breakdown": 60, "use_case_rationale": 50,
                  "use_case_evidence": 50}
BANNER_ORIGINAL = "Original Data"      # owner-added banner row (2026-10-14), reproduced on fresh runs
BANNER_AFTER = "Agent-Worked Data"


def header_row_of(ws):
    for r in range(1, 6):
        if ws.cell(row=r, column=1).value == "account_id":
            return r
    raise ValueError("header row with 'account_id' not found in accounts sheet")


def load_template():
    """Use the current working workbook as the template so the owner's formatting (banner row,
    column widths, freeze panes, styles) survives a re-run. Its original columns must still equal
    the pristine backup, otherwise we refuse to write. Falls back to the backup on a fresh run."""
    raw_ws = openpyxl.load_workbook(RAW_ACCOUNTS)["accounts"]
    raw_vals = [[c.value for c in r] for r in raw_ws.iter_rows()]
    if not ACCOUNTS_XLSX.exists():
        return openpyxl.load_workbook(RAW_ACCOUNTS), {}
    wb = openpyxl.load_workbook(ACCOUNTS_XLSX)
    ws = wb["accounts"]
    hr = header_row_of(ws)
    n = len(ORIGINAL_COLUMNS)
    cur = [[ws.cell(row=hr + i, column=j + 1).value for j in range(n)] for i in range(len(raw_vals))]
    if cur != raw_vals or ws.max_row - hr + 1 != len(raw_vals):
        sys.exit("STOP: original columns A-L in accounts-XLSX.xlsx no longer match "
                 "backup_originals/. Nothing was written. Investigate before re-running.")
    widths = {}
    for col in range(n + 1, ws.max_column + 1):
        hdr = ws.cell(row=hr, column=col).value
        w = ws.column_dimensions[openpyxl.utils.get_column_letter(col)].width
        if hdr and w:
            widths[hdr] = w
    for rng in list(ws.merged_cells.ranges):
        if rng.max_col > n:
            ws.unmerge_cells(str(rng))
    ws.delete_cols(n + 1, ws.max_column - n)
    for name in wb.sheetnames:
        if name != "accounts":
            del wb[name]
    return wb, widths


def add_default_banner(ws):
    """Fresh run from the backup: reproduce the owner's banner row above the headers."""
    ws.insert_rows(1)
    ws.cell(row=1, column=1, value=BANNER_ORIGINAL)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(ORIGINAL_COLUMNS))
    for col in range(1, len(ORIGINAL_COLUMNS) + 1):
        ws.cell(row=1, column=col).fill = PatternFill("solid", fgColor="D6DCE4")
    a1 = ws.cell(row=1, column=1)
    a1.font = Font(bold=True, size=18)
    a1.alignment = Alignment(horizontal="center")
    ws.row_dimensions[1].height = 21
    ws.freeze_panes = "C3"


def write_outputs(rows, by_id, entities, hierarchy, unresolved_targets):
    for c in rows:
        c["_ent"] = entities[c["entity_id"]]
    uc_path = OUTPUT / "step2_use_cases.json"
    if uc_path.exists():
        for u in json.loads(uc_path.read_text(encoding="utf-8")):
            if u["account_id"] in by_id:
                by_id[u["account_id"]]["uc"] = u
    asg_path = OUTPUT / "step3_assignments.json"
    if asg_path.exists():
        for g in json.loads(asg_path.read_text(encoding="utf-8")):
            if g["account_id"] in by_id:
                by_id[g["account_id"]]["asg"] = g
    wb, widths = load_template()
    ws = wb["accounts"]
    if header_row_of(ws) == 1:
        add_default_banner(ws)
    hr = header_row_of(ws)
    assert ws.max_column == len(ORIGINAL_COLUMNS)
    start = len(ORIGINAL_COLUMNS) + 1
    last = start + len(AFTER_COLUMNS) - 1
    order = {c["account_id"]: c for c in rows}
    for j, (hdr, _, _) in enumerate(AFTER_COLUMNS):
        cell = ws.cell(row=hr, column=start + j, value=hdr)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = HEADER_AFTER
        letter = openpyxl.utils.get_column_letter(start + j)
        ws.column_dimensions[letter].width = widths.get(hdr, DEFAULT_WIDTHS.get(hdr, 18))
    if hr > 1:
        banner = ws.cell(row=hr - 1, column=start, value=BANNER_AFTER)
        banner.font = Font(bold=True, size=18, color="FFFFFF")
        banner.fill = HEADER_AFTER
        banner.alignment = Alignment(horizontal="center")
        ws.merge_cells(start_row=hr - 1, start_column=start, end_row=hr - 1, end_column=last)
    for i in range(hr + 1, ws.max_row + 1):
        c = order[ws.cell(row=i, column=1).value]
        for j, (_, get, _) in enumerate(AFTER_COLUMNS):
            cell = ws.cell(row=i, column=start + j, value=get(c))
            cell.fill = BODY_AFTER
    ws.auto_filter.ref = f"A{hr}:{openpyxl.utils.get_column_letter(last)}{ws.max_row}"

    # summary
    st = Counter(c["status"] for c in rows)
    prim = [c for c in rows if c["is_primary"]]
    code_counts = Counter(k for c in prim if c["status"] == STATUS_EXCLUDED
                          for k in c["exclusion_codes"].split("; "))
    primary_code = Counter(c["exclusion_codes"].split("; ")[0] for c in prim
                           if c["status"] == STATUS_EXCLUDED)
    elig = [c for c in rows if c["status"] == STATUS_ELIGIBLE]
    seg = Counter((c["region"], c["segment"]) for c in elig)
    summ = [
        ["Raw rows in accounts-XLSX.xlsx", len(rows)],
        ["Distinct companies (entities)", len(entities)],
        ["Rows merged into another record (duplicates)", st[STATUS_MERGED]],
        ["Companies excluded", st[STATUS_EXCLUDED]],
        ["Companies eligible for routing", st[STATUS_ELIGIBLE]],
        ["CHECK: eligible + excluded + merged = raw rows",
         "OK" if st[STATUS_ELIGIBLE] + st[STATUS_EXCLUDED] + st[STATUS_MERGED] == len(rows)
         else "MISMATCH"],
        [],
        ["Excluded companies by FIRST reason (each counted once)", ""],
        *[[f"  {k}", v] for k, v in primary_code.most_common()],
        ["Excluded companies by ANY reason (a company can have several)", ""],
        *[[f"  {k}", v] for k, v in code_counts.most_common()],
        [],
        ["Eligible companies by region / segment", ""],
        *[[f"  {r} / {s}", seg[(r, s)]] for r in ("EAST", "CENTRAL", "WEST")
          for s in ("Mid-Market", "Enterprise")],
    ]
    write_sheet(wb, "summary", ["metric", "value"], summ, [62, 14])

    excl = []
    for c in rows:
        if c["status"] == STATUS_ELIGIBLE:
            continue
        excl.append([c["account_id"], c["company_name_clean"], c["status"], c["exclusion_codes"],
                     c["exclusion_reason"], c["entity_id"]])
    write_sheet(wb, "exclusions", ["account_id", "company_name", "status", "reason_codes",
                                   "reason", "entity_id"], excl, [13, 30, 18, 34, 110, 12])

    ents = []
    for e in sorted(entities.values(), key=lambda e: e["entity_id"]):
        if len(e["members"]) < 2:
            continue
        p = by_id[e["primary"]]
        for a in e["members"]:
            c = by_id[a]
            ents.append([e["entity_id"], a, "primary" if a == e["primary"] else "merged",
                         c["company_name_clean"], c["raw"]["website"], c["city_clean"],
                         c["raw"]["employee_count"], c["spend_clean"], c["notes_clean"],
                         ent_status_of(p), e["total_spend"]])
    write_sheet(wb, "entities", ["entity_id", "account_id", "role", "company_name",
                                 "website_as_entered", "city", "employee_count_as_entered",
                                 "spend", "notes", "entity_status", "entity_total_spend"],
                ents, [12, 13, 9, 30, 36, 14, 12, 10, 60, 12, 12])

    hier = []
    for h in hierarchy:
        ch, pa = by_id[h["child_account_id"]], by_id[h["parent_account_id"]]
        hier.append([h["child_account_id"], ch["company_name_clean"], h["relationship"],
                     h["parent_account_id"], pa["company_name_clean"], ch["status"],
                     pa["status"], ch["region"], pa["region"]])
    write_sheet(wb, "hierarchy", ["child_account_id", "child_name", "relationship",
                                  "parent_account_id", "parent_name", "child_status",
                                  "parent_status", "child_region", "parent_region"],
                hier, [14, 26, 16, 16, 28, 12, 12, 12, 12])

    flag_rows = [[c["account_id"], c["company_name_clean"], c["status"], f,
                  " ".join(dict.fromkeys(c["agent_notes"]))]
                 for c in rows for f in dict.fromkeys(c["flags"])]
    for aid, kind, tgt, n in unresolved_targets:
        flag_rows.append([aid, by_id[aid]["company_name_clean"], by_id[aid]["status"],
                          "relationship_target_not_found", f"{kind} -> '{tgt}' ({n} matches)"])
    write_sheet(wb, "review_flags", ["account_id", "company_name", "status", "flag", "detail"],
                flag_rows, [13, 30, 16, 36, 110])

    cap_path = OUTPUT / "step3_capacity.json"
    if asg_path.exists() and cap_path.exists():
        cap = json.loads(cap_path.read_text(encoding="utf-8"))
        write_sheet(wb, "capacity", ["rep_id", "rep_name", "region", "segment",
                                     "current_book_size", "room (260 - current)",
                                     "eligible_in_pool", "assigned", "new_book_size", "left_over",
                                     "shortfall", "lowest_assigned_score"],
                    [[c["rep_id"], c["rep_name"], c["region"], c["segment"],
                      c["current_book_size"], c["room"], c["eligible_in_pool"], c["assigned"],
                      c["new_book_size"], c["left_over"], c["shortfall"],
                      c["lowest_assigned_score"]] for c in cap],
                    [8, 18, 10, 12, 12, 14, 12, 10, 12, 10, 10, 14])
        books = sorted((g for g in (c.get("asg") for c in rows) if g),
                       key=lambda g: (g["rep_id"], g["status"] != "assigned", g["pool_rank"]))
        write_sheet(wb, "rep_books", ["rep_id", "rep_name", "status", "pool_rank", "account_id",
                                      "company_name", "fit_score", "use_case", "reason"],
                    [[g["rep_id"], g["rep_name"], g["status"], g["pool_rank"], g["account_id"],
                      g["company_name"], g["fit_score"], g["use_case"], g["reason"]]
                     for g in books], [8, 18, 10, 9, 13, 28, 9, 20, 140])

    guide = [[c, "original (never edited)", "As exported from the CRM."] for c in ORIGINAL_COLUMNS]
    guide += [[h, "after (Claude)", g] for h, _, g in AFTER_COLUMNS]
    write_sheet(wb, "column_guide", ["column", "group", "meaning"], guide, [30, 24, 100])
    # neutral file metadata: never publish the editor's name (pre-publish review 2026-10-14)
    wb.properties.creator = wb.properties.lastModifiedBy = "Account Routing Service pipeline"
    wb.save(ACCOUNTS_XLSX)

    OUTPUT.mkdir(exist_ok=True)
    out = []
    for c in rows:
        e = c["_ent"]
        out.append({
            "account_id": c["account_id"], "company_name": c["company_name_clean"],
            "website": c["website_clean"], "website_type": c["website_type"],
            "country": c["country_clean"], "city": c["city_clean"], "state": c["state_clean"],
            "employee_count": c["employee_count_clean"], "funding_stage": c["funding_stage_clean"],
            "last_funding_year": c["last_funding_year_clean"], "industry": c["industry_clean"],
            "spend": c["spend_clean"], "notes": c["notes_clean"], "entity_id": c["entity_id"],
            "is_primary": c["is_primary"], "entity_members": e["members"],
            "entity_total_spend": e["total_spend"], "entity_notes": e["notes_combined"],
            "parent_account_id": c.get("parent_account_id"),
            "acquirer_account_id": c.get("acquirer_account_id"), "region": c["region"],
            "segment": c["segment"], "status": c["status"],
            "exclusion_codes": c["exclusion_codes"], "exclusion_reason": c["exclusion_reason"],
            "flags": list(dict.fromkeys(c["flags"])),
            "agent_notes": list(dict.fromkeys(c["agent_notes"])),
        })
    (OUTPUT / "step1_accounts.json").write_text(json.dumps(out, indent=1), encoding="utf-8")

    for line in summ:
        if line:
            print(*line, sep=": ")


def ent_status_of(p):
    return p["status"]


if __name__ == "__main__":
    main()
