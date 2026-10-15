"""Step 3 - fit score, rep assignment, and a rep-readable reason for every eligible company.

Weights and routing rules: docs/step3_scoring_proposal.md (approved 2026-10-14, D31-D34).
Reads output/step1_accounts.json + output/step2_use_cases.json + backup_originals/reps-XLSX.xlsx.
Writes output/step3_assignments.json and output/step3_capacity.json, adds new_book_size to
reps-XLSX.xlsx (owner formatting preserved), then rebuilds accounts-XLSX.xlsx.

Run:  python pipeline/step3_route.py
"""
import json
import re
import sys
from collections import defaultdict

import openpyxl
from openpyxl.styles import Font

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from config import OUTPUT, RAW_REPS, REPS_XLSX  # noqa: E402

TARGET_BOOK = 260  # rules.md
WIN_INDUSTRIES = {"Healthcare", "Contact Center Software", "Conversation Intelligence",
                  "Telephony / CPaaS", "EdTech", "Media & Entertainment", "Legal Tech",
                  "Insurance", "Sales Tech"}
INTENT_NOTE = re.compile(r"^(Inbound demo request in 202[56]|Evaluating several vendors)")
CONF_RANK = {"high": 3, "medium": 2, "low": 1}


def score(acc, uc):
    """Return (total, parts) where parts lists (label, points) - the breakdown shown to reps."""
    parts = []
    if uc["evidence_source"] == "notes" and uc["use_case"] != "none":
        parts.append(("speech use case in notes", 35))
    elif uc["evidence_source"] == "notes+industry":
        parts.append(("speech interest in notes", 20))
    if any(INTENT_NOTE.match(n) for n in acc["entity_notes"]):
        parts.append(("buying intent", 5))  # D31
    parts.append(("win-list industry", 25) if acc["industry"] in WIN_INDUSTRIES
                 else ("other industry", 5))
    e = acc["employee_count"]
    if e is None:
        parts.append(("size unknown", 4))
    elif e < 50:
        parts.append(("20-49 employees", 6))
    elif e < 200:
        parts.append(("50-199 employees", 12))
    elif e <= 10000:
        parts.append(("200-10,000 employees", 20))
    else:
        parts.append(("over 10,000 employees", 8))
    y = acc["last_funding_year"]
    if y and y >= 2025:
        parts.append(("funded 2025-26", 15))
    elif y == 2024:
        parts.append(("funded 2024", 8))
    if "duplicate_note_unresolved" in acc["flags"]:
        parts.append(("unresolved 'Duplicate?' note", -5))
    return sum(p for _, p in parts), parts


def tie_key(acc, uc, total):
    """Sort key: score, then the approved tie-break (D32). Over 10,000 employees ranks below any
    company of 10,000 or fewer ("bigger is better, up to a point")."""
    e = acc["employee_count"]
    size = -1 if e is None else (0 if e > 10000 else e)
    return (-total, -CONF_RANK[uc["confidence"]], -size, -(acc["last_funding_year"] or 0),
            acc["account_id"])


def load_reps():
    ws = openpyxl.load_workbook(RAW_REPS, read_only=True)["reps"]
    rows = list(ws.iter_rows(values_only=True))
    hdr = rows[0][:5]
    return [dict(zip(hdr, r[:5])) for r in rows[1:] if r[0]]


def fmt_emp(e):
    return "employee count unknown" if e is None else f"{e:,} employees"


def build_reason(acc, uc, total, rank, pool_n, region, segment, status, rep, cutoff,
                 ranking_score, parent=None):
    """1-4 sentences built only from this account's own fields (verified by verify_step3.py)."""
    s = []
    if parent:
        s.append(f"Business unit of {parent['company_name']} ({parent['account_id']}); it goes "
                 f"with its parent and is ranked on the parent's score of {ranking_score}.")
    if uc["evidence_source"] == "notes" and uc["use_case"] != "none":
        s.append(f"Notes: \"{uc['evidence']}\"")
    elif uc["evidence_source"] == "notes+industry":
        note = uc["evidence"].split(" | ")[0]
        s.append(f"Notes: \"{note}\" (speech interest; use case {uc['use_case']} inferred from "
                 f"industry).")
    else:
        shown = [n for n in acc["entity_notes"] if not n.startswith("Business unit of")]
        s.append("No speech need in the notes yet" +
                 (f" (notes: \"{shown[0]}\")." if shown else "; no notes on file."))
    intent = [n for n in acc["entity_notes"] if INTENT_NOTE.match(n)]
    if intent and uc["evidence"] != intent[0] and intent[0] not in s[-1]:
        s.append(f"Buying intent: \"{intent[0]}\"")
    ind = acc["industry"] + (" (a win-list industry)" if acc["industry"] in WIN_INDUSTRIES else "")
    stage = acc["funding_stage"]
    fund = ("funding stage unknown" if stage == "Unknown" else stage) + (
        f" {acc['last_funding_year']}" if acc["last_funding_year"] else "")
    s.append(f"{ind}, {fmt_emp(acc['employee_count'])}, {fund}.")
    score_txt = f"Fit score {total}/100, #{rank} of {pool_n} in {region} {segment}"
    if status == "assigned":
        s.append(score_txt + ".")
    elif ranking_score == cutoff:
        s.append(score_txt + f"; not assigned: tied with the lowest assigned score ({cutoff}) in "
                 f"{rep}'s book but lost the tie-break (use-case confidence, then size, then "
                 f"funding year), and the book is full.")
    else:
        s.append(score_txt + f"; not assigned because {rep}'s book is full "
                 f"(lowest assigned score {cutoff}).")
    return " ".join(s)


def main():
    accounts = json.loads((OUTPUT / "step1_accounts.json").read_text(encoding="utf-8"))
    by_id = {a["account_id"]: a for a in accounts}
    ucs = {u["account_id"]: u for u in json.loads(
        (OUTPUT / "step2_use_cases.json").read_text(encoding="utf-8"))}
    reps = load_reps()
    rep_of = {(r["region"], r["segment"]): r for r in reps}

    scored = {}
    for aid, uc in ucs.items():
        total, parts = score(by_id[aid], uc)
        scored[aid] = (total, parts)

    # units: an eligible parent plus its eligible business units (D25); everyone else alone
    children = defaultdict(list)
    for aid in ucs:
        p = by_id[aid]["parent_account_id"]
        if p and p in ucs:
            children[p].append(aid)
    pools = defaultdict(list)
    for aid in ucs:
        acc = by_id[aid]
        if acc["parent_account_id"] in ucs:
            continue  # rides with its parent
        unit = [aid] + sorted(children.get(aid, []))
        pools[(acc["region"], acc["segment"])].append(unit)

    out, capacity = {}, []
    for rep in reps:
        key = (rep["region"], rep["segment"])
        room = TARGET_BOOK - int(rep["current_book_size"])
        units = sorted(pools.get(key, []),
                       key=lambda u: tie_key(by_id[u[0]], ucs[u[0]], scored[u[0]][0]))
        pool_n = sum(len(u) for u in units)
        left, rank, skipped_pairs = room, 0, []
        decisions = []
        for unit in units:
            if len(unit) <= left:
                status = "assigned"
                left -= len(unit)
            else:
                status = "left_over"
                if len(unit) > 1 and left > 0:
                    skipped_pairs.append(unit[0])  # D33: pair skipped, slot goes to next account
            for aid in unit:
                rank += 1
                decisions.append((aid, unit[0], status, rank))
        assigned_scores = [scored[h][0] for _, h, st, _ in decisions if st == "assigned"]
        cutoff = min(assigned_scores) if assigned_scores else None
        for aid, head, status, rk in decisions:
            acc, uc = by_id[aid], ucs[aid]
            total, parts = scored[aid]
            parent = by_id[head] if head != aid else None
            out[aid] = {
                "account_id": aid, "company_name": acc["company_name"],
                "region": key[0], "segment": key[1], "rep_id": rep["rep_id"],
                "rep_name": rep["rep_name"], "status": status,
                "assigned_rep": rep["rep_name"] if status == "assigned" else "",
                "fit_score": total, "ranking_score": scored[head][0],
                "score_breakdown": " + ".join(f"{n} {p}" for n, p in parts) + f" = {total}",
                "pool_rank": rk, "pool_size": pool_n, "parent_account_id": parent and head,
                "use_case": uc["use_case"],
                "reason": build_reason(acc, uc, total, rk, pool_n, key[0], key[1], status,
                                       rep["rep_name"], cutoff, scored[head][0], parent),
            }
        assigned = sum(1 for _, _, st, _ in decisions if st == "assigned")
        capacity.append({
            "rep_id": rep["rep_id"], "rep_name": rep["rep_name"], "region": key[0],
            "segment": key[1], "current_book_size": int(rep["current_book_size"]),
            "room": room, "eligible_in_pool": pool_n, "assigned": assigned,
            "new_book_size": int(rep["current_book_size"]) + assigned,
            "left_over": pool_n - assigned, "shortfall": room - assigned,
            "lowest_assigned_score": cutoff, "pairs_skipped_for_space": skipped_pairs,
        })
    assert set(out) == set(ucs), "every eligible company must get a decision"
    (OUTPUT / "step3_assignments.json").write_text(json.dumps(list(out.values()), indent=1),
                                                   encoding="utf-8")
    (OUTPUT / "step3_capacity.json").write_text(json.dumps(capacity, indent=1), encoding="utf-8")
    write_reps(capacity)
    for c in capacity:
        print(f"{c['rep_id']} {c['rep_name']:16s} {c['region']:7s} {c['segment']:10s} room "
              f"{c['room']:3d} pool {c['eligible_in_pool']:3d} assigned {c['assigned']:3d} "
              f"new book {c['new_book_size']} left over {c['left_over']:3d} shortfall "
              f"{c['shortfall']:3d} cut-off {c['lowest_assigned_score']} "
              f"pairs skipped {c['pairs_skipped_for_space']}")

    import step1_clean  # rebuild the accounts workbook with the step 3 columns + sheets
    step1_clean.main()


def write_reps(capacity):
    """Add new_book_size next to the untouched columns. Uses the working file as the template so
    any owner formatting survives; refuses to write if A-E no longer match the backup."""
    raw = [list(r[:5]) for r in openpyxl.load_workbook(RAW_REPS)["reps"].iter_rows(values_only=True)]
    wb = openpyxl.load_workbook(REPS_XLSX)
    ws = wb["reps"]
    hr = next(r for r in range(1, 6) if ws.cell(row=r, column=1).value == "rep_id")
    cur = [[ws.cell(row=hr + i, column=j + 1).value for j in range(5)] for i in range(len(raw))]
    if cur != raw:
        sys.exit("STOP: reps-XLSX.xlsx columns A-E no longer match backup_originals/.")
    col = next((c for c in range(6, ws.max_column + 2)
                if ws.cell(row=hr, column=c).value in (None, "new_book_size")), 6)
    hdr = ws.cell(row=hr, column=col, value="new_book_size")
    hdr.font = Font(bold=True)
    new = {c["rep_id"]: c["new_book_size"] for c in capacity}
    for r in range(hr + 1, hr + len(raw)):
        rid = ws.cell(row=r, column=1).value
        if rid in new:
            ws.cell(row=r, column=col, value=new[rid])
    ws.column_dimensions[openpyxl.utils.get_column_letter(col)].width = 16
    if ws.auto_filter.ref:
        ws.auto_filter.ref = f"A{hr}:{openpyxl.utils.get_column_letter(max(col, 5))}{hr + len(raw) - 1}"
    # neutral file metadata: never publish the editor's name (pre-publish review 2026-10-14)
    wb.properties.creator = wb.properties.lastModifiedBy = "Account Routing Service pipeline"
    wb.save(REPS_XLSX)


if __name__ == "__main__":
    main()
