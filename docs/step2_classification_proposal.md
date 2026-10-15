# Step 2 — Use-case classification: proposal (pending owner approval)

**Status: APPROVED 2026-10-14 with owner changes** — D26 Option B (no signal → none), D28 podcasts/lecture → media_captions, D29 dispatch → new label `audio_analytics`, D30 speech-interest rule as proposed. Implemented in `pipeline/step2_classify.py`.

## Scope

The 1,452 eligible companies from step 1, one label each (on the entity's primary record), using
that company's notes (all merged records' notes combined) and its industry. Excluded and merged
rows get no label.

## Output schema

`pipeline/use_case_schema.json` — one JSON record per account:

| Field | Values | Purpose |
|---|---|---|
| `account_id` | `ACC-######` | |
| `use_case` | call_analytics · voice_agent · meeting_notes · media_captions · clinical_documentation · legal_transcription · other · none | The one label. |
| `evidence_source` | notes · notes+industry · industry · no_signal | What the label rests on. |
| `evidence` | verbatim text | The exact note and/or industry value used. A script checks it really appears in that account's data, so no label can rest on invented text. |
| `confidence` | high · medium · low | |
| `rationale` | ≤ 200 chars | One sentence a rep can read; reused in the step 5 reasons. |
| `needs_review` | true/false | Ambiguous mapping or low confidence. |

## Label definitions

| Label | Means the account wants speech-to-text for… |
|---|---|
| call_analytics | recorded/live phone calls analysed after or during the call: QA scoring, call summaries, agent assist, sales coaching, voice-of-customer |
| voice_agent | a real-time conversational voice bot or IVR that talks to callers |
| meeting_notes | meetings recorded and turned into transcripts/notes |
| media_captions | published audio/video: captions, subtitles, dubbing, podcasts, lectures |
| clinical_documentation | clinician–patient conversations turned into clinical notes |
| legal_transcription | depositions, hearings, legal proceedings |
| other | a clear speech/transcription need that fits none of the above |
| none | no evidence of any speech/transcription need |

## Method (recommended)

The notes field is templated: the 1,452 eligible companies use only **30 distinct note templates** (ignoring the year or agent count inside a note; plus 14
"Business unit of X" notes and blanks). So Claude (this session, no API key) reads each distinct
note once and decides its label, and that decision table is applied to every account by a script
(`pipeline/step2_classify.py`), which emits schema-validated JSON plus the grounding check.

Why not have the LLM read all 1,452 accounts one by one: every account with the same note would get
the same answer anyway, so per-account calls cost ~50× more tokens and add the risk of the model
labelling two identical notes differently. The table is the LLM judgment, written down where a
person can review and change it, and free to re-run.

Precedence for each account:
1. A note that names a use case → that label (`notes`, high confidence).
2. A note that shows speech interest but no use case (Speech ML job post, own STT, internal speech
   team) → industry decides if it is one of the industries below, else `other` (`notes+industry`,
   medium).
3. No speech signal in any note → **owner decision A or B below**.

## Proposed note → label table (counts = eligible companies)

| Note (as written) | # | Label | Confidence |
|---|---|---|---|
| Records inbound support calls; evaluating vendors for call transcription and QA scoring. | 38 | call_analytics | high |
| Voice-of-customer analytics across chat, email and calls. | 45 | call_analytics | high |
| Sales coaching product built on call recordings. Uses a competitor's API today. | 31 | call_analytics | high |
| Contact center with ~N agents. Interested in real-time agent assist. | 43 | call_analytics | high |
| Insurance claims intake via phone; wants call summaries pushed to the claims system. | 29 | call_analytics | high |
| Building an AI voice agent for appointment scheduling. Currently on a Twilio stack. | 42 | voice_agent | high |
| IVR modernization project scoped for next fiscal year. | 30 | voice_agent | high |
| Product has a meeting recorder feature; transcription is a core workflow. | 33 | meeting_notes | high |
| Streaming captions for live events. | 41 | media_captions | high |
| Video platform adding captions and dubbing for creators. | 41 | media_captions | high |
| Runs a podcast network; wants automated show notes and searchable transcripts. | 31 | media_captions | medium — **Q-C** |
| Lecture capture product for universities; needs multilingual transcription. | 29 | media_captions | medium — **Q-C** |
| Telehealth platform. Clinicians want ambient note-taking from patient visits. | 36 | clinical_documentation | high |
| Legal deposition and hearing recordings; accuracy on proper nouns is the sticking point. | 37 | legal_transcription | high |
| Dispatch and driver communication over radio and phone; exploring transcription. | 44 | other | medium — **Q-D** |
| Job posting for a 'Speech ML Engineer' seen in YYYY. | 58 | rule 2 (industry or other) | medium |
| Built their own STT in YYYY, reportedly looking to replace it. | 3 | rule 2 | medium |
| Has an internal speech team but buys transcription for scale. | 2 | rule 2 | medium |
| Website mentions AI features but nothing audio-specific. | 56 | none (explicitly no audio) | high |
| Hiring for customer support leadership · Referral from a partner · Met at a conference booth · Inbound demo request · No recent activity · Marketing-sourced lead · Evaluating several vendors · Recently expanded into the US market · Duplicate? · Created by a rep manually · Imported from a conference list · Business unit of X · (blank) | 783 | rule 3 | — |

Notes always beat industry when they disagree (e.g. "Streaming captions for live events" at a
Contact Center Software company → media_captions), because the note describes this company's
actual project; the industry is a vendor guess.

Industry → label table (used by rule 2, and by rule 3 only under Option A):
Healthcare → clinical_documentation · Legal Tech → legal_transcription · Contact Center Software,
Conversation Intelligence, Sales Tech, Insurance → call_analytics · Telephony / CPaaS → voice_agent
· Media & Entertainment, EdTech → media_captions · anything else → (rule 2: other; rule 3: none).

## Decisions needed from the owner

- **Q-A/B (biggest one, 783 accounts): no speech signal in the notes.**
  - **Option B (recommended): `none`.** An industry is not a use case. Labelling a Healthcare
    company "clinical_documentation" with nothing in its notes would put an invented project into
    the rep-facing reason. Industry is still credited separately in the step 4 score, so we would
    not lose that signal (and would not count it twice).
  - Option A: use the industry table (`industry`, low confidence, needs_review = true); `none` only
    for industries not in the table.
- **Q-C:** podcasts and lecture capture → `media_captions` (published media) rather than
  `meeting_notes`? Recommended: media_captions.
- **Q-D:** dispatch radio/phone transcription → `other` (radio dispatch is not call analytics) or
  `call_analytics`? Recommended: other.
- **Q-E:** the speech-interest notes (63 accounts) → rule 2 as above? Recommended: yes.

## Verification (after the run)

1. **Script checks on 100% of accounts:** schema-valid JSON, one label each, evidence text really
   present in that account's notes/industry, counts reconcile to 1,452.
2. **Hand check, measured error rate:** a stratified random sample of **150 accounts** that covers
   every distinct note (≥3 accounts each) plus blank/generic notes. Each is labelled **blind** by an
   independent Claude sub-agent given only the raw notes, industry and label definitions (it never
   sees my labels). Claude then adjudicates every disagreement by re-reading the account and records
   which side was wrong. Reported: error rate with a 95% confidence interval, sample size, the
   errors themselves, and a per-note view (one wrong table row repeats across every account with
   that note, so errors are also reported by note).
   *Limitation:* both labellers are Claude, so shared blind spots are possible — your ground-truth
   comparison is the real test.
3. **Cost:** I will ask you for `/cost` right before and right after the run (and the hand check),
   and report the difference.
