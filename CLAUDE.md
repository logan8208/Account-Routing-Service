# CLAUDE.md — Account Sorting & Routing Project

This file is the standing memory for Claude Code on this project, and the place any engineer can
read to understand how the output was built. Keep it current: every new instruction or decision
from the project owner goes here (short form), and every build decision goes in "How the output
is built".

## Project in one paragraph

Six account executives (reps) share ~2,000 messy CRM accounts. The project ingests and cleans the
accounts, removes ineligible ones (with reasons), merges duplicates/related records, classifies each
eligible account's use case, scores and routes accounts to reps per `rules.md`, and exposes each
rep's book (with readable, data-grounded reasons) in a small locally-run web UI. Deliverables ship in
a GitHub repo with a README and the project log.

## Source files (inputs — never edit the original columns)

| File | Role |
|---|---|
| `Initial Prompt to Claude.md` | The project brief / instructions from the owner. |
| `rules.md` | Routing spec from the sales manager. Treated as the spec. |
| `accounts-XLSX.xlsx` | ~2,020 raw CRM accounts. The **only** account source we work from. |
| `reps-XLSX.xlsx` | The 6 reps: region, segment, current book size. The **only** rep source. |
| `accounts.csv`, `reps.csv` | Not inputs. Keep unedited; owner may later ask for the same edits (D1). |
| `backup_originals/` | Pristine copies of all four input files. The pipeline reads ONLY from here. |

## Standing instructions from the owner (always follow)

1. **Approval gate:** before each step/action, the owner must have tested and approved the previous
   step — until the owner says this is no longer necessary.
2. **Ask, don't guess:** where `rules.md` is silent or unclear, make a proposed call, write it down,
   and ask the owner to confirm. Record the answer in `LOG.md` and the README.
3. **Follow `rules.md`** at every step.
4. **Traceability in the accounts workbook:** before changing anything in `accounts-XLSX.xlsx`,
   duplicate the existing columns; never edit the original columns. Cleaned values go in new
   columns so before/after is visible side by side.
5. **Nothing silently dropped.** Every excluded row carries an explicit reason, shown in the web UI.
6. **No web lookups / enrichment.** All companies are fictional. Work only from the two XLSX files.
7. **Use-case classification:** propose the structured output schema + methodology and get approval
   BEFORE running it. Afterwards hand-check a sample and report error rate, sample size, and cost.
8. **Reasons must be grounded** in that account's actual data (a rep will notice if not).
9. **Logging:** keep `LOG.md` from the very beginning, grouped by category (see LOG.md headings),
   including prompts/instructions (short summaries), decisions, delegations, actions, file changes,
   corrections (owner-caught), self-corrections, scoring/judgment errors, AI tools used, and cost.
10. **README:** ask the owner for input on: how to run it, clarifications made, improvements they
    would add with another day; Claude writes one paragraph for the sales manager.
11. **CSV conversion** of the final approved accounts workbook happens only when the owner asks.
12. **Web UI runs locally only.** Do not deploy anywhere.
13. Self-check questions for every step: careful (not fastest) handling of data problems? verified
    with a measured error rate before handing over? unclear rules asked about and documented? can a
    rep/manager understand every decision? can someone else run and maintain it?
14. **After-columns** in accounts-XLSX.xlsx are a different color (green) from the originals and end
    with an **Agent Notes** column explaining each edit and why.
15. **reps-XLSX.xlsx:** keep `current_book_size` unedited; add `new_book_size` after assignment.
16. **Cost logging:** ask the owner to paste `/cost` at every checkpoint and STOP until they do.
17. **Human in the loop:** raise tricky accounts, hierarchies, scoring and assignment calls with the
    owner instead of deciding silently.
18. Sub-agents are allowed when they make work faster (parallel tasks).
19. Owner decisions D1-D43 are in LOG.md section 3; code comments cite them as (D<n>).
20. **Never overwrite owner edits** to the workbooks. The owner formats files by hand (e.g. the
    banner row in `accounts`); scripts must preserve it (see step 1 writer).
21. Children of customer parents are owned by account management (D21). Business units move with
    their parent and use the parent's rep's capacity (D25).
22. GitHub repo is **public** (D19); `gh` CLI installed via winget; Claude handles setup (D27); authenticated as the owner's account 2026-10-14.
23. Update LOG.md and CLAUDE.md **before ending every turn**, not afterwards.
25. **Before every push:** run `python pipeline/check_publish_safety.py` (must report 0 findings).
    Never publish personal names, emails, usernames, tokens or local folder paths (D42).
26. **Do not run `gh auth logout` until the owner approves** (D43).
27. `private_originals/` (git-ignored) holds the true original exports; `backup_originals/` holds
    metadata-scrubbed copies with identical cell data — the pipeline reads the latter.
24. For simple sub-agent tasks, propose a cheaper model (e.g. Sonnet/Haiku) rather than defaulting to Opus.

## How the output is built

Python 3.13 + pandas + openpyxl (`requirements.txt`). Every script reads the pristine files in
`backup_originals/` and regenerates its outputs, so any step can be re-run safely.

| File | Purpose |
|---|---|
| `pipeline/config.py` | All constants: paths, rules.md region appendix, segment thresholds, and the regexes for the templated notes (relationship, defunct, competitor, churned, "Duplicate?", "~N agents"). |
| `pipeline/step1_clean.py` | Step 1. Cleans fields, infers blank states, merges duplicates, links hierarchies, decides eligibility, writes the workbook + `output/step1_accounts.json`. |
| `pipeline/verify_step1.py` | Independent checks on step 1 (separate, simpler code). Exits non-zero on failure. |
| `pipeline/use_case_schema.json` | Step 2 structured-output schema (approved; exactly the brief's 8 labels). |
| `docs/step2_classification_proposal.md` | Step 2 method, label definitions, note→label table (approved with owner changes D26–D30). |
| `pipeline/step2_classify.py` | Step 2. Applies the note→label decision table, validates every record against the schema, checks the evidence text is the account's own, writes `output/step2_use_cases.json`, rebuilds the workbook. |
| `pipeline/step2_sample.py` | Draws the reproducible stratified 150-company hand-check sample (raw inputs only). |
| `pipeline/step2_handcheck.py` | Compares Claude vs the blind sub-agent labeller, applies adjudications, reports error rate + 95% CI. |
| `docs/step3_scoring_proposal.md` | Approved fit-score weights, routing rules, tie-break (D31–D34). |
| `pipeline/step3_route.py` | Step 3. Scores, routes within region+segment pools with capacity, business units ride with parents, writes reasons, `new_book_size` in reps-XLSX, rebuilds the workbook. |
| `pipeline/verify_step3.py` | Independent step 3 checks incl. score recomputed from raw data and every reason's quotes/numbers grounded. |
| `pipeline/step4_build_ui.py` | Step 4. Builds `web_ui/rep_books.html`: one self-contained offline page (data embedded, no external assets). |
| `pipeline/step5_export_csv.py` | Exports the final workbooks to `output/accounts_final.csv` and `output/reps_final.csv` (originals untouched). |
| `pipeline/check_publish_safety.py` | Pre-publish privacy scan; run before every push (0 findings required). |
| `run.py` | Runs steps 1–5 and every check in order; stops on the first failure; opens the UI (`--no-open` to skip). |
| `web_ui/rep_books.html` | The web UI. Committed to the repo so anyone can download it and double-click (D37). |

### Project status
- Step 0 setup: done. Step 1 clean/dedupe/eligibility: done, approved 2026-10-14.
- Step 2 classification: approved with changes (D26–D30); run done (1,452 labelled); blind hand
  check 0/150 errors (CI 0–2.5%). Step 2 cost $2.37. D29 revised (dispatch → media_captions).
  Workbook rebuilt and current. **Approved 2026-10-14.**
  `gh` logged in as the owner's account (log out after step 8 push).
- Step 3 scoring/routing: approved 2026-10-14 (D31–D36). Books 260×5 + Sam 225 (shortfall 35).
- Step 4 web UI: approved 2026-10-14 (no GitHub Pages). Cost $2.12 (running total $10.32).
- Step 5 README: approved 2026-10-14. Cost $0.97 (running total $11.29).
- Step 6 CSV: done 2026-10-14 (`output/accounts_final.csv`, `output/reps_final.csv`); cost $1.45 (running
  total $12.74). Push approved (D41); privacy scan clean (D42).
- Step 8 GitHub: published 2026-10-14 as public repo `Account-Routing-Service` (branch `main`).
  To publish changes: `python run.py` → `python pipeline/check_publish_safety.py` (0 findings)
  → commit → `git push`. `gh auth logout` pending owner approval (D43).

### Step 2 logic
Precedence per company (notes of all merged records count): (1) a note naming a use case → that
label; (2) speech-interest note only → industry-implied label if the industry clearly implies one,
else `other`; (3) no speech signal → `none` (D26). Notes beat industry. Table lives in
`NOTE_RULES` / `INDUSTRY_USE_CASE` in `step2_classify.py` — change a row there and re-run.

### Step 4 (web UI)
`step4_build_ui.py` joins the step 1–3 JSON into one list and embeds it in a single HTML file with
plain JavaScript (no libraries, no network). To change the page, edit the `HTML` string in that file
and re-run. To test: open the file in a browser; `run.py` rebuilds it.

### Step 3 logic
Score = notes use case 35 (or speech interest 20) + intent 5 + industry 25/5 + size 4–20 + funding
15/8 (table in `score()`). Pools = region + segment; business units join their parent's unit and
pool, ranked on the parent's score. Units are sorted by score + D32 tie-break and taken while they
fit in 260 − current book; a unit that does not fit is skipped (D33). Reasons are assembled only
from the account's own fields (`build_reason()`), then audited by `verify_step3.py`.

### Step 1 logic (in order)
1. **Field cleaning** → `_clean` columns. City text with encoding damage (e.g. 'SÃ£o Paulo') is repaired by `fix_mojibake()`. Website → bare lowercase host. linkedin/twitter/crunchbase
   URLs are typed `social_profile` and never used for matching.
2. **Location:** a blank state is filled from the city only when every other row with that city has
   one single state (flag `state_inferred_from_city`). Region comes from the rules.md appendix using
   state only; country is re-derived from state (the country column is not trusted). Anything else
   → `NOT_COVERED` (e.g. `KA` = Karnataka, India).
3. **Same-entity merge** (union-find): same company domain, OR a note saying "Billing domain for X",
   "Self-serve signup. Same company as X", "Product brand of X". The primary record is the named
   real company (for note merges) or the most complete record. Blanks on the primary are filled
   from duplicates; spend is summed across the entity.
4. **Hierarchy** (not merged, D8): "Business unit of X" → `parent_account_id`. "Acquired by X" →
   `acquirer_account_id`.
5. **Eligibility per entity:** no_longer_exists (shut down / parked / acquired) · competitor ·
   existing_customer (entity spend > 0) · territory_not_covered · under_20_employees. All
   applicable reasons are listed. A business unit whose parent is a customer is excluded
   (`parent_is_customer`) because the parent's owner (account management) owns it.
6. **Segment** (eligible only): Enterprise if 500+ employees or Public / Private Equity.
7. **Flags** for human review → `review_flags` column + sheet.

### accounts-XLSX.xlsx layout
- Sheet `accounts`: row 1 = owner's banner ("Original Data" over A–L, "Agent-Worked Data" over the
  after-columns), row 2 = headers, data from row 3, frozen at C3. A–L original (never edited) ·
  M–AK green after-columns (see `column_guide`).
- The writer loads the current workbook as its template, refuses to write if A–L differ from
  `backup_originals/`, and re-applies the owner's column widths by header name.
- Sheets: `summary` (counts + reconciliation check), `exclusions` (every non-eligible row with its
  reason), `entities` (merge groups), `hierarchy`, `review_flags`, `column_guide`.
