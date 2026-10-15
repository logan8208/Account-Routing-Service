# Account Routing Service

Cleans the raw CRM export of ~2,000 accounts and assigns the good ones to six account executives,
following the routing rules in [`rules.md`](rules.md). Every account gets a plain-English reason,
and each rep's book can be browsed in a small web page that runs on your own computer.

All companies, people and data in this project are fictional.

> **📒 Project log:** open [`LOG.md`](LOG.md) (click it in the file list above). It is a short
> record of who did what, every decision, every mistake and how it was caught, and what the project
> cost. Build details for engineers are in [`CLAUDE.md`](CLAUDE.md).

---

## For the sales manager

Every one of the 2,020 CRM rows is accounted for: 945 accounts are assigned to reps, 507 good but
lower-ranked accounts are waiting as "unassigned", and 568 rows are excluded or merged, each with
its reason. Reps got the highest-scoring companies in their region and segment, scored on what
`rules.md` says wins (a speech use case in the notes, our strongest industries, mid-to-large size,
recent funding), until their book reached 260.

**How to open it**

1. Open [`web_ui/rep_books.html`](web_ui/rep_books.html) in this GitHub repo.
2. Click **Download raw file** (the download icon at the top right of the file view).
3. Double-click the downloaded file. It opens in your browser, works offline, and needs no install
   or login.

**What to double-check**

- **Sam Okafor (West Enterprise) has 35 empty slots.** Only 195 eligible West Enterprise companies
  exist, and we chose not to fill from other regions or segments.
- **Kenji Mori (West Mid-Market) only had room for 50.** 178 eligible companies are unassigned,
  including 26 that score 60+ with a real speech use case. Worth a look.
- **85 use-case labels are flagged for review:** dispatch radio/phone companies labelled
  `media_captions`, and companies that show speech interest without saying what for.
- **The "Needs review" tab:** states filled in from the city, LinkedIn/Twitter links instead of real
  websites, employee counts that conflict with the notes, churned customers that still show spend.
- **Use-case labels haven't been compared with the team's ground truth yet.** They follow the agreed
  rules, and an independent blind check of 150 accounts found no disagreements.

---

## How to run it

### Just view the rep books (no setup)

1. Open [`web_ui/rep_books.html`](web_ui/rep_books.html) in this repo on GitHub.
2. Click **Download raw file**.
3. Double-click the downloaded file. It opens in any modern browser and works offline.

(If you cloned or downloaded the repo, just double-click `web_ui/rep_books.html`.)

### Rebuild everything from the original data

Requires Python 3.11+.

```bash
pip install -r requirements.txt
python run.py            # rebuild, run every check, open the web UI
python run.py --no-open  # same, without opening a browser
```

Close `accounts-XLSX.xlsx` and `reps-XLSX.xlsx` in Excel first (Windows locks open files).
`run.py` stops at the first failed check and says which step failed.

---

## What is in the repo

| Path | What it is |
|---|---|
| `web_ui/rep_books.html` | The web UI: rep books, unassigned, excluded & merged, needs review, how it works. |
| `accounts-XLSX.xlsx` | The accounts workbook. Columns A–L are the original export, never edited. The green "Agent-Worked Data" columns are the cleaned values, use case, score, assignment, reason and Agent Notes. Extra sheets: `summary`, `exclusions`, `entities` (merged duplicates), `hierarchy`, `review_flags`, `capacity`, `rep_books`, `column_guide`. |
| `reps-XLSX.xlsx` | The six reps. `current_book_size` is unchanged; `new_book_size` is added. |
| `output/accounts_final.csv` | **The final accounts file as CSV:** all 2,020 CRM rows, original columns + every agent-worked column (cleaned values, eligibility and exclusion reason, use case, score, assigned rep, reason, Agent Notes). |
| `output/reps_final.csv` | The reps with `current_book_size` and `new_book_size`. |
| `output/` (other) | Machine-readable outputs: `step1_accounts.json` (cleaned + eligibility), `step2_use_cases.json`, `step3_assignments.json`, `step3_capacity.json`, the hand-check sample, blind labels and report. |
| `pipeline/` | The code, one script per step plus independent `verify_*` scripts. |
| `docs/` | The approved step 2 (classification) and step 3 (scoring) proposals, and the final instruction-by-instruction check (`final_check.md`). |
| `backup_originals/` | Untouched copies of the input files. The pipeline only ever reads these. |
| `rules.md`, `Initial Prompt to Claude.md` | The routing spec and the project brief. |
| `LOG.md` | The project log: delegation, prompts, decisions, mistakes and how they were caught, cost. |
| `CLAUDE.md` | How the output is built, for engineers maintaining it. |
| `accounts.csv`, `reps.csv` | The original CSV exports, unedited. |

### Pipeline

| Step | Script | Check |
|---|---|---|
| 1. Clean, de-duplicate, link hierarchies, decide eligibility | `pipeline/step1_clean.py` | `pipeline/verify_step1.py` (18 checks) |
| 2. Classify one use case per eligible company | `pipeline/step2_classify.py` | schema + evidence check on every record; `pipeline/step2_handcheck.py` (blind sample) |
| 3. Score, route to reps under capacity, write reasons | `pipeline/step3_route.py` | `pipeline/verify_step3.py` (17 checks) |
| 4. Build the web UI | `pipeline/step4_build_ui.py` | rendered and screenshot-tested in a browser |
| 5. Export the final CSVs | `pipeline/step5_export_csv.py` | row/column counts asserted; read straight from the workbooks |
| Final check against `rules.md` and the brief | `pipeline/verify_rules.py` | 19 checks |

Before publishing changes, run `python pipeline/check_publish_safety.py`: it scans everything git
would publish (including inside the workbooks) for emails, personal folder paths, user names,
tokens and personal names in file metadata, and must report 0 findings.

Shared rules (region map, thresholds, note patterns) live in `pipeline/config.py`. The use-case
table is `NOTE_RULES` in `step2_classify.py`; the score weights are in `score()` in
`step3_route.py`. Change a value there and run `python run.py`.

---

## Results

| Rep | Region / segment | Book before | Room | Eligible | Assigned | Book after | Left over | Shortfall |
|---|---|---|---|---|---|---|---|---|
| Priya Natarajan | East Mid-Market | 140 | 120 | 275 | 120 | 260 | 155 | 0 |
| Marcus Bell | East Enterprise | 60 | 200 | 288 | 200 | 260 | 88 | 0 |
| Dana Whitfield | Central Mid-Market | 95 | 165 | 229 | 165 | 260 | 64 | 0 |
| Luis Ortega | Central Enterprise | 45 | 215 | 237 | 215 | 260 | 22 | 0 |
| Kenji Mori | West Mid-Market | 210 | 50 | 228 | 50 | 260 | 178 | 0 |
| Sam Okafor | West Enterprise | 30 | 230 | 195 | 195 | 225 | 0 | **35** |

**Excluded** (first reason per company): under 20 employees 253 · existing customer 164 · outside
territory 66 · no longer exists 22 · competitor 7 · business unit of a customer 1. Plus 55 duplicate
rows merged into their company.

**Use cases:** none 839 · call_analytics 196 · media_captions 193 · voice_agent 73 · other 41 ·
clinical_documentation 39 · legal_transcription 38 · meeting_notes 33.

**Hand check of the use cases:** a stratified sample of **150** companies, covering every note
template, was labelled blind by an independent Claude sub-agent. Result: **0 errors (0.0%, 95% CI
0.0–2.5%)**.

That measures whether the agreed rules were applied correctly. The rules most likely to differ from
the ground truth are listed in `output/step2_handcheck_report.md`.

**How relationships hidden in the notes were found:** the notes are templated ("Business unit of X",
"Billing domain for X"), so fixed rules find them reliably and the same way every run. Claude also
read all 85 distinct notes to confirm the rules miss nothing.

**Why the score weights are what they are:** see
[`docs/step3_scoring_proposal.md`](docs/step3_scoring_proposal.md). In short, notes describing the
company's own speech project count most, then industry, then size, then recent funding.

---

## Final check

Every instruction in the brief, `rules.md`, `CLAUDE.md` and Logan's decisions was checked
against the finished output: [`docs/final_check.md`](docs/final_check.md).

`python run.py` runs **54 automated checks**, and all pass:

- 18 on cleaning
- 17 on scoring and routing, including every reason checked against its account's own data
- 19 testing the output directly against `rules.md`, e.g. "no customer in any book", "AZ → Central"

Plus a schema and evidence check on all 1,452 use-case labels, and a privacy scan before publishing
(0 findings).

---

## What it cost

Measured with Claude Code's `/cost` (model Claude Opus 5.5) at each checkpoint. Details are in
[`LOG.md`](LOG.md) § Cost.

| Stage | Cost |
|---|---|
| Planning, setup, first cleaning build | not measured (session restarted before the first reading) |
| Cleaning fixes and classification proposal | $2.82 |
| Use-case classification and blind hand check | $2.37 |
| Scoring proposal | $1.57 |
| Scoring and routing | $1.44 |
| Web UI | $2.12 |
| README | $0.97 |
| CSV export and encoding fix | $1.45 |
| Privacy review and publishing | $2.13 |
| **Total measured** | **≈ $14.87**, about 6% of a weekly Claude plan limit |

The final round of edits (this README, the shorter log, the final check) comes on top of that.

---

## Clarifications made where the rules were unclear

Decisions by Logan when Claude asked. IDs match `LOG.md` and the code comments.

**Eligibility**
- Any spend greater than $0 in the last 12 months makes a company a customer, even if the notes say
  it churned (the conflict is flagged, not acted on). (D6, D7)
- Shut down, parked domain, or acquired = no longer exists, linked to the acquirer. (D9)
- Competitor = core product is a speech engine. Companies that built their own STT, have a speech
  team, post Speech ML jobs, or use a competitor's API are prospects, not competitors. (D10)
- Blank employee count: kept eligible, small score penalty, flagged. (D11)
- Employee count is trusted over agent counts in notes; the 14 tiny companies with large agent
  counts stay excluded but are flagged. (D12, D24)
- Blank state is filled from the city only when that city has one state everywhere else in the data;
  flagged for enrichment. Anything outside US/Canada is not covered. (D13)

**Duplicates and hierarchies**
- Records of the same company are merged. If any record has spend, the whole company is a customer.
  (D8)
- "Billing domain for", "Self-serve signup. Same company as" and "Product brand of" notes mean the
  same company. (D23)
- Business units are not merged: they go to whichever rep owns the parent, take one slot in that
  book, and move with the parent. Business units of customers stay with account management. (D8,
  D21, D25)
- LinkedIn/Twitter/Crunchbase links are never used to merge; those accounts need their real domain
  enriched. (D22)

**Use case**
- Labels are exactly the brief's 8.
- No speech signal in the notes → `none`; industry alone is not a use case. (D26)
- Podcasts and lecture capture → `media_captions`. (D28)
- Dispatch radio/phone → `media_captions`, flagged for review. (D29)
- Speech interest without a use case → the industry's use case if clear, else `other`. (D30)

**Scoring and routing**
- Recent funding: full credit 2025–26, partial 2024. "Duplicate?" note: penalty only if no duplicate
  was found. "Not yet qualified" referral: neutral. (D14, D15)
- +5 buying-intent bonus for recent demo requests or vendor evaluations; weights as in
  `docs/step3_scoring_proposal.md`. (D31, D34)
- Room = 260 − current book. Ties broken by use-case confidence, then size, then funding year. A
  parent + business unit that do not fit together are skipped for the next account. (D16, D32, D33,
  D36)
- A rep with empty slots is not filled from another region **or segment**; the shortfall is
  reported. (D35)

**Output**
- The original columns are never edited; cleaned values sit in separate green columns with Agent
  Notes. The web UI is a single offline file in the repo, not deployed (no GitHub Pages). (D4, D37)

---

## What I would add with another day

*(From Logan.)*

- Enrich the 8 accounts that have only social-media URLs, and the 20 states inferred from city.
- Revisit Kenji's 50-slot limit, given 26 strong accounts left over.
- Decide what to do with Sam's 35 open slots.
- Compare the use-case labels against the ground truth and adjust the label table.
- Automate it so that it re-runs on a schedule as new accounts arrive, so the books "stay sorted."
- Let reps leave feedback on reasons in the UI, and set up summary notifications delivered to
  Logan.
- Further enrich account data with tools like Clay and AI web-scraping / intent-scoring tools, so we
  know accurately for **all** accounts whether they align with our product (Voice AI
  infrastructure / model / STT service); then adjust scores to align more closely with our ICP and
  improve assignments from there.
- Add automated suggestions for sales managers to review accounts and rep books where there are
  gaps — e.g. a rep without a full 260 while accounts from other segments could fill the gap — then
  discuss with the sales managers and operationalize their input in the automated process as far as
  possible.
- Add more to the web UI so reps can group by other categories such as city, explore more deeply to
  run controlled, organized campaigns, and explore intent scoring and accounts' tech stacks to dig
  for Voice AI use cases.

---

## How this was built

Built with Claude Code (model Claude Opus 5.5) working with Logan, one step at a time,
with Logan's approval at each step.

One Claude sub-agent was used as an independent blind labeller for the use-case hand check.

[`LOG.md`](LOG.md) records the prompts, the decisions, every mistake (including Claude's own and how
each was caught) and the cost.
