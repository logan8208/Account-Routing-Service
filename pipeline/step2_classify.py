"""Step 2 - classify one use case per eligible company.

Method (approved 2026-10-14, see docs/step2_classification_proposal.md): the notes are templated,
so Claude read every distinct note once and wrote the decision table below (NOTE_RULES). This
script applies the table to every eligible company, validates each record against
pipeline/use_case_schema.json, checks that the quoted evidence really is in that company's own data,
and writes output/step2_use_cases.json. It then rebuilds accounts-XLSX.xlsx so the use-case columns
appear in the after-columns.

Precedence per company (all notes of merged duplicate records are considered):
  1. a note naming a use case                  -> that label            (evidence: notes)
  2. a speech-interest note with no use case   -> industry if clear, else other (notes+industry)
  3. no speech signal                          -> none                 (D26: Option B)

Run:  python pipeline/step2_classify.py
"""
import json
import re
import sys
from collections import Counter

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from config import OUTPUT, ROOT  # noqa: E402

SCHEMA = json.loads((ROOT / "pipeline" / "use_case_schema.json").read_text(encoding="utf-8"))
LABELS = SCHEMA["properties"]["use_case"]["enum"]

# (regex on one note, use_case, confidence, needs_review, rationale for a rep)
NOTE_RULES = [
    (r"^Records inbound support calls", "call_analytics", "high", False,
     "Records inbound support calls and wants call transcription and QA scoring."),
    (r"^Voice-of-customer analytics across chat, email and calls", "call_analytics", "high", False,
     "Runs voice-of-customer analytics that include calls."),
    (r"^Sales coaching product built on call recordings", "call_analytics", "high", False,
     "Sales coaching product built on call recordings; uses a competitor's API today."),
    (r"^Contact center with ~\d+ agents\. Interested in real-time agent assist", "call_analytics",
     "high", False, "Contact center interested in real-time agent assist."),
    (r"^Insurance claims intake via phone", "call_analytics", "high", False,
     "Takes insurance claims by phone and wants call summaries in the claims system."),
    (r"^Building an AI voice agent", "voice_agent", "high", False,
     "Building an AI voice agent for appointment scheduling (on Twilio today)."),
    (r"^IVR modernization project", "voice_agent", "high", False,
     "Has an IVR modernization project scoped for next fiscal year."),
    (r"^Product has a meeting recorder feature", "meeting_notes", "high", False,
     "Product has a meeting recorder; transcription is a core workflow."),
    (r"^Streaming captions for live events", "media_captions", "high", False,
     "Needs streaming captions for live events."),
    (r"^Video platform adding captions and dubbing", "media_captions", "high", False,
     "Video platform adding captions and dubbing for creators."),
    (r"^Runs a podcast network", "media_captions", "medium", False,  # D28 (Q-C)
     "Podcast network wanting automated show notes and searchable transcripts."),
    (r"^Lecture capture product", "media_captions", "medium", False,  # D28 (Q-C)
     "Lecture capture product for universities needing multilingual transcription."),
    (r"^Telehealth platform\. Clinicians want ambient note-taking", "clinical_documentation", "high",
     False, "Telehealth platform; clinicians want ambient note-taking from patient visits."),
    (r"^Legal deposition and hearing recordings", "legal_transcription", "high", False,
     "Transcribes legal depositions and hearings; proper-noun accuracy matters."),
    # D29 (revised 2026-10-14): owner chose media_captions over audio_analytics (not one of the
    # brief's 8 labels). Claude flagged it as a loose fit (dispatch audio is not published media),
    # so it is marked needs_review.
    (r"^Dispatch and driver communication over radio and phone", "media_captions", "medium",
     True, "Dispatch and driver radio/phone communication; exploring transcription."),
]
# Speech interest, but no use case named -> rule 2 (D30, Q-E)
SPEECH_INTEREST = [
    (r"^Job posting for a 'Speech ML Engineer' seen in \d{4}", "Posted a job for a Speech ML Engineer"),
    (r"^Built their own STT in \d{4}, reportedly looking to replace it", "Built their own speech-to-text and is reportedly looking to replace it"),
    (r"^Has an internal speech team but buys transcription for scale", "Has an internal speech team but buys transcription for scale"),
]
EXPLICIT_NO_AUDIO = r"^Website mentions AI features but nothing audio-specific"

INDUSTRY_USE_CASE = {
    "Healthcare": "clinical_documentation",
    "Legal Tech": "legal_transcription",
    "Contact Center Software": "call_analytics",
    "Conversation Intelligence": "call_analytics",
    "Sales Tech": "call_analytics",
    "Insurance": "call_analytics",
    "Telephony / CPaaS": "voice_agent",
    "Media & Entertainment": "media_captions",
    "EdTech": "media_captions",
}


def classify(acc):
    notes = acc["entity_notes"]
    for n in notes:
        for pat, label, conf, review, why in NOTE_RULES:
            if re.match(pat, n):
                return dict(use_case=label, evidence_source="notes", evidence=n, confidence=conf,
                            rationale=why, needs_review=review)
    for n in notes:
        for pat, why in SPEECH_INTEREST:
            if re.match(pat, n):
                ind = acc["industry"]
                label = INDUSTRY_USE_CASE.get(ind)
                if label:
                    return dict(use_case=label, evidence_source="notes+industry",
                                evidence=f"{n} | industry: {ind}", confidence="medium",
                                rationale=f"{why}; as a {ind} company the likely use is "
                                          f"{label.replace('_', ' ')}.", needs_review=False)
                return dict(use_case="other", evidence_source="notes+industry",
                            evidence=f"{n} | industry: {ind}", confidence="low",
                            rationale=f"{why}, but neither the notes nor the industry ({ind}) say "
                                      f"what for.", needs_review=True)
    for n in notes:
        if re.match(EXPLICIT_NO_AUDIO, n):
            return dict(use_case="none", evidence_source="notes", evidence=n, confidence="high",
                        rationale="Notes say the website mentions AI features but nothing "
                                  "audio-specific.", needs_review=False)
    return dict(use_case="none", evidence_source="no_signal", evidence="", confidence="medium",
                rationale="Nothing in the notes points to a speech or transcription need.",
                needs_review=False)


def validate(rec, acc):
    """Hand-rolled check against use_case_schema.json (no extra dependency) + grounding check."""
    props = SCHEMA["properties"]
    errs = []
    if set(rec) != set(SCHEMA["required"]):
        errs.append(f"fields {sorted(rec)}")
    for k in ("use_case", "evidence_source", "confidence"):
        if rec.get(k) not in props[k]["enum"]:
            errs.append(f"{k}={rec.get(k)!r}")
    if not re.fullmatch(props["account_id"]["pattern"], rec["account_id"]):
        errs.append("account_id")
    if len(rec["rationale"]) > props["rationale"]["maxLength"] or not rec["rationale"]:
        errs.append("rationale length")
    if not isinstance(rec["needs_review"], bool):
        errs.append("needs_review type")
    # grounding: every piece of quoted evidence must be this company's own text
    for part in [p for p in rec["evidence"].split(" | ") if p]:
        if part.startswith("industry: "):
            ok = part[len("industry: "):] == acc["industry"]
        else:
            ok = part in acc["entity_notes"]
        if not ok:
            errs.append(f"ungrounded evidence {part!r}")
    if (rec["evidence"] == "") != (rec["evidence_source"] == "no_signal"):
        errs.append("evidence/no_signal mismatch")
    return errs


def main():
    accounts = json.loads((OUTPUT / "step1_accounts.json").read_text(encoding="utf-8"))
    eligible = [a for a in accounts if a["status"] == "eligible"]
    out, problems = [], []
    for a in eligible:
        rec = {"account_id": a["account_id"], **classify(a)}
        errs = validate(rec, a)
        if errs:
            problems.append((a["account_id"], errs))
        out.append(rec)
    if problems:
        sys.exit(f"STOP: {len(problems)} records failed validation, e.g. {problems[:3]}")
    assert len(out) == len(eligible) == len({r["account_id"] for r in out})
    (OUTPUT / "step2_use_cases.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"classified {len(out)} eligible companies; 0 schema/grounding failures")
    for k, v in Counter(r["use_case"] for r in out).most_common():
        print(f"  {k:24s}{v}")
    print("by evidence source:", dict(Counter(r["evidence_source"] for r in out)))
    print("needs_review:", sum(r["needs_review"] for r in out))

    import step1_clean  # rebuild the workbook so the use-case columns appear
    step1_clean.main()


if __name__ == "__main__":
    main()
