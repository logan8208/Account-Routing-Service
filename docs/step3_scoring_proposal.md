# Step 3 — Fit score and routing: proposal (pending owner approval)

Proposed 2026-10-14. Nothing has been scored or assigned yet.

## Fit score (0–100), from the rules.md fit signals

| Signal (rules.md) | Points | Why this weight |
|---|---|---|
| **Notes name a speech use case** (calls, recordings, transcription, captions, voice agents, meetings, IVR) | **35** | rules.md calls it "a strong signal", and it is the only signal about *this* company's actual project. Biggest weight. |
| Notes show speech interest but no use case (Speech ML job post, own STT, internal speech team) | 20 | Real but less specific interest. |
| Buying-intent bonus: inbound demo request in 2025/2026, or "evaluating several vendors" | +5 | Not in rules.md; a small nudge for recent intent. **Q1** |
| **Industry** in the win list (Healthcare, Contact Center Software, Conversation Intelligence, Telephony/CPaaS, EdTech, Media & Entertainment, Legal Tech, Insurance, Sales Tech) | **25** | "Where we win"; second-strongest. |
| Industry not in the list | 5 | "Possible but rarer" — not zero. |
| **Size** 200–10,000 employees | **20** | "Bigger is better, up to a point." |
| Size 50–199 | 12 | |
| Size 20–49 | 6 | |
| Size over 10,000 | 8 | "Slow and usually already have a vendor" — below mid-size, above small. |
| Size unknown (blank) | 4 | D11 small penalty. |
| **Funding** year 2025 or 2026 | **15** | "Recent funding means budget" (D14). |
| Funding year 2024 | 8 | D14 partial credit. |
| Older or unknown funding | 0 | |
| "Duplicate?" note with no duplicate found | −5 | D15. *In this data every "Duplicate?" note was resolved by a merge, so it applies to 0 accounts.* |
| "Not yet qualified" partner referral | 0 | D15 neutral. |

Max 100. Notes + industry together (60) outweigh size + funding (35): a mid-size healthcare company
with a telehealth note beats a large, freshly funded company with no speech need.

## Routing (rules.md + D16, D21, D25)

- Pool = eligible companies with the rep's region + segment. Room = 260 − current book
  (120 / 200 / 165 / 215 / 50 / 230).
- Highest score first until the room is full; the rest are **left over** (reported, shown in the UI
  as "unassigned — over capacity" with their score). A rep with room after the pool runs out is
  **not** filled from another region (shortfall reported).
- Business units (D25): routed with their parent into the parent's region/segment pool, ranked by
  the **parent's** score, and take one slot each. Parent in → child in; parent out → child out.
- **Tie-break** at the cutoff (scores are whole numbers, so ties happen): higher use-case
  confidence → more employees (within ≤10,000) → more recent funding → lower account_id.
  Deterministic, so a re-run gives the same books. **Q2**

## Dry run of these weights (not saved)

| Pool | Eligible | Room | Result | Cut-off score |
|---|---|---|---|---|
| EAST Mid-Market (Priya) | 275 | 120 | 155 left over | 45 |
| EAST Enterprise (Marcus) | 288 | 200 | 88 left over | 32 |
| CENTRAL Mid-Market (Dana) | 229 | 165 | 64 left over | 30 |
| CENTRAL Enterprise (Luis) | 237 | 215 | 22 left over | 17 |
| WEST Mid-Market (Kenji) | 228 | 50 | 178 left over | 72 |
| WEST Enterprise (Sam) | 195 | 230 | **35 shortfall** | — (all assigned) |

(Pool counts already include the 14 business units moved into their Enterprise parents' pools.)

## Reasons a rep reads

Every assigned (and left-over) account gets a 1–3 sentence reason built only from that account's
own fields, e.g.:

> "Telehealth platform; clinicians want ambient note-taking from patient visits (notes). Healthcare,
> 1,220 employees, Seed round in 2026. Score 95 — #3 of 237 in CENTRAL Enterprise."

A script will check every reason against the account's data (each number, industry, year and
quoted note must match) before you see it.

## Questions for the owner

- **Q1:** keep the +5 buying-intent bonus (demo request 2025/26, evaluating vendors), or drop it to
  stick strictly to rules.md's list? Recommended: keep.
- **Q2:** OK with the tie-break order above?
- **Q3:** a parent + business unit need 2 slots. If only 1 slot is left when the parent's turn
  comes, recommended: skip that pair (both left over) and fill the slot with the next account, so
  the book is exactly full. Alternative: let the book go 1 over 260.
- **Q4:** any weight you want changed?
