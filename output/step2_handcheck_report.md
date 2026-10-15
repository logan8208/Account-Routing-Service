# Step 2 hand check — measured error rate

- Sample: **150** of 1452 eligible companies, stratified so every one of the 47 note templates is checked (fixed seed, `pipeline/step2_sample.py`).
- Method: an independent Claude sub-agent labelled the sample **blind** (raw notes + industry + the owner-approved label rules only; it never saw Claude's labels or table). Every disagreement was then re-read and adjudicated by Claude.
- Raw agreement between the two labellers: **150/150 = 100.0%**.
- **Claude's measured error rate: 0/150 = 0.0%** (95% Wilson CI 0.0%–2.5%).
- Weighted to the full population by note template: **0.0%**.
- Limitation: both labellers are Claude, so shared blind spots are possible. The owner's ground-truth comparison is the real test.

## What this error rate does and does not measure

It measures whether each company got the label the **owner-approved rules** give it (reading the notes correctly, applying precedence, no typos or table mistakes). It does **not** test whether the rules themselves match the ground truth, because the blind labeller was given the same rules. If the ground truth differs, it will most likely be in these policy calls, not in reading individual notes:

- D26: 783 companies with no speech signal → `none` (ground truth might use industry).
- D29: 44 dispatch radio/phone companies → `media_captions` (owner's call; a loose fit, since dispatch audio is not published media — ground truth may say `other` or `call_analytics`). The blind labeller used `audio_analytics` for these before the owner changed the rule; that label name was re-mapped (`POLICY_RELABEL`), not re-judged.
- D28: 60 podcast / lecture-capture companies → `media_captions` (could be `meeting_notes`).
- D30: 63 speech-interest-only companies → industry-implied label or `other`.
- 56 "website mentions AI features but nothing audio-specific" → `none`.

## Disagreements and rulings

| account | industry | notes | Claude | blind | correct | ruling |
|---|---|---|---|---|---|---|
| — | | | | | | none |

## Per note template

| template | in sample | Claude errors | companies in population |
|---|---|---|---|
| (blank) | 8 | 0 | 194 |
| Referral from a partner. Not yet qualified. | 6 | 0 | 82 |
| Met at a conference booth. Interest unclear. | 3 | 0 | 72 |
| Marketing-sourced lead. Downloaded a whitepaper. | 5 | 0 | 71 |
| No recent activity. | 6 | 0 | 69 |
| Hiring for customer support leadership. | 4 | 0 | 68 |
| Inbound demo request in #; no follow-up recorded. | 5 | 0 | 68 |
| Evaluating several vendors; no decision maker identified. | 4 | 0 | 67 |
| Recently expanded into the US market. | 5 | 0 | 65 |
| Job posting for a 'Speech ML Engineer' seen in #. | 4 | 0 | 58 |
| Website mentions AI features but nothing audio-specific. | 5 | 0 | 54 |
| Voice-of-customer analytics across chat, email and calls. | 4 | 0 | 44 |
| Dispatch and driver communication over radio and phone; exploring transcription. | 4 | 0 | 43 |
| Building an AI voice agent for appointment scheduling. Currently on a Twilio stack. | 4 | 0 | 42 |
| Contact center with ~# agents. Interested in real-time agent assist. | 5 | 0 | 42 |
| Streaming captions for live events. | 5 | 0 | 41 |
| Video platform adding captions and dubbing for creators. | 4 | 0 | 41 |
| Records inbound support calls; evaluating vendors for call transcription and QA scoring. | 4 | 0 | 38 |
| Legal deposition and hearing recordings; accuracy on proper nouns is the sticking point. | 4 | 0 | 37 |
| Telehealth platform. Clinicians want ambient note-taking from patient visits. | 4 | 0 | 36 |
| Product has a meeting recorder feature; transcription is a core workflow. | 5 | 0 | 32 |
| IVR modernization project scoped for next fiscal year. | 3 | 0 | 30 |
| Runs a podcast network; wants automated show notes and searchable transcripts. | 4 | 0 | 30 |
| Sales coaching product built on call recordings. Uses a competitor's API today. | 4 | 0 | 30 |
| Insurance claims intake via phone; wants call summaries pushed to the claims system. | 7 | 0 | 29 |
| Lecture capture product for universities; needs multilingual transcription. | 4 | 0 | 28 |
| Business unit of X. | 3 | 0 | 14 |
| Built their own STT in #, reportedly looking to replace it. | 3 | 0 | 3 |
| Created by a rep manually. | 3 | 0 | 3 |
| Created by a rep manually. + Inbound demo request in #; no follow-up recorded. | 2 | 0 | 2 |
| Has an internal speech team but buys transcription for scale. | 2 | 0 | 2 |
| Imported from a conference list. + Recently expanded into the US market. | 2 | 0 | 2 |
| Contact center with ~# agents. Interested in real-time agent assist. + Duplicate? Check before outreach. | 1 | 0 | 1 |
| Created by a rep manually. + Evaluating several vendors; no decision maker identified. | 1 | 0 | 1 |
| Created by a rep manually. + Marketing-sourced lead. Downloaded a whitepaper. | 1 | 0 | 1 |
| Dispatch and driver communication over radio and phone; exploring transcription. + Imported from a conference list. | 1 | 0 | 1 |
| Duplicate? Check before outreach. | 1 | 0 | 1 |
| Duplicate? Check before outreach. + Inbound demo request in #; no follow-up recorded. | 1 | 0 | 1 |
| Duplicate? Check before outreach. + Lecture capture product for universities; needs multilingual transcription. | 1 | 0 | 1 |
| Duplicate? Check before outreach. + No recent activity. | 1 | 0 | 1 |
| Duplicate? Check before outreach. + Product has a meeting recorder feature; transcription is a core workflow. | 1 | 0 | 1 |
| Duplicate? Check before outreach. + Runs a podcast network; wants automated show notes and searchable transcripts. | 1 | 0 | 1 |
| Duplicate? Check before outreach. + Sales coaching product built on call recordings. Uses a competitor's API today. | 1 | 0 | 1 |
| Duplicate? Check before outreach. + Voice-of-customer analytics across chat, email and calls. | 1 | 0 | 1 |
| Duplicate? Check before outreach. + Website mentions AI features but nothing audio-specific. | 1 | 0 | 1 |
| Imported from a conference list. + Referral from a partner. Not yet qualified. | 1 | 0 | 1 |
| Imported from a conference list. + Website mentions AI features but nothing audio-specific. | 1 | 0 | 1 |
