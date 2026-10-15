"""Independent checks on step 3. Re-derives scores and facts from the RAW backup workbook with
separate code, and audits every reason sentence against that account's own data.
Run: python pipeline/verify_step3.py   (exits non-zero on any failure)"""
import json
import re
import sys
from collections import Counter, defaultdict

import openpyxl

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from config import ORIGINAL_COLUMNS, OUTPUT, RAW_ACCOUNTS, RAW_REPS, REPS_XLSX  # noqa: E402

fails = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f"  -> {detail}" if detail and not ok else ""))
    if not ok:
        fails.append(name)


raw = {r[0]: dict(zip(ORIGINAL_COLUMNS, r)) for r in
       openpyxl.load_workbook(RAW_ACCOUNTS, read_only=True)["accounts"].iter_rows(min_row=2, values_only=True)}
s1 = {a["account_id"]: a for a in json.loads((OUTPUT / "step1_accounts.json").read_text("utf-8"))}
uc = {u["account_id"]: u for u in json.loads((OUTPUT / "step2_use_cases.json").read_text("utf-8"))}
asg = {g["account_id"]: g for g in json.loads((OUTPUT / "step3_assignments.json").read_text("utf-8"))}
cap = json.loads((OUTPUT / "step3_capacity.json").read_text("utf-8"))
reps = [r for r in openpyxl.load_workbook(RAW_REPS, read_only=True)["reps"].iter_rows(min_row=2, values_only=True) if r[0]]

# 1. coverage
check("every eligible company has exactly one decision", set(asg) == {a for a, x in s1.items() if x["status"] == "eligible"})
check("no excluded/merged company is assigned", all(s1[a]["status"] == "eligible" for a in asg))

# 2. score recomputed from raw values of the entity (separate implementation)
WIN = {"Healthcare", "Contact Center Software", "Conversation Intelligence", "Telephony / CPaaS",
       "EdTech", "Media & Entertainment", "Legal Tech", "Insurance", "Sales Tech"}
bad = []
for a, g in asg.items():
    x, u = s1[a], uc[a]
    pts = {"notes": 35, "notes+industry": 20}.get(u["evidence_source"], 0) if u["use_case"] != "none" else 0
    notes = " ".join(str(raw[m]["notes"] or "") for m in x["entity_members"])
    pts += 5 if re.search(r"Inbound demo request in 202[56]|Evaluating several vendors", notes) else 0
    pts += 25 if x["industry"] in WIN else 5
    emps = [raw[m]["employee_count"] for m in x["entity_members"] if raw[m]["employee_count"] not in (None, "")]
    e = int(raw[a]["employee_count"]) if raw[a]["employee_count"] not in (None, "") else (int(emps[0]) if emps else None)
    pts += 4 if e is None else 6 if e < 50 else 12 if e < 200 else 20 if e <= 10000 else 8
    yrs = [raw[m]["last_funding_year"] for m in x["entity_members"] if raw[m]["last_funding_year"] not in (None, "")]
    y = int(raw[a]["last_funding_year"]) if raw[a]["last_funding_year"] not in (None, "") else (int(yrs[0]) if yrs else None)
    pts += 15 if y and y >= 2025 else 8 if y == 2024 else 0
    if pts != g["fit_score"]:
        bad.append((a, pts, g["fit_score"]))
check("fit score recomputed from raw data matches for every company", not bad, str(bad[:5]))

# 3. routing rules
rep_by = {r[0]: r for r in reps}
check("assigned only within the rep's region",
      all(g["region"] == rep_by[g["rep_id"]][2] == s1[g["account_id"]]["region"] for g in asg.values()))
check("segment matches the rep (business units take the parent's segment)",
      all(g["segment"] == rep_by[g["rep_id"]][3] and
          (s1[g["account_id"]]["segment"] == g["segment"] or g["parent_account_id"])
          for g in asg.values()))
for c in cap:
    n = sum(1 for g in asg.values() if g["rep_id"] == c["rep_id"] and g["status"] == "assigned")
    room = 260 - int(rep_by[c["rep_id"]][4])
    check(f"{c['rep_id']}: assigned {n} <= room {room}; full if anything is left over",
          n <= room and (n == room or c["left_over"] == 0) and n == c["assigned"])
check("rules.md: no rep filled from another region (shortfall reported, not filled)",
      all(c["shortfall"] == c["room"] - c["assigned"] >= 0 for c in cap))
# higher ranking score never left over while a lower one in the same pool is assigned
inv = []
pool = defaultdict(list)
for g in asg.values():
    pool[g["rep_id"]].append(g)
for rid, gs in pool.items():
    lo_assigned = min((g["ranking_score"] for g in gs if g["status"] == "assigned"), default=None)
    hi_left = max((g["ranking_score"] for g in gs if g["status"] == "left_over"), default=None)
    if lo_assigned is not None and hi_left is not None and hi_left > lo_assigned:
        inv.append((rid, hi_left, lo_assigned))
check("no left-over company outranks an assigned one (score order respected)", not inv, str(inv))
pairs = [(a, g) for a, g in asg.items() if g["parent_account_id"]]
check(f"business units move with their parent ({len(pairs)})",
      all(asg[g["parent_account_id"]]["status"] == g["status"] and
          asg[g["parent_account_id"]]["rep_id"] == g["rep_id"] for _, g in pairs))

# 4. reasons are grounded in the account's own data
ungrounded = []
for a, g in asg.items():
    x, r = s1[a], g["reason"]
    allowed_quotes = set(x["entity_notes"])
    for q in re.findall(r'"([^"]+)"', r):
        if q not in allowed_quotes:
            ungrounded.append((a, "quote", q))
    allowed_nums = {str(g["fit_score"]), str(g["ranking_score"]), str(g["pool_rank"]), str(g["pool_size"]), "100"}
    if x["employee_count"] is not None:
        allowed_nums.add(f"{x['employee_count']:,}")
    if x["last_funding_year"]:
        allowed_nums.add(str(x["last_funding_year"]))
    c = next(c for c in cap if c["rep_id"] == g["rep_id"])
    allowed_nums.add(str(c["lowest_assigned_score"]))
    if g["parent_account_id"]:
        allowed_nums.add(g["parent_account_id"].split("-")[1])
    stripped = re.sub(r'"[^"]+"', "", r)  # numbers inside verified quotes are fine
    for num in re.findall(r"\d{1,3}(?:,\d{3})+|\d+", stripped):  # "1,220" or "100", no trailing comma
        if num not in allowed_nums:
            ungrounded.append((a, "number", num))
    if x["industry"] not in r:
        ungrounded.append((a, "industry missing", x["industry"]))
    if g["parent_account_id"] and g["ranking_score"] != asg[g["parent_account_id"]]["fit_score"]:
        ungrounded.append((a, "parent score", g["ranking_score"]))
    if ", Unknown." in r:
        ungrounded.append((a, "bare Unknown", ""))
    if g["status"] == "left_over" and "not assigned" not in r:
        ungrounded.append((a, "left_over reason", ""))
check(f"every reason is grounded: quotes, numbers, industry ({len(asg)} reasons)",
      not ungrounded, str(ungrounded[:5]))
check("no two reasons are identical boilerplate", max(Counter(g["reason"] for g in asg.values()).values()) == 1,
      str(Counter(g["reason"] for g in asg.values()).most_common(1)))

# 5. reps workbook
ws = openpyxl.load_workbook(REPS_XLSX, read_only=True)["reps"]
rows = list(ws.iter_rows(values_only=True))
hdr = list(rows[0])
check("reps-XLSX: current_book_size untouched, new_book_size added",
      [list(r[:5]) for r in rows[1:7]] == [list(r[:5]) for r in reps] and "new_book_size" in hdr
      and all(r[hdr.index("new_book_size")] == r[4] + next(c["assigned"] for c in cap if c["rep_id"] == r[0])
              for r in rows[1:7]))

print(f"\n{len(fails)} failed check(s)")
sys.exit(1 if fails else 0)
