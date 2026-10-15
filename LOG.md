# Project Log — Account Sorting & Routing

Grouped by category. Newest entries at the bottom of each section. Dates are absolute (YYYY-MM-DD).
Decision IDs (D1, D2, ...) match the question numbers Claude asked on 2026-10-13 and are cited in
the code comments.

## 1. AI tools used

- 2026-10-13 — Claude Code (terminal/CLI, Windows), model **Claude Opus 5.5** (`claude-opus-5-5`).
- 2026-10-14 — Owner confirmed: no Anthropic API key; all LLM work (e.g. use-case classification)
  runs inside this Claude Code session. Owner permitted sub-agents (Claude Code Agent tool) where
  they speed things up. Not used for step 1 (one sequential script; faster inline).
- 2026-10-14 — Sub-agent used for the first time: one independent Claude sub-agent (general-purpose,
  same model) as a **blind second labeller** for the step 2 hand check. Its cost is included in the
  session `/cost` total.
- 2026-10-14 — Microsoft Edge (headless) used as a test harness to render and screenshot the web
  UI. Not an AI tool; listed for completeness.

## 2. Owner prompts, plans & instructions (short summaries)

- 2026-10-13 — **Initial prompt** (`Initial Prompt to Claude.md`): build a system that cleans ~2,000
  CRM accounts, flags/merges duplicates, excludes ineligible accounts with reasons, classifies use
  case (fixed label set, structured schema, approval first, sampled error rate + cost), scores and
  routes to 6 reps per `rules.md` with grounded reasons, exposes rep books in a local web UI, and
  documents it in a README. Deliverables in a GitHub repo. Create CLAUDE.md first, keep this log,
  get approval before each step, read everything and ask clarifications, then send an ordered plan.
- 2026-10-13 — Claude sent 20 clarifying questions + an 8-step plan (0 setup … 8 finish).
- 2026-10-14 — **Owner answered all questions** (see section 3), approved the plan, said "execute",
  allowed sub-agents, asked to be pulled in on tricky accounts/hierarchies/scoring/assignment calls,
  and asked to continuously update LOG.md and CLAUDE.md.
- 2026-10-14 — New instruction: after-columns in accounts-XLSX.xlsx must be a **different color**
  from the original columns, and include an **Agent Notes** column explaining each edit and why.
- 2026-10-14 — New instruction: in reps-XLSX.xlsx keep `current_book_size` unedited and add
  `new_book_size` (after assignment) for before/after comparison.
- 2026-10-14 — New instruction: whenever Claude needs `/cost` for logging, Claude must ask and
  **stop working until the owner pastes it**.
- 2026-10-14 — Clarified: "rules" = `rules.md` + `Initial Prompt to Claude.md` + every amended or
  clarified instruction given in conversation.
- 2026-10-14 — Owner pasted `/cost` (logged in section 10) and said to wait for feedback.
- 2026-10-14 — **Owner feedback round 2:** owner added a banner row ("Original Data" / "Agent-Worked
  Data") above the headers in the `accounts` sheet and changed column widths (keep these). Confirmed
  decisions D21–D25 and D16/D19 updates (section 3). Said "keep working" → **step 1 treated as
  approved**. Asked Claude to install `gh` via winget and keep CLAUDE.md / LOG.md updated.
- 2026-10-14 — Claude sent the step 2 proposal (schema + method) with open questions Q-A/B, Q-C,
  Q-D, Q-E, asked the owner to run `! gh auth login`, and requested `/cost` (step-2 "before"
  reading). Waiting on all three before running classification.
- 2026-10-14 — Owner asked: "are claude.md and the log updated?" Claude checked; found the gaps
  below and filled them.
- 2026-10-14 — Owner pasted `/cost` for the step 2 pre-run checkpoint (section 10) and said to log
  it and wait for the next round of feedback before taking more action. Step 2 questions
  Q-A/B…Q-E still unanswered.
- 2026-10-14 — **Owner feedback round 3:** asked Claude to handle GitHub login itself; answered the
  step 2 questions (D26–D30); "keep working and keep CLAUDE.md and LOG updated" → step 2 schema +
  method treated as **approved** with the owner's changes.
- 2026-10-14 — Owner pasted `/cost` (step 2 "after" reading, section 10) and said to log it and
  wait for the next round of feedback before taking more action. Still open: step 2 approval,
  D29 `audio_analytics` confirmation, GitHub login (owner to say "ready for GitHub").
- 2026-10-14 — **Owner feedback round 4:** after Claude's flag about the brief's fixed label set,
  owner changed D29: dispatch notes → `media_captions` (drop `audio_analytics`). Asked for a new
  GitHub code and what the code is for / whether it gives Claude permanent GitHub access.
- 2026-10-14 — Owner closed the workbook and asked what step 2 approval Claude needs.
- 2026-10-14 — **Owner: "step 2 approved".** Claude moved to step 3 (scoring proposal).
- 2026-10-14 — Owner pasted `/cost` (step 3 baseline, section 10) and said to log it and wait for
  the next round of feedback. Step 3 Q1–Q4 still open.
- 2026-10-14 — **Owner answered step 3 Q1–Q4** (D31–D34) → scoring proposal approved; Claude built
  step 3.
- 2026-10-14 — Owner pasted `/cost` (step 3 "after", section 10) and said to log it and wait for
  the next round of feedback. Step 3 testing and H1/H2 still open.
- 2026-10-14 — **Owner answered H1/H2** (D35, D36). Did not yet say step 3 is approved; Claude
  asked for explicit step 3 approval before starting the web UI.
- 2026-10-14 — **Owner: "step 3 approved"; step 4 UI plan approved** on condition that people with
  GitHub access can open and use the web UI easily from the repo (e.g. a link in the README).
- 2026-10-14 — Owner pasted `/cost` (step 4 "after", section 10) and said to log it and wait for
  the next round of feedback. Step 4 testing and the GitHub Pages question (D37) still open.
- 2026-10-14 — **Owner: "The UI html looks great. No need to implement GitHub Pages."** → step 4
  approved. Claude moved to step 5 (README) and asked the owner the README questions.
- 2026-10-14 — **Owner answered README questions R1–R4:** R1 run instructions as proposed; R2
  clarifications grouped by topic; R3 owner's own 9-item "another day" list (verbatim in README);
  R4 manager paragraph as proposed **plus instructions for opening the web UI from the Git repo**.
- 2026-10-14 — Owner pasted `/cost` (step 5 "after", section 10) and said to log it and wait for
  the next round of feedback. README approval still open.
- 2026-10-14 — **Owner: "step 5 approved".** Claude asked the step 6 (CSV) and step 8 (GitHub)
  questions F1–F4 before acting.
- 2026-10-14 — **Owner answered F1–F4:** final workbook approved and CSV requested; single CSV plan
  approved; original CSVs untouched; public repo named "Account Routing Service".
- 2026-10-14 — Owner pasted `/cost` (step 6 "after", section 10) and said to log it and wait for
  the next round of feedback. Push go-ahead (D41) still open.
- 2026-10-14 — **Owner feedback (pre-publish):** repo name/plan approved; asked whether Claude did a
  full scan for sensitive data (passwords, emails, usernames, credentials, computer folder paths)
  and to obfuscate identifying path parts; **do not run `gh auth logout` until the owner approves**.
- 2026-10-14 — **Owner: "push it"** → step 8 (create public repo `Account-Routing-Service`, push).

## 3. Owner decisions & clarifications (rule interpretations)

- **D1** `accounts.csv` / `reps.csv`: keep unedited for now; owner may later ask for the same edits.
- **D2** Installing pandas + openpyxl approved.
- **D3** Excel files closed by owner before writing.
- **D4** After-columns live inside `accounts-XLSX.xlsx` next to untouched originals, in a different
  color, with an Agent Notes column; exclusions on a new sheet; untouched backup kept.
- **D5** Follow rules.md + Initial Prompt + all conversation amendments.
- **D6** Any spend = customer, per spec. Churned-with-spend rows are customers (not a separate
  "churned" category); just note the data conflict.
- **D7** Any spend > $0 = customer (no minimum).
- **D8** True duplicates of the same entity: merge; if any record has spend the whole company is a
  customer. **Parent–child hierarchy (different entities) is NOT merged**: the child goes to
  whichever rep owns the top-level parent, while still following the rest of the rules.
- **D9** Acquired / shut down / parked domain: exclude as "no longer exists", link to the acquirer.
- **D10** Competitor exclusion as proposed. (Owner asked what "excluding the notes" meant —
  Claude clarified 2026-10-14: the *accounts* are excluded from rep books; notes are never edited.)
- **D11** Blank employee count: keep eligible, Mid-Market unless Public/PE, small penalty, flag.
- **D12** Employee count vs. notes conflict: trust employee_count and flag (agents may not be FTEs).
- **D13** Blank state: fill from city only when unambiguous, flag, note "double-check state
  enrichment later". Non-US/Canada / unmapped → excluded "not covered by this team".
- **D14** Funding recency: full credit 2025–2026, partial credit 2024.
- **D15** "Duplicate?" note: no penalty if the duplicate is found and merged; small penalty if not.
  "Not yet qualified" partner referral: neutral.
- **D16** Capacity = 260 − current_book_size (owner: "agree for now, may change later").
- **D17** No API key; classification cost = this session's tokens.
- **D18** Web UI: Python script builds an HTML page, run locally; no deployment.
- **D19** Claude creates the GitHub repo; owner wants it shareable by emailed URL with access only
  for people who have the URL. (Open: GitHub has no URL-only repos — options sent 2026-10-14.)
- **D20** Claude asks for `/cost` whenever needed and waits for it.
- **Notes relationships:** rules (regex on templated notes) + Claude's review of all 85 distinct
  notes — approved.
- **D10 (confirmed 2026-10-14)** Owner agrees: competitor *accounts* are excluded; done correctly.
- **D16 (confirmed 2026-10-14)** Capacity 120 / 200 / 165 / 215 / 50 / 230 (REP-01..06) = 260 −
  current book. Also apply rules.md as written: overflow → highest scoring kept, report leftovers;
  room left after region exhausted → do NOT fill from another region, report shortfall.
- **D19 (updated 2026-10-14)** GitHub repo will be **public**. Install `gh` with winget.
- **D21** Any subsidiary (child) account of a parent that is a customer is also owned by the account
  management team with the parent, so reps focus solely on new-logo account hierarchies.
  (Covers Meridian Labs ACC-101804 → excluded, confirmed.)
- **D22** Accounts whose website is a social/profile URL (LinkedIn, Twitter, also Crunchbase) are
  never merged on URL alone; Claude's Agent Notes on those rows say the real domain needs to be
  updated via enrichment.
- **D23** "Product brand of X" = same company as X → merged (confirmed). Birch Scribe, Blue Pay,
  Maple Call become customers via their brand records' spend.
- **D24** The 14 accounts under 20 employees whose notes mention 40–2,000 contact-center agents stay
  excluded but flagged: company size / ICP does not meet targeting criteria.
- **D25** Business units: child counts against the parent's rep's capacity, and moves with the
  parent (parent in the book → child in the book; parent not → child unassigned).
- ~~Pending Q-A/B…Q-E~~ → answered 2026-10-14 as D26–D30 below.
- **D26 (Q-A/B)** Companies with no speech signal in notes (783) → `none` (Option B). Industry alone
  is never a use case.
- **D27** Claude handles the GitHub login/setup itself. (The browser approval step needs the owner's
  GitHub account, so Claude started `gh auth login --web` and gave the owner the one-time code.)
- **D28 (Q-C)** Podcasts and lecture capture → `media_captions`.
- **D29 (Q-D)** Dispatch/driver radio-and-phone transcription → new label **`audio_analytics`**
  (owner's choice; not `call_analytics`, not `other`). **Claude flagged a conflict:** the brief fixes
  8 labels and says ground truth will be compared against them; `audio_analytics` is a 9th label, so
  these 44 companies may score as mismatches. Implemented as instructed (one table row, easy to
  change); owner confirmation requested.
- **D29 (revised 2026-10-14)** Owner: dispatch/driver radio-and-phone notes (44) → **`media_captions`**;
  `audio_analytics` dropped, back to the brief's 8 labels. Claude's note: a loose fit (media_captions
  is defined as published audio/video; dispatch audio is operational) — Claude's earlier
  recommendation was `other`. Implemented as instructed and marked needs_review; flagged to owner.
- **D30 (Q-E)** Speech-interest-only notes (63) → industry-implied label if clear, else `other`.
- **Step 2 approved** by owner 2026-10-14 (results + hand check).
- ~~Pending step 3 Q1–Q4~~ → answered 2026-10-14 as D31–D34.
- **D31 (Q1)** Keep the +5 buying-intent bonus (demo request 2025/26, "evaluating several vendors").
- **D32 (Q2)** Tie-break: use-case confidence → employees (≤10,000; over 10k ranks below) → funding
  year → lower account_id.
- **D33 (Q3)** Parent + business unit needing 2 slots with 1 left: skip the pair, give the slot to
  the next account (book exactly full). (Did not occur in this data.)
- **D34 (Q4)** Weights exactly as proposed in `docs/step3_scoring_proposal.md`.
- ~~Pending H1/H2~~ → answered 2026-10-14 as D35/D36.
- **D35 (H1)** Sam (WEST Enterprise) keeps 35 empty slots; report the shortfall. Do NOT fill from
  WEST Mid-Market left-overs (segment ownership stands; same-region/other-segment is not used).
- **D36 (H2)** Capacity stays 260 − current book for now (Kenji keeps 50 slots; 178 left over,
  including 26 scoring ≥60 — reported, for the sales manager to review).
- **Step 3 approved** by owner 2026-10-14.
- **D37** Web UI must be easy to open for anyone with access to the GitHub repo. Claude's approach
  (within the brief's "do not deploy"): one self-contained offline HTML file committed to the repo
  (`web_ui/rep_books.html`), linked from the README with download-and-double-click steps.
  GitHub Pages: **not used** (owner, 2026-10-14) — consistent with the brief's "do not deploy".
- **Step 4 approved** by owner 2026-10-14.
- **R1–R4 (README, 2026-10-14):** see section 2; all applied in `README.md`.
- **Step 5 approved** by owner 2026-10-14.
- **D38 (F1)** `accounts-XLSX.xlsx` approved as final; convert to CSV now.
- **D39 (F2)** One `output/accounts_final.csv` (all rows, original + agent-worked columns) plus
  `output/reps_final.csv`; no separate exclusion / rep-book CSVs.
- **D40 (F3)** `accounts.csv` and `reps.csv` stay untouched (confirms D1).
- **D41 (F4)** Public GitHub repo "Account Routing Service" with everything in the folder. GitHub does
  not allow spaces → Claude proposed `Account-Routing-Service` (description "Account Routing
  Service") — **approved by owner 2026-10-14.**
- **D42** Before publishing: full sensitive-data scan; obfuscate identifying parts of local folder
  paths (→ `C:\Users\<user>\...`); remove usernames.
- **D43** Claude must ask before running `gh auth logout` and wait for the owner's approval.

## 4. Delegation — what Claude does vs. what the owner does

- 2026-10-13 — Delegated to Claude: everything in the brief (pipeline, classification, scoring,
  routing, web UI, README draft, log). Owner: approvals/testing at each step, rule clarifications,
  README input (run instructions review, clarifications, improvements list).
- 2026-10-14 — Owner: will paste `/cost` output on request; will act as human-in-the-loop on tricky
  accounts/hierarchies/scoring/assignment. Claude: creates the GitHub repo.
- 2026-10-14 — GitHub setup delegated to Claude (D27); owner only approves the browser login.
- 2026-10-14 — README: owner wrote the "what I would add with another day" list; Claude wrote the
  sales-manager paragraph, run instructions and clarifications summary.

## 5. Actions taken (chronological)

- 2026-10-13 — Read `Initial Prompt to Claude.md` and `rules.md` in full.
- 2026-10-13 — Read-only profiling of `accounts-XLSX.xlsx` and `reps-XLSX.xlsx` (Python stdlib).
- 2026-10-13 — Created `CLAUDE.md` and `LOG.md`. Sent questions + plan.
- 2026-10-14 — **Step 0:** installed pandas 3.0.6 + openpyxl 3.1.5 (`requirements.txt`); `git init`;
  copied all four input files to `backup_originals/` (SHA-256 verified identical); created
  `pipeline/`, `output/`, `.gitignore`. Confirmed Excel lock files gone. `gh` CLI is not installed.
- 2026-10-14 — Read all 85 distinct notes and resolved every relationship note's target name: all 35
  named parents/acquirers match exactly one company (no fuzzy matching needed in this data).
- 2026-10-14 — Reviewed all 42 shared-domain groups by hand. 40 are true duplicates (same name stem,
  city, size). 2 are NOT: `linkedin.com` (4 unrelated companies) and `twitter.com` (3) — profile
  links, not company domains. Also `crunchbase.com` (1). These 8 are never used for matching.
- 2026-10-14 — **Step 1 built:** `pipeline/config.py`, `pipeline/step1_clean.py`,
  `pipeline/verify_step1.py`. Ran: 2,020 rows → 1,965 companies; 55 rows merged; 513 companies
  excluded; 1,452 eligible. Independent verification script: 16/16 checks pass.
- 2026-10-14 — Sent step 1 results for owner testing.
- 2026-10-14 — Found the owner's workbook edits (banner row 1 merged A1:L1 / M1:AK1, headers moved
  to row 2, freeze C3, custom widths). Verified the original data A–L still matches the backup
  cell-for-cell. Changed `step1_clean.py` to use the current workbook as the template (refuses to
  write if A–L ever stop matching the backup) so owner formatting survives re-runs; fresh runs
  recreate the banner. Updated `verify_step1.py` for the banner row; added a D22 check. Re-ran:
  same counts, 17/17 checks pass, owner widths/merges/freeze/colors confirmed preserved.
- 2026-10-14 — Started `winget install GitHub.cli` (v2.102.0).
- 2026-10-14 — Profiled eligible accounts for step 2 (exact): 550 with a use-case note, 63 speech-interest only, 56 "nothing audio-specific", 783 no signal (incl. 194 blank); no entity has two conflicting use-case notes. Earlier rough estimate (~690 generic / ~570 signal) superseded.
 . Drafted the step 2 proposal
  (`docs/step2_classification_proposal.md`, `pipeline/use_case_schema.json`) for owner approval.
- 2026-10-14 — `winget install GitHub.cli` finished (exit 0): `gh` 2.102.0 at
  `C:\Program Files\GitHub CLI\gh.exe`. Not authenticated yet — owner to run `! gh auth login`.
- 2026-10-14 — Sent step 2 proposal to owner; requested `/cost`. Classification NOT run.
- 2026-10-14 — Started `gh auth login --web` as a background task; one-time device code given to
  the owner (first attempt's code superseded when the process was restarted to keep it alive).
- 2026-10-14 — **Step 2 built and run:** `pipeline/step2_classify.py` (decision table + schema
  validator + grounding check), schema updated with `audio_analytics`. 1,452 classified, 0
  schema/grounding failures: none 839 · call_analytics 196 · media_captions 149 · voice_agent 73 ·
  audio_analytics 44 · other 41 · clinical_documentation 39 · legal_transcription 38 ·
  meeting_notes 33. Evidence: notes 606, notes+industry 63, no_signal 783. needs_review 41.
  Workbook rebuilt with 4 use-case columns before Agent Notes; step 1 checks still 17/17.
- 2026-10-14 — Drew the hand-check sample (`pipeline/step2_sample.py`, seed 20261014): 150
  companies, all 47 note templates/combinations covered. Launched the blind sub-agent labeller.
  Wrote `pipeline/step2_handcheck.py` (agreement, adjudication, Wilson 95% CI, template-weighted
  error rate).
- 2026-10-14 — Blind sub-agent finished (68k sub-agent tokens, 28 s): labelled all 150, read only
  the sample file. `step2_handcheck.py`: **150/150 agreement → Claude's measured error rate 0/150 =
  0.0% (95% Wilson CI 0.0%–2.5%)**, template-weighted 0.0%. Report: `output/step2_handcheck_report.md`,
  with an added section stating the limit: the check measures correct application of the approved
  rules, not whether the rules match ground truth; the policy calls most at risk are listed (D26,
  D29, D28, D30, "nothing audio-specific").
- 2026-10-14 — Restarted `gh auth login --web` (previous device code likely expired); fresh code
  given to owner. Not authenticated yet. Sent step 2 results; requested `/cost` (step 2 "after").
- 2026-10-14 — GitHub device code 97A2-4A07 expired unused (`context deadline exceeded`). Not
  restarting automatically; a fresh code will be started when the owner says they are at the browser.
- 2026-10-14 — Applied revised D29: schema back to 8 labels; dispatch rule → media_captions
  (needs_review = true). Re-ran step 2: 0 failures; media_captions 193 (149 + 44), needs_review 85.
  Hand check re-scored with `POLICY_RELABEL` (blind label name audio_analytics → media_captions,
  not a re-judgement): still 150/150, 0.0% (CI 0–2.5%). **Workbook rebuild failed — file open in
  Excel (PermissionError)**; JSON outputs are current, workbook use-case columns are stale until
  re-run with Excel closed. Step 1 checks still pass.
- 2026-10-14 — Started a third `gh auth login --web`; fresh code given to owner.
- 2026-10-14 — Owner approved the GitHub device login: `gh` authenticated as the owner's account
  (token in Windows keyring; scopes gist, read:org, repo). No repo created yet (step 8). Plan: run
  `gh auth logout` after the step 8 push unless the owner says otherwise.
- 2026-10-14 — Rebuilt `accounts-XLSX.xlsx` with Excel closed: use-case columns now current (no
  `audio_analytics`; media_captions 193), owner banner intact, step 1 checks pass. Explained the
  step 2 approval ask to the owner.
- 2026-10-14 — Dry-ran draft weights (not saved) against capacity: leftovers EAST MM 155, EAST ENT
  88, CENTRAL MM 64, CENTRAL ENT 22, WEST MM 178; WEST ENT shortfall 35. Found ties at several
  cut-offs → proposed a deterministic tie-break. Found the D15 "Duplicate?" penalty applies to 0
  accounts (all resolved by merges). Wrote `docs/step3_scoring_proposal.md` and sent for approval.
- 2026-10-14 — **Step 3 built:** `pipeline/step3_route.py` (score, units with business units,
  capacity fill, tie-break, reasons, `new_book_size` in reps-XLSX via template-preserving writer),
  `pipeline/verify_step3.py` (17 independent checks: score recomputed from raw backup, region/segment,
  capacity, no score inversions, BUs with parents, every reason's quotes/numbers/industry grounded,
  no identical reasons, reps file untouched A–E). Workbook rebuilt with 6 step-3 columns + sheets
  `capacity` and `rep_books`.
- 2026-10-14 — Results: Priya 120/120 (155 left over, cut-off 45) · Marcus 200/200 (88, 33) · Dana
  165/165 (64, 30) · Luis 215/215 (22, 17) · Kenji 50/50 (178, 72) · Sam 195/230 (**shortfall 35**,
  0 left over). New books 260/260/260/260/260/225. 945 assigned, 507 left over, 0 pairs skipped.
- 2026-10-14 — Claude read a sample of reasons as a rep would and rewrote 4 wording issues (see
  self-corrections). Left-over quality check: Kenji's left-overs include 29 accounts with a
  speech-use-case note (26 scoring ≥60); other reps' left-overs have ≤1. Raised H1/H2 to owner.
- 2026-10-14 — D35/D36 confirm the current step 3 output; no code or output changes needed.
- 2026-10-14 — **Step 4 built:** `pipeline/step4_build_ui.py` → `web_ui/rep_books.html` (1.6 MB,
  all 2,020 rows embedded, no external scripts/fonts, works offline; light/dark; tabs: Overview,
  one per rep, Unassigned, Excluded & merged, Needs review, How it works; search + filters).
  `run.py` added at the repo root: runs steps 1–4 and all checks, stops on the first failure,
  opens the UI. Full run: all checks pass.
- 2026-10-14 — Tested the UI in headless Edge: first build rendered **nothing** — a JavaScript
  syntax error (one extra `)` in the capacity table). Found it with an error-capturing debug copy;
  fixed. Re-tested all 10 tabs: no errors; row counts match the data exactly (Priya 120, Kenji 50,
  Sam 195, Unassigned 507, Excluded & merged 568, flags 127). Screenshots checked at desktop width
  and inside a 390 px phone-width frame (fits; wide tables scroll inside their box).
- 2026-10-14 — **Step 5:** wrote `README.md` (manager paragraph incl. how to open the UI from GitHub,
  run instructions, repo map, results, clarifications by topic, owner's improvements, how it was
  built). Cross-checked every number in it against the pipeline outputs (labels, capacity table,
  check counts 17/17). Sent for approval; requested `/cost`.
- 2026-10-14 — **Step 6 (CSV):** `pipeline/step5_export_csv.py` (added to `run.py`) writes
  `output/accounts_final.csv` (2,020 × 47, UTF-8 BOM) and `output/reps_final.csv` (6 × 6), read
  straight from the workbooks. Verified: header and all 2,020 rows match the workbook cell-for-cell;
  `accounts.csv`/`reps.csv` byte-identical to the backups.
- 2026-10-14 — **Data problem found during CSV verification:** the original XLSX export has 4
  encoding-damaged cells — city "SÃ£o Paulo" (UTF-8 read as Latin-1) on ACC-100866, ACC-101061,
  ACC-101461, ACC-101507; `accounts.csv` has the correct "São Paulo". Nothing else differs between
  the XLSX and CSV exports. Added `fix_mojibake()` to `city_clean` with an Agent Note per row
  (original column untouched) and a permanent verify_step1 check (now 18). All 4 accounts were and
  remain excluded (Brazil, outside territory) — no routing impact. Full `run.py`: all checks pass.
- 2026-10-14 — Pre-publish review: no email address or credentials in any file; excluded the local
  `.claude/` settings folder via `.gitignore`. README updated for the CSVs and check counts. Repo
  size ~8 MB.
- 2026-10-14 — **Full pre-publish privacy scan** of all 39 publishable files incl. the XML inside
  every .xlsx. No passwords, tokens, credentials or email addresses. Found and fixed:
  (1) the owner's full name as author/last-editor in the metadata of all 4 workbooks → neutral
  values; both writers now always set neutral metadata; (2) the local folder path with the Windows
  user name in `Initial Prompt to Claude.md` (5×) → `C:\Users\<user>\...`, and inside the two backup
  workbooks (`absPath`) → removed; (3) the GitHub username in LOG.md (1×) and CLAUDE.md (2×) →
  "the owner's account"; (4) git had no identity set → repo-local identity "Account Routing Service"
  with GitHub's private noreply address, so no personal email can enter commit history.
- 2026-10-14 — True, unmodified originals copied to `private_originals/` (git-ignored, local only).
  `backup_originals/` now holds metadata-scrubbed copies whose cell data is verified identical to
  the true originals. Full `run.py` re-run: all checks pass.
- 2026-10-14 — Added `pipeline/check_publish_safety.py` (re-runnable: emails, personal paths, the
  local OS user name read at run time, tokens, secret words, person names in xlsx metadata).
  Positive control: planted an email, a personal path and an original workbook → 9 findings caught;
  removed them → 0 findings on the real repo (40 files).
- 2026-10-14 — First attempt to write this log entry failed (backslash escaping in an inline
  command); nothing was written; redone from a script file.
- 2026-10-14 — README: added the pre-publish scan instruction. Re-scan: 0 findings. Not pushed yet —
  reported the scan findings to the owner and asked for the explicit "push it" before publishing.
- 2026-10-14 — **Step 8 published:** final privacy scan 0 findings → initial commit `71e010b` (40
  files, author "Account Routing Service" with GitHub noreply address) → `gh repo create
  Account-Routing-Service --public` + push to `main`. Verified: visibility PUBLIC, description
  "Account Routing Service", remote commit == local commit, 40 files on GitHub, no
  `private_originals/`, `.claude/` or cache files published, repo page returns HTTP 200.
  URL: https://github.com/<owner>/Account-Routing-Service (owner = the owner's GitHub account).
- 2026-10-14 — This log entry pushed as a follow-up commit so the published LOG.md is current.
  `gh auth logout` NOT run — waiting for the owner's approval (D43).

## 6. File changes

- 2026-10-13 — Created `CLAUDE.md`, `LOG.md`.
- 2026-10-14 — Created `backup_originals/` (copies of all 4 inputs), `requirements.txt`,
  `.gitignore`, `pipeline/config.py`, `pipeline/step1_clean.py`, `pipeline/verify_step1.py`,
  `output/step1_accounts.json`.
- 2026-10-14 — **`accounts-XLSX.xlsx` modified** (regenerated from the backup each run): original
  columns A–L untouched (verified cell-by-cell); 25 green after-columns M–AK added (12 `_clean`
  copies + derived columns + Agent Notes); new sheets summary, exclusions, entities, hierarchy,
  review_flags, column_guide. `reps-XLSX.xlsx`, `accounts.csv`, `reps.csv` not touched.
- 2026-10-14 — `pipeline/step1_clean.py` (template-preserving writer, D22/D24 note wording),
  `pipeline/verify_step1.py` (banner-aware, +1 check), `accounts-XLSX.xlsx` regenerated (owner
  formatting kept). Added `docs/step2_classification_proposal.md`, `pipeline/use_case_schema.json`.
- 2026-10-14 — Added `pipeline/step2_classify.py`, `pipeline/step2_sample.py`,
  `pipeline/step2_handcheck.py`, `output/step2_use_cases.json`, `output/step2_handcheck_sample.json`.
  Changed `pipeline/use_case_schema.json` (audio_analytics), `pipeline/step1_clean.py` (use-case
  columns), `accounts-XLSX.xlsx` (regenerated; owner formatting preserved).
- 2026-10-14 — Added `output/step2_handcheck_blind_labels.json` (written by the sub-agent),
  `output/step2_handcheck_report.md`.
- 2026-10-14 — Added `docs/step3_scoring_proposal.md`.
- 2026-10-14 — Added `pipeline/step3_route.py`, `pipeline/verify_step3.py`,
  `output/step3_assignments.json`, `output/step3_capacity.json`. Changed `pipeline/step1_clean.py`
  (step 3 columns + `capacity`/`rep_books` sheets). **`reps-XLSX.xlsx` modified:** added
  `new_book_size` in column F; A–E (incl. `current_book_size`) untouched (verified).
  `accounts-XLSX.xlsx` regenerated (owner formatting kept).
- 2026-10-14 — Added `pipeline/step4_build_ui.py`, `run.py`, `web_ui/rep_books.html`.
- 2026-10-14 — Added `README.md`.
- 2026-10-14 — Added `pipeline/step5_export_csv.py`, `output/accounts_final.csv`,
  `output/reps_final.csv`. Changed `pipeline/step1_clean.py` (city repair), `pipeline/verify_step1.py`
  (+1 check), `run.py` (step 5), `README.md`, `.gitignore`; workbooks regenerated (formatting kept).
- 2026-10-14 — Changed `Initial Prompt to Claude.md` (paths obfuscated, owner-requested),
  `backup_originals/*.xlsx` (metadata only), `LOG.md`/`CLAUDE.md` (username removed),
  `pipeline/step1_clean.py` + `pipeline/step3_route.py` (neutral metadata), `.gitignore`
  (+`.claude/`, +`private_originals/`). Added `private_originals/` (local only),
  `pipeline/check_publish_safety.py`.
- 2026-10-14 — Git: initial commit `71e010b` on `main`, pushed to the public GitHub repo; follow-up
  commit for this log update.

## 7. Corrections caught by the owner

- 2026-10-14 — Owner asked what "excluding the notes" meant (Q10). Claude's wording was ambiguous;
  it meant excluding the accounts. Clarified.
- 2026-10-14 — Not an owner-caught error, but an owner-reversed decision: `audio_analytics` (D29)
  dropped after Claude pointed out it was outside the brief's label set.

## 8. Claude self-corrections

- 2026-10-13 — pandas/openpyxl not installed; used a stdlib XLSX reader instead of installing
  without permission.
- 2026-10-13 — `state = KA` (12 rows) looked like a Kansas typo but is Karnataka (Bangalore,
  India). Not mapped to CENTRAL.
- 2026-10-14 — **Wrong number in the 2026-10-13 message:** said "17 churned accounts still show
  spend". The actual count is **12** (7 April + 3 January + 2 February 2026). Code was unaffected.
- 2026-10-14 — First step-1 run flagged 13 "merge field conflicts" that were only `Unknown` vs. a
  real funding stage. `Unknown` is a placeholder, not a conflicting value; fixed so real values
  fill it instead and no false conflict is raised.
- 2026-10-14 — First step-1 run only flagged the "employee_count vs. ~N agents in notes" conflict on
  eligible accounts. 14 accounts excluded as under 20 employees have notes claiming 40–2,000 agents;
  now flagged too, since their exclusion rests on the contested number.
- 2026-10-14 — Avoided a wrong merge: naive domain matching would have merged 4 unrelated companies
  sharing `linkedin.com` and 3 sharing `twitter.com`.
- 2026-10-14 — Caught before re-running: the step 1 writer rebuilt the workbook from the backup,
  which would have silently wiped the owner's banner row and column widths. Fixed before any re-run.
- 2026-10-14 — Rough counts in a progress note ("~690 generic-only, ~570 with a use-case note")
  were off; exact counts are 783 no-signal (incl. 194 blank), 550 use-case, 63 speech-interest,
  56 "nothing audio". Also "31 distinct notes" corrected to 30 templates (two "~N agents" forms are
  one template). Proposal doc corrected before sending.
- 2026-10-14 — Log/CLAUDE.md were behind by the last few actions when the owner asked; brought
  current. Will update both before ending each turn from now on.
- 2026-10-14 — First reasons draft, caught on Claude's own read-through: (1) accounts tied at the
  cut-off said only "book is full (lowest assigned score 45)" while scoring 45 → now say they lost
  the tie-break; (2) ", Unknown." for unknown funding → "funding stage unknown"; (3) no-signal
  reasons now quote the actual note or say "no notes on file"; (4) business-unit reasons now state
  the parent's score they are ranked on. Verifier extended to catch (2) and (4).
- 2026-10-14 — Verifier bug: its number pattern read "100," (with the comma) from "47/100," and
  flagged 5 correct reasons. Fixed the pattern; not a reason error.
- 2026-10-14 — Web UI first build had a JavaScript syntax error (extra `)`), so the page would have
  opened blank. Caught by Claude's headless-browser test before handing over; fixed and re-tested.
- 2026-10-14 — A phone-width screenshot looked cut off; confirmed it was headless Edge's minimum
  window width (re-tested inside a 390 px frame: layout fits). No change needed.
- 2026-10-14 — **Missed in step 1, caught in step 6:** the "SÃ£o Paulo" encoding damage in the XLSX.
  During the very first profiling (2026-10-13) the city printed as "S�o Paulo" and Claude put that
  down to the terminal's encoding instead of checking the data. Found when the CSV cross-check
  against `accounts.csv` disagreed on 4 cells. Fixed in the cleaned column + new automated check.

## 9. Scoring / judgment calls on accounts that were wrong

_None yet._

## 10. Cost (tokens and dollars)

- 2026-10-14 — **Step 1 checkpoint `/cost` (pasted by owner, verbatim figures):**
  Total cost $0.0000 · API duration 0s · wall duration 5h 4m 42s · code changes 0 added / 0 removed
  · usage 0 input, 0 output, 0 cache read, 0 cache write tokens. Current session 0% used; current
  week (all models) 1% used, resets Oct 20, 10am (America/Chicago). Usage credits off. Plugin
  skill-listing footprint ~143 tok/turn. "27% of your usage went to always-on context over 40k
  tokens" (last 24h, all local sessions).
  - **Caveat (Claude):** the $0 / 0-token figures cannot be this session's real usage — Claude made
    many model calls and wrote ~700 lines of code in it. The counters most likely reset when the
    session was resumed/restarted, and/or the account is on a subscription plan where `/cost` does
    not track per-session dollars. Treat this reading as "not measured". The weekly figure (1% of
    the weekly limit) is the only usable usage signal so far. Claude will flag this again at the
    next checkpoint so the next reading can be compared against this one.
  - First paste attempt (same day) arrived empty; owner re-pasted.
- 2026-10-14 — **Step 2 pre-run checkpoint `/cost` (pasted by owner, verbatim figures):**
  Total cost **$2.82** · API duration 4m 59s · wall duration 6h 50m 24s · code changes 239 lines
  added, 11 removed · claude-opus-5-5: 1.8k input, 27.6k output, 4.6m cache read, 167.3k cache write
  tokens ($2.82). Current session 8% used (resets 11pm America/Chicago); current week (all models)
  2% used (resets Oct 20, 10am America/Chicago). Usage credits off. Last-24h notes: 59% of usage at
  >150k context; 25% went to always-on context over 40k tokens.
  - **Interpretation (Claude):** the previous reading was $0 right after a session restart, so
    **$2.82 ≈ the cost of the work between the two readings**: preserving the owner's workbook
    formatting, D21–D25 updates, `gh` install, step 2 profiling + proposal, and log upkeep. Work
    done before the restart (planning, step 0, first build of step 1) was **not measured** by
    `/cost`. Known cumulative so far: **$2.82 + an unmeasured pre-restart amount**. The weekly bar
    moved 1% → 2%.
  - This $2.82 is the **"before" baseline for step 2**; the classification run + hand check will be
    measured as (next reading − $2.82), unless the session restarts again in between.
  - Cost tip from `/cost` noted (long context costs more); Claude will keep turns compact.
- 2026-10-14 — **Step 2 "after" checkpoint `/cost` (pasted by owner, verbatim figures):**
  Total cost **$5.19** · API duration 9m 38s · wall 7h 45m 11s · code changes 581 added / 11
  removed · claude-opus-5-5: 3.5k input, 54.5k output, 10.6m cache read, 270.8k cache write tokens
  ($5.19) · prompt cache: 22 requests, 99% of input from cache, no misses. Current session 14% used
  (resets 11pm America/Chicago); current week 3% used (resets Oct 20, 10am). Last 24h: 100% of usage
  from subagent-heavy sessions; general-purpose subagents 5% of usage; 69% at >150k context; 21% to
  always-on context >40k tokens.
  - **Step 2 cost = $5.19 − $2.82 = $2.37** (same session, no restart in between). This covers
    the whole step: building the classifier/validator/sampler/report scripts, the run itself, the
    blind sub-agent hand check (68k sub-agent tokens; ~5% of the day's usage per `/cost`), two
    GitHub login attempts, and log upkeep. The classification run itself is a deterministic script,
    so re-running it costs ~$0 in tokens; nearly all of the $2.37 is design, verification and
    documentation.
  - Running total measured by `/cost`: **$5.19** (+ unmeasured pre-restart work, see first entry).
  - Note from `/cost`: consider a cheaper model for simple sub-agents. Claude will propose that for
    any future sub-agent work instead of defaulting to Opus.
- 2026-10-14 — **Step 3 baseline `/cost` (pasted by owner, verbatim figures):** Total cost **$6.76**
  · API duration 12m 43s · wall 8h 14m 53s · code changes 655 added / 11 removed · claude-opus-5-5:
  5.8k input, 71.0k output, 15.9m cache read, 291.9k cache write tokens ($6.76) · prompt cache: 38
  requests, 99% from cache, no misses. Current session 17% used (resets 11pm America/Chicago);
  current week 4% used (resets Oct 20, 10am). Last 24h: 100% of usage from subagent-heavy sessions
  (general-purpose subagents 4%); 75% at >150k context; 20% to always-on context >40k tokens.
  - **Since the last reading: $6.76 − $5.19 = $1.57** — D29 relabel (audio_analytics →
    media_captions) + hand-check re-score, GitHub login (third code, success) + the owner's
    question about token access, workbook rebuild, step 2 approval explanation, and the step 3
    scoring proposal with dry run, plus log upkeep. Charged to the step 2 wrap-up / step 3 proposal.
  - **Step 3 baseline = $6.76**; the step 3 build will be measured as (next reading − $6.76).
  - Running total measured by `/cost`: **$6.76** (+ unmeasured pre-restart work).
- 2026-10-14 — **Step 3 "after" `/cost` (pasted by owner, verbatim figures):** Total cost **$8.20**
  · API duration 16m 7s · wall 8h 23m 15s · code changes 1,011 added / 12 removed ·
  claude-opus-5-5: 6.3k input, 93.8k output, 19.7m cache read, 321.0k cache write tokens ($8.20) ·
  prompt cache: 51 requests, 99% from cache, no misses. Current session 21% used (resets 11pm
  America/Chicago); current week 4% used (resets Oct 20, 10am). Last 24h: 100% of usage from
  subagent-heavy sessions (general-purpose subagents 3%); 79% at >150k context; 19% to always-on
  context >40k tokens.
  - **Step 3 cost = $8.20 − $6.76 = $1.44** — scoring/routing script, independent verifier (17
    checks), reason read-through and 4 wording fixes, verifier bug fix, reps-XLSX `new_book_size`,
    workbook rebuild, left-over analysis, log upkeep. No sub-agents used in step 3.
  - Running total measured by `/cost`: **$8.20** (+ unmeasured pre-restart work).
  - Per-step so far: step 2 $2.37 · step 2 wrap-up + step 3 proposal $1.57 · step 3 build $1.44.
- 2026-10-14 — **Step 4 "after" `/cost` (pasted by owner, verbatim figures):** Total cost **$10.32**
  · API duration 20m 15s · wall 8h 38m 47s · code changes 1,324 added / 12 removed ·
  claude-opus-5-5: 7.9k input, 119.4k output, 26.2m cache read, 358.0k cache write tokens ($10.32)
  · prompt cache: 70 requests, 99% from cache, no misses. Current session 26% used (resets 11pm
  America/Chicago); current week 5% used (resets Oct 20, 10am). Last 24h: 100% of usage from
  subagent-heavy sessions (general-purpose subagents 3%); 83% at >150k context; 18% to always-on
  context >40k tokens.
  - **Since the last reading: $10.32 − $8.20 = $2.12** — logging D35/D36, step 3 approval exchange,
    and the step 4 build: UI builder, `run.py`, full pipeline run, headless-Edge testing (blank-page
    bug found and fixed), screenshots, log upkeep. No sub-agents used.
  - Running total measured by `/cost`: **$10.32** (+ unmeasured pre-restart work).
  - Per-step so far: step 2 $2.37 · step 2 wrap-up + step 3 proposal $1.57 · step 3 build $1.44 ·
    step 3 decisions + step 4 build $2.12.
- 2026-10-14 — **Step 5 "after" `/cost` (pasted by owner, verbatim figures):** Total cost **$11.29**
  · API duration 21m 57s · wall 8h 53m 51s · code changes 1,524 added / 12 removed ·
  claude-opus-5-5: 9.0k input, 130.1k output, 29.5m cache read, 370.4k cache write tokens ($11.29)
  · prompt cache: 77 requests, 99% from cache, no misses. Current session 28% used (resets 11pm
  America/Chicago); current week 5% used (resets Oct 20, 10am). Last 24h: 100% of usage from
  subagent-heavy sessions (general-purpose subagents 2%); 85% at >150k context; 18% to always-on
  context >40k tokens.
  - **Since the last reading: $11.29 − $10.32 = $0.97** — step 4 approval logging, README questions,
    writing `README.md`, cross-checking its numbers, log upkeep. No sub-agents used.
  - Running total measured by `/cost`: **$11.29** (+ unmeasured pre-restart work).
  - Per-step so far: step 2 $2.37 · step 2 wrap-up + step 3 proposal $1.57 · step 3 build $1.44 ·
    step 3 decisions + step 4 build $2.12 · step 5 README $0.97 (everything before the first
    $0.00 reading — planning, step 0, first step 1 build — unmeasured).
- 2026-10-14 — **Step 6 "after" `/cost` (pasted by owner, verbatim figures):** Total cost **$12.74**
  · API duration 24m 4s · wall 9h 9m 16s · code changes 1,595 added / 13 removed ·
  claude-opus-5-5: 10.1k input, 144.0k output, 34.5m cache read, 389.2k cache write tokens ($12.74)
  · prompt cache: 89 requests, 99% from cache, no misses. Current session 31% used (resets 11pm
  America/Chicago); current week 5% used (resets Oct 20, 10am). Last 24h: 100% of usage from
  subagent-heavy sessions (general-purpose subagents 2%); 86% at >150k context; 17% to always-on
  context >40k tokens.
  - **Since the last reading: $12.74 − $11.29 = $1.45** — step 5 approval logging, F1–F4 questions,
    CSV export script, cell-for-cell verification, finding and fixing the "SÃ£o Paulo" encoding
    damage (+ new check, full re-run), pre-publish review, README/log upkeep. No sub-agents used.
  - Running total measured by `/cost`: **$12.74** (+ unmeasured pre-restart work).
  - Per-step so far: step 2 $2.37 · step 2 wrap-up + step 3 proposal $1.57 · step 3 build $1.44 ·
    step 3 decisions + step 4 build $2.12 · step 5 README $0.97 · step 6 CSV + data fix $1.45.

