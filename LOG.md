# Project Log — Account Routing Service

The short record of how this was built: who did what, every decision, what went wrong and how it
was caught, and what it cost. All dates are 2026-10-13/14. Decision IDs (D1–D43) are cited in the
code comments. Full technical detail lives in `CLAUDE.md` and the `docs/` folder.

## 1. AI tools used

- **Claude Code** (terminal CLI on Windows), model **Claude Opus 5.5**, for everything.
- **One Claude sub-agent**, used as an independent *blind* second labeller for the use-case hand
  check (68k tokens).
- No API key. All AI work ran inside the Claude Code session. No other AI tools.
  (Headless Microsoft Edge was used only to render-test the web UI.)

## 2. Delegation: what Logan kept, what Claude did

| Logan kept | Delegated to Claude |
|---|---|
| Approving each step after testing it | Reading the brief and data; asking clarifying questions; the plan |
| Every rule interpretation (D1–D43) | All code: cleaning, de-duplication, eligibility, classification, scoring, routing |
| Formatting the workbook by hand (banner row, column widths) | Verification scripts and hand checks; reporting error rates |
| Approving the GitHub sign-in in the browser | Web UI, README draft, CSV export |
| The README's "what I would add with another day" list | GitHub setup (D27): `gh` install, repo creation, push |
| Pasting `/cost` at each checkpoint | Keeping `LOG.md` / `CLAUDE.md` current |
| Deciding when to run `gh auth logout` (D43) | The pre-publish privacy scan |

## 3. Logan's prompts and plans (short)

- **Brief** (`Initial Prompt to Claude.md`): clean ~2,000 CRM accounts, merge duplicates, exclude
  ineligible accounts with reasons, classify the use case (approved schema, measured error rate and
  cost), score and route to 6 reps per `rules.md` with grounded reasons, build a local web UI, write
  a README, ship it in a GitHub repo. Create CLAUDE.md first, keep this log, get approval before
  every step.
- **Claude's plan** (approved): 0 setup → 1 clean → 2 classification schema → 3 classify + hand
  check → 4 scoring weights → 5 route → 6 web UI → 7 README → 8 CSV, log, GitHub.
- Short instructions from Logan, verbatim or near-verbatim:
  - "Before any action you take, make sure I have tested and approved what you did in the previous step."
  - "Make [the after-columns] a different color … also have an Agent Notes column."
  - "Keep the current_book_size column unedited and add a new_book_size."
  - "Tell me to paste /cost whenever you need … Don't continue working til I do so."
  - "If there are any accounts … that are tricky and you need me as a human in the loop … let me know."
  - "step 2 approved" · "step 3 approved" · "step 5 approved" · "push it"
  - "The UI html looks great. No need to implement Github Pages."
  - "Ask me when you should run gh auth logout and don't do it til I approve."
  - Final round: shorter README paragraphs, cost summary and LOG link in the README, a final check
    against all instructions, and a much shorter LOG.

## 4. Decisions (rule interpretations by Logan)

**Eligibility:** any spend > $0 = customer, even when the notes say churned (D6, D7) · shut down /
parked / acquired = no longer exists (D9) · competitor = core product is a speech engine (D10) ·
blank employee count stays eligible with a small penalty (D11) · employee count trusted over agent
counts in notes; 14 tiny call centers stay excluded but flagged (D12, D24) · blank state filled from
the city only when unambiguous, flagged for enrichment (D13).

**Duplicates and hierarchies:** same company = merge, and spend on any record makes it a customer;
billing domains, self-serve signups and product brands are the same company (D8, D23) · business
units stay separate, go to the parent's rep, take one slot and move with the parent; business units
of customers stay with account management (D8, D21, D25) · LinkedIn/Twitter URLs never used to merge
(D22).

**Use case:** exactly the brief's 8 labels · no speech signal → `none` (D26) · podcasts and lecture
capture → `media_captions` (D28) · dispatch radio/phone → `media_captions` (D29, revised from
`audio_analytics`) · speech interest only → industry's use case if clear, else `other` (D30).

**Scoring and routing:** funding 2025–26 full credit, 2024 partial (D14) · "Duplicate?" penalty only
if unresolved; "not yet qualified" neutral (D15) · room = 260 − current book (D16, D36) · +5
buying-intent bonus; weights as proposed (D31, D34) · tie-break: confidence → size → funding year →
ID (D32) · a parent + business unit pair that doesn't fit is skipped (D33) · Sam's 35 empty slots are
left empty and reported (D35).

**Delivery:** after-columns in green with Agent Notes; originals never edited (D4) · original CSVs
untouched (D1, D40) · web UI as one offline file in the repo, no GitHub Pages (D18, D37) · one final
CSV + reps CSV (D38, D39) · public repo `Account-Routing-Service` (D19, D41) · privacy scan before
publishing; paths and usernames obfuscated (D42) · no `gh auth logout` without approval (D43).

## 5. What was done (one line per step)

0. **Setup:** pandas + openpyxl, git, untouched backups of all inputs.
1. **Clean:** 2,020 rows → 1,965 companies (55 merged) → 513 excluded with reasons, 1,452 eligible.
   18 automated checks.
2. **Classify:** schema approved, 1,452 labelled. Blind hand check of 150: 0 errors (95% CI 0–2.5%).
3. **Score and route:** 945 assigned (five books at 260, Sam at 225), 507 left over. 17 checks,
   including every reason audited against its account's own data.
4. **Web UI:** single offline HTML file. All 10 tabs render-tested; counts match the data.
5. **README:** written from Logan's answers.
6. **CSV:** `output/accounts_final.csv` and `output/reps_final.csv`, matching the workbooks cell for cell.
7. **Publish:** privacy scan, public repo, pushed and verified.
8. **Final check:** every instruction checked (`docs/final_check.md`); 19 more rule checks
   (`pipeline/verify_rules.py`); 54 automated checks in total, all passing.

**Key file changes:** `accounts-XLSX.xlsx` and `reps-XLSX.xlsx` gained new columns and sheets
(originals untouched) · `Initial Prompt to Claude.md` had its folder paths obfuscated · backup
workbooks had their metadata scrubbed (cell data verified identical; true originals kept locally in
the git-ignored `private_originals/`).

## 6. Where Claude got it wrong, and how it was caught

**Caught by Logan**
- **No privacy scan before publishing.** Logan asked whether Claude had scanned for personal
  data. It hadn't. The scan then found Logan's full name in the metadata of all 4 workbooks,
  the local folder path (5× in the brief, plus inside 2 workbooks) and the GitHub username in the
  log. All fixed before the push, and `pipeline/check_publish_safety.py` added.
- **Log fell behind.** Logan asked "are claude.md and the log updated?" They weren't fully. Fixed,
  and a standing rule added: update both before ending every turn.
- **Ambiguous wording.** Claude wrote "excluding the notes" and meant "excluding the accounts". Logan
  asked; Claude clarified.
- **Hard-to-read output.** The README paragraphs were too dense and the log too long (this final
  round). Both rewritten.

**Caught by Claude (before Logan saw the result)**
- Would have wiped Logan's hand formatting on re-run. Fixed so the workbook is used as a template.
- Said "17 churned accounts". It was 12. Also gave rough note counts that were off; corrected before
  the proposal was sent.
- Wrongly flagged "Unknown vs Seed" as a merge conflict (13 false flags). Fixed.
- First draft of the reasons: unclear on tie-breaks, a bare "Unknown", and business units not naming
  the parent's score. Rewritten; the checker extended.
- The web UI's first build opened blank (one extra `)` in the JavaScript). Caught by a headless
  browser test.
- **Missed in step 1, caught in step 6:** "SÃ£o Paulo" encoding damage in 4 cells. It had been seen
  early and blamed on the terminal. Fixed, with a permanent check (no routing impact: the accounts are
  in Brazil).
- In this final round, the README first said 53 automated checks; the real count is 54. Fixed
  before sending.
- Avoided wrong merges: 7 unrelated companies sharing `linkedin.com` / `twitter.com`. `KA` is
  Karnataka (India), not Kansas.

**Decision Logan reversed (not an error):** `audio_analytics` was added at Logan's request; Claude
pointed out it isn't one of the brief's 8 labels; Logan switched it to `media_captions`.

## 7. Scoring and assignment calls Logan changed

None. Logan kept every proposed weight and routing rule (D31–D36). The open questions on Sam's
shortfall and Kenji's 50 slots were decided as recommended.

## 8. Cost

Measured with Claude Code's `/cost`, pasted by Logan at each checkpoint. The session restarted
once early on, so the first part (planning, setup, first build of step 1) wasn't measured.

| Stage | Cost |
|---|---|
| Planning, step 0, first step 1 build | not measured |
| Step 1 fixes and step 2 proposal | $2.82 |
| Step 2 classification and blind hand check | $2.37 |
| Step 2 wrap-up and step 3 proposal | $1.57 |
| Step 3 scoring and routing | $1.44 |
| Step 3 decisions and step 4 web UI | $2.12 |
| Step 5 README | $0.97 |
| Step 6 CSV and encoding fix | $1.45 |
| Privacy review and publish | $2.13 |
| **Total measured (as of the last reading)** | **$14.87**: about 164k output tokens and 42M cached-input tokens; about 6% of the weekly plan limit |

This final round (README and log rewrite, final check) comes on top of that figure.
