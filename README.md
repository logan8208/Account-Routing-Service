# Account Sorting & Routing

Takes the raw CRM export of ~2,000 accounts, cleans it, removes duplicates and ineligible accounts
(with a reason for every one), classifies each company's speech use case, scores fit, assigns
accounts to six account executives under the routing rules in [`rules.md`](rules.md), and shows each
rep's book, with a readable reason per account, in a small local web UI.

All companies, people and data in this project are fictional.

---

## For the sales manager

**What this is.** Every one of the 2,020 CRM rows has been accounted for. After merging 55 duplicate
rows, the 1,965 real companies split into 513 that are excluded (existing customers, under 20
employees, competitors, companies that no longer exist, outside our territory, or business units of
customers) and 1,452 eligible prospects. Each eligible company has a fit score out of 100 built from
what `rules.md` says wins: a speech use case in the notes, our strongest industries, mid-to-large
size, and recent funding. Reps got the highest-scoring companies in their region and segment until
their book reached 260. 945 accounts are assigned; 507 good-but-lower-ranked accounts are waiting as
"unassigned", and every account (assigned, unassigned or excluded) carries a plain-English reason
built only from its own CRM data. **To open it:** go to the [`web_ui/rep_books.html`](web_ui/rep_books.html)
file in this GitHub repo, click **Download raw file** (the download icon at the top right of the
file view), then double-click the downloaded file — it opens in your browser, works offline, and
needs no install or login. **What to double-check:** (1) Sam Okafor (West Enterprise) has 35 empty
slots because only 195 eligible West Enterprise companies exist — we chose not to fill them from
other regions or segments; (2) Kenji Mori (West Mid-Market) had room for only 50, so 178 eligible
companies are unassigned, including 26 that score 60+ with a real speech use case — worth a look;
(3) 85 use-case labels are flagged for review (dispatch radio/phone companies labelled
`media_captions`, and companies that show speech interest without saying what for); (4) the
**Needs review** tab lists data the rules handled but a person should confirm (states filled in from
the city, LinkedIn/Twitter links instead of real websites, size conflicts with notes, churned
customers that still show spend). The use-case labels follow the rules we agreed and matched an
independent blind check on 150 accounts with no disagreements, but they have not yet been compared
with the team's ground truth.

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
| `docs/` | The approved step 2 (classification) and step 3 (scoring) proposals. |
| `backup_originals/` | Untouched copies of the input files. The pipeline only ever reads these. |
| `rules.md`, `Initial Prompt to Claude.md` | The routing spec and the project brief. |
| `LOG.md` | Full project log: every instruction, decision, action, correction and cost. |
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

Exclusions (first reason per company): under 20 employees 253 · existing customer 164 · outside
territory 66 · no longer exists 22 · competitor 7 · business unit of a customer 1. Plus 55 duplicate
rows merged into their company.

**Use-case classification:** 1,452 companies labelled (none 839, call_analytics 196,
media_captions 193, voice_agent 73, other 41, clinical_documentation 39, legal_transcription 38,
meeting_notes 33). Hand check: a stratified sample of **150** covering every note template,
labelled blind by an independent Claude sub-agent → **0 errors, 0.0% (95% CI 0.0–2.5%)**. This
measures correct application of the agreed rules; the policy calls most likely to differ from
ground truth are listed in `output/step2_handcheck_report.md`. Cost of step 2 (design, run, hand
check): **$2.37** in Claude Code session tokens (see `LOG.md` § Cost).

---

## Clarifications made where the rules were unclear

Decisions by the project owner when Claude asked. IDs match `LOG.md` and the code comments.

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
- Records of the same company are merged; if any record has spend, the whole company is a customer.
  "Billing domain for", "Self-serve signup. Same company as" and "Product brand of" notes are the
  same company. (D8, D23)
- Business units are not merged: they go to whichever rep owns the parent, take one slot in that
  book, and move with the parent. Business units of customers stay with account management. (D8,
  D21, D25)
- LinkedIn/Twitter/Crunchbase links are never used to merge; those accounts need their real domain
  enriched. (D22)

**Use case**
- Labels are exactly the brief's 8. No speech signal in the notes → `none` (industry alone is not a
  use case). Podcasts and lecture capture → `media_captions`. Dispatch radio/phone → `media_captions`
  (flagged for review). Speech interest without a use case → the industry's use case if clear, else
  `other`. (D26, D28, D29, D30)

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

*(From the project owner.)*

- Enrich the 8 accounts that have only social-media URLs, and the 20 states inferred from city.
- Revisit Kenji's 50-slot limit, given 26 strong accounts left over.
- Decide what to do with Sam's 35 open slots.
- Compare the use-case labels against the ground truth and adjust the label table.
- Automate it so that it re-runs on a schedule as new accounts arrive, so the books "stay sorted."
- Let reps leave feedback on reasons in the UI, and set up summary notifications delivered to the
  owner.
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

Built with Claude Code (model Claude Opus 5.5) working with the project owner, step by step with an
approval at each step. One Claude sub-agent was used as an independent blind labeller for the
use-case hand check. `LOG.md` records every prompt, decision, correction (including Claude's own
mistakes and how they were caught) and the token/dollar cost per step.
