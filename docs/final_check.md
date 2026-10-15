# Final check against the instructions

Checked 2026-10-14 against `Initial Prompt to Claude.md` (the brief), `rules.md`, `CLAUDE.md` and
every decision Logan made in conversation (`LOG.md` § Decisions).

**Automated:** `python run.py` runs 54 checks: step 1 (18), step 3 (17) and the final rules check
(19, `pipeline/verify_rules.py`). The step 2 schema and evidence check covers all 1,452 labels, and
the privacy scan reports 0 findings. All pass.

## The brief

| Instruction | Where it is met | Status |
|---|---|---|
| CLAUDE.md first, so any engineer can understand the build | `CLAUDE.md` | ✅ |
| Log from the start, grouped by category | `LOG.md` | ✅ |
| Logan tests and approves each step before the next | Approvals recorded in `LOG.md` for every step | ✅ |
| Normalize domains, find duplicates and related records, flag what can't be resolved | Step 1; `entities`, `hierarchy`, `review_flags` sheets | ✅ |
| Nothing dropped silently; exclusions show the reason in the web UI | "Excluded & merged" tab (568 rows, each with a reason) | ✅ |
| Give a view on rules vs. LLM for relationships hidden in notes | Rules on the templated notes, plus Claude reading all 85 distinct notes (approved by Logan) | ✅ |
| Duplicate the original columns before editing; never edit the originals | Columns A–L checked cell by cell against the backup on every run | ✅ |
| Use case: structured schema approved before the run | `pipeline/use_case_schema.json`, `docs/step2_classification_proposal.md` | ✅ |
| Hand-check a sample: error rate, sample size, cost | 150 sampled, 0 errors (95% CI 0–2.5%), $2.37; `output/step2_handcheck_report.md` | ✅ |
| Score, route, respect capacity, write a grounded reason for each account | Step 3; every reason's quotes and numbers checked against the account's own data | ✅ |
| Weight the fit signals and say why | `docs/step3_scoring_proposal.md` | ✅ |
| Small web UI of each rep's book with reasons, run locally, not deployed | `web_ui/rep_books.html` (offline single file; no GitHub Pages) | ✅ |
| README: how to run, clarifications, Logan's improvements, paragraph for the manager | `README.md` | ✅ |
| Deliverables: repo, code, README, log, cleaned accounts, exclusions, use cases, assignments | GitHub repo; workbook sheets; `output/accounts_final.csv` | ✅ |
| CSV only once Logan approves the final workbook | Done after approval (D38) | ✅ |
| No web lookups or outside enrichment | None used | ✅ |

## rules.md

| Rule | Check | Status |
|---|---|---|
| Customers (any spend) are off limits | No company with spend on any of its records is in a book | ✅ |
| Under 20 employees: skip | Nobody under 20 in a book | ✅ |
| Speech-engine competitors: skip | 7 excluded | ✅ |
| Companies that no longer exist: skip | 22 excluded | ✅ |
| One company, one account | No company in a book twice | ✅ |
| Enterprise = 500+ employees or Public / PE | Holds for every account | ✅ |
| Region from city and state, not the country column | Country never used; state/province appendix applied | ✅ |
| AZ → Central; MI, IN → East; KY, TN → Central | Checked (KY has no rows in the data) | ✅ |
| Target book 260 including current; highest scores first | Five books at 260, Sam at 225 | ✅ |
| Report left-overs | 507 reported, per rep | ✅ |
| Don't fill from another region; report the shortfall | Sam: 35 short, not filled (D35) | ✅ |
| "Duplicate?" / "not qualified" notes count against | "Duplicate?" penalty applies only if no duplicate was found (0 cases); "not *yet* qualified" is neutral (D15) | ✅ |

## Open items (not failures)

- The use-case labels haven't been compared with the team's ground truth yet. The policy calls most
  likely to differ are listed in `output/step2_handcheck_report.md`.
- 85 use-case labels are flagged for review.
- 127 accounts carry review flags (shown in the "Needs review" tab).
