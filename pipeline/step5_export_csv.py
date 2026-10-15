"""Export the approved final workbooks to CSV (owner request 2026-10-14, F1-F3).

  output/accounts_final.csv  one row per original CRM row: the 12 original columns, then every
                             agent-worked column (cleaned values, eligibility, use case, score,
                             assignment, reason, Agent Notes). The banner row is dropped.
  output/reps_final.csv      the reps with current_book_size and new_book_size.

Read straight from accounts-XLSX.xlsx / reps-XLSX.xlsx so the CSVs always match the workbooks.
The original accounts.csv / reps.csv are never touched (D1, F3). UTF-8 with BOM so Excel shows
characters such as "São Paulo" correctly.   Run: python pipeline/step5_export_csv.py
"""
import csv
import sys

import openpyxl

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from config import ACCOUNTS_XLSX, ORIGINAL_COLUMNS, OUTPUT, REPS_XLSX  # noqa: E402


def sheet_rows(path, sheet, first_header):
    ws = openpyxl.load_workbook(path, read_only=True, data_only=True)[sheet]
    rows = list(ws.iter_rows(values_only=True))
    start = next(i for i, r in enumerate(rows) if r and r[0] == first_header)  # skip banner row
    header = [h for h in rows[start] if h is not None]
    body = [list(r[:len(header)]) for r in rows[start + 1:] if r and r[0] is not None]
    return header, body


def write_csv(path, header, body):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows([["" if v is None else v for v in r] for r in body])


def main():
    OUTPUT.mkdir(exist_ok=True)
    h, b = sheet_rows(ACCOUNTS_XLSX, "accounts", "account_id")
    assert h[:len(ORIGINAL_COLUMNS)] == ORIGINAL_COLUMNS and len(b) == 2020, (h[:12], len(b))
    write_csv(OUTPUT / "accounts_final.csv", h, b)
    rh, rb = sheet_rows(REPS_XLSX, "reps", "rep_id")
    assert "new_book_size" in rh and len(rb) == 6, (rh, len(rb))
    write_csv(OUTPUT / "reps_final.csv", rh, rb)
    print(f"wrote output/accounts_final.csv ({len(b)} rows x {len(h)} columns) and "
          f"output/reps_final.csv ({len(rb)} rows x {len(rh)} columns)")


if __name__ == "__main__":
    main()
