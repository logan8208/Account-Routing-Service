"""Final compliance checks: tests the finished output directly against rules.md and the brief.
Run: python pipeline/verify_rules.py   (exits non-zero on any failure; run.py runs it last)"""
import csv
import json
import sys
from collections import Counter

import openpyxl

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from config import ORIGINAL_COLUMNS, OUTPUT, RAW_ACCOUNTS  # noqa: E402

s1 = {a["account_id"]: a for a in json.loads((OUTPUT / "step1_accounts.json").read_text("utf-8"))}
asg = json.loads((OUTPUT / "step3_assignments.json").read_text("utf-8"))
cap = json.loads((OUTPUT / "step3_capacity.json").read_text("utf-8"))
raw = {r[0]: dict(zip(ORIGINAL_COLUMNS, r)) for r in
       openpyxl.load_workbook(RAW_ACCOUNTS, read_only=True)["accounts"].iter_rows(min_row=2, values_only=True)}
fails = []


def check(name, ok):
    print(("PASS " if ok else "FAIL ") + name)
    if not ok:
        fails.append(name)


assigned = [g for g in asg if g["status"] == "assigned"]
ents = Counter(s1[g["account_id"]]["entity_id"] for g in assigned)
check("rules.md: one company, one account (no company in a book twice)", max(ents.values()) == 1)
check("rules.md: no company with spend on ANY of its records is in a book",
      all(sum(int(raw[m]["existing_spend_usd_t12m"] or 0) for m in s1[g["account_id"]]["entity_members"]) == 0
          for g in assigned))
check("rules.md: nobody under 20 employees in a book",
      all((s1[g["account_id"]]["employee_count"] or 20) >= 20 for g in assigned))
for st, reg in [("AZ", "CENTRAL"), ("MI", "EAST"), ("IN", "EAST"), ("KY", "CENTRAL"), ("TN", "CENTRAL"),
                ("BC", "WEST"), ("ON", "EAST"), ("QC", "EAST"), ("AB", "CENTRAL"), ("HI", "WEST")]:
    rows = [a for a in s1.values() if a["state"] == st]
    check(f"rules.md: {st} -> {reg} ({len(rows)} rows{'; none in data' if not rows else ''})",
          all(a["region"] == reg for a in rows))
check("rules.md: region from state/province, not the country column (blank-country rows still routed)",
      any(a["region"] != "NOT_COVERED" and raw[a["account_id"]]["country"] in (None, "") for a in s1.values()))
check("rules.md: Enterprise = 500+ employees or Public / Private Equity (all non-business-unit accounts)",
      all((s1[g["account_id"]]["segment"] == "Enterprise") ==
          ((s1[g["account_id"]]["employee_count"] or 0) >= 500 or
           s1[g["account_id"]]["funding_stage"] in ("Public", "Private Equity"))
          for g in asg if not g["parent_account_id"]))
check("rules.md: every book at most 260", all(c["new_book_size"] <= 260 for c in cap))
check("rules.md: left-overs and shortfall reported for every rep",
      all(c["left_over"] == c["eligible_in_pool"] - c["assigned"] and c["shortfall"] == c["room"] - c["assigned"]
          for c in cap))
check("brief: every eligible account has a reason; every excluded/merged row has a reason",
      all(g["reason"] for g in asg) and all(a["exclusion_reason"] for a in s1.values() if a["status"] != "eligible"))
rows = list(csv.reader(open(OUTPUT / "accounts_final.csv", encoding="utf-8-sig")))
check("brief: final CSV has all 2,020 rows with the 12 original columns first",
      len(rows) == len(raw) + 1 and rows[0][:12] == ORIGINAL_COLUMNS)

print(f"\n{len(fails)} failed check(s)")
sys.exit(1 if fails else 0)
