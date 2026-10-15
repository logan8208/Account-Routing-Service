"""Independent checks on step 1 output. Re-derives facts from the raw backup with separate,
simpler code, so a bug in step1_clean.py is not repeated here.  Run: python pipeline/verify_step1.py
Exits non-zero if any check fails."""
import json
import re
import sys
from collections import Counter

import openpyxl

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from config import ACCOUNTS_XLSX, ORIGINAL_COLUMNS, OUTPUT, RAW_ACCOUNTS, REGION_BY_STATE  # noqa

fails = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f"  -> {detail}" if detail and not ok else ""))
    if not ok:
        fails.append(name)


raw_ws = openpyxl.load_workbook(RAW_ACCOUNTS, read_only=True)["accounts"]
new_wb = openpyxl.load_workbook(ACCOUNTS_XLSX, read_only=True)
new_ws = new_wb["accounts"]
raw_rows = [list(r) for r in raw_ws.iter_rows(values_only=True)]
new_rows = [list(r) for r in new_ws.iter_rows(values_only=True)]
# the owner added a banner row above the headers; locate the real header row
new_rows = new_rows[next(i for i, r in enumerate(new_rows) if r[0] == "account_id"):]

# 1. original columns are byte-for-byte unchanged
n = len(ORIGINAL_COLUMNS)
diff = [i for i, (a, b) in enumerate(zip(raw_rows, new_rows)) if a[:n] != b[:n]]
check("original 12 columns unchanged in every row", len(raw_rows) == len(new_rows) and not diff,
      f"{len(diff)} rows differ")

data = json.loads((OUTPUT / "step1_accounts.json").read_text(encoding="utf-8"))
by_id = {d["account_id"]: d for d in data}
raw = {r[0]: dict(zip(ORIGINAL_COLUMNS, r)) for r in raw_rows[1:]}
check("every raw row appears exactly once in output", sorted(by_id) == sorted(raw))

st = Counter(d["status"] for d in data)
check("eligible + excluded + merged == raw rows", sum(st.values()) == len(raw), str(st))

check("every non-eligible row has a written reason",
      all(d["exclusion_reason"].strip() for d in data if d["status"] != "eligible"))

# 2. eligible rows obey every eligibility rule (re-derived from raw values)
bad = []
for d in data:
    if d["status"] != "eligible":
        continue
    members = d["entity_members"]
    spend = sum(int(raw[m]["existing_spend_usd_t12m"] or 0) for m in members)
    notes = " ".join(str(raw[m]["notes"] or "") for m in members)
    emp = raw[d["account_id"]]["employee_count"]
    if spend > 0:
        bad.append((d["account_id"], "has spend"))
    if emp not in (None, "") and int(emp) < 20:
        bad.append((d["account_id"], "under 20"))
    if re.search(r"shut down|parked|Acquired by|speech recognition API|ASR engine|Speech-to-text vendor",
                 notes):
        bad.append((d["account_id"], "defunct/competitor note"))
    if d["state"] not in REGION_BY_STATE:
        bad.append((d["account_id"], "state not covered"))
check("no eligible company has spend / <20 emp / defunct / competitor / bad state",
      not bad, str(bad[:5]))

# 3. exactly one primary per entity; merged rows point at an eligible-or-excluded primary
ents = Counter(d["entity_id"] for d in data if d["is_primary"])
check("exactly one primary record per entity", all(v == 1 for v in ents.values())
      and set(ents) == {d["entity_id"] for d in data})
check("merged rows are never primary",
      all(not d["is_primary"] for d in data if d["status"] == "merged_duplicate"))

# 4. duplicate-domain pairs found by a naive method are all merged (except profile sites)
def host(w):
    return re.sub(r"^www\.", "", re.sub(r"^https?://", "", str(w).lower()).split("/")[0])
hosts = Counter(host(r["website"]) for r in raw.values())
missed = [h for h, k in hosts.items() if k > 1 and h not in ("linkedin.com", "twitter.com")
          and len({by_id[a]["entity_id"] for a in raw if host(raw[a]["website"]) == h}) > 1]
check("every shared real domain collapsed to one entity", not missed, str(missed))
prof = [a for a in raw if host(raw[a]["website"]) in ("linkedin.com", "twitter.com")]
check("profile-page sites (linkedin/twitter) NOT merged with each other",
      len({by_id[a]["entity_id"] for a in prof}) == len(prof))

# 5. every relationship note was acted on
for pat, field in [(r"^Business unit of", "parent_account_id"), (r"^Acquired by", "acquirer_account_id")]:
    rows = [a for a in raw if re.match(pat, str(raw[a]["notes"] or ""))]
    check(f"all '{pat[1:]}' notes linked ({len(rows)})", all(by_id[a][field] for a in rows))
same = [a for a in raw if re.match(r"^(Billing domain for|Self-serve signup|Product brand of)",
                                    str(raw[a]["notes"] or ""))]
check(f"all same-company notes merged ({len(same)})",
      all(by_id[a]["status"] == "merged_duplicate" for a in same))

# 6. regions follow the appendix
check("region matches appendix for every covered state",
      all(d["region"] == REGION_BY_STATE.get(d["state"], "NOT_COVERED") for d in data))
check("KA (Karnataka) never routed", all(d["region"] == "NOT_COVERED" for d in data if d["state"] == "KA"))

# 7. segment rule
segbad = [d["account_id"] for d in data if d["status"] == "eligible" and
          (d["segment"] == "Enterprise") != (d["funding_stage"] in ("Public", "Private Equity")
                                             or (d["employee_count"] or 0) >= 500)]
check("segment rule holds for every eligible company", not segbad, str(segbad[:5]))

# 8. sheets present
check("workbook has all sheets", set(new_wb.sheetnames) >= {
    "accounts", "summary", "exclusions", "entities", "hierarchy", "review_flags", "column_guide"},
    str(new_wb.sheetnames))
check("profile-page websites carry the 'update via enrichment' agent note (D22)",
      all(any("enrichment" in n for n in d["agent_notes"]) for d in data
          if d["website_type"] == "social_profile"))

moj = [d["account_id"] for d in data
       if any(re.search("[ÃÂ][\u0080-¿]", str(d[k] or "")) for k in ("company_name", "city", "notes"))]
check("no encoding damage (e.g. 'SÃ£o Paulo') left in cleaned text", not moj, str(moj[:5]))

print(f"\n{len(fails)} failed check(s)")
sys.exit(1 if fails else 0)
