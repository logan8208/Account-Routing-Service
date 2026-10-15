"""Step 2 hand check: compare Claude's labels with the blind second labeller, apply the
adjudication of every disagreement, and report the measured error rate.

Inputs : output/step2_use_cases.json            (Claude's labels, all eligible companies)
         output/step2_handcheck_sample.json     (the 150-company sample, raw inputs only)
         output/step2_handcheck_blind_labels.json (independent sub-agent's blind labels)
         output/step2_adjudication.json         (optional: Claude's ruling on each disagreement,
                                                 {account_id: {"correct": label, "why": text}})
Output : output/step2_handcheck_report.md
Run    : python pipeline/step2_handcheck.py
"""
import json
import math
import sys
from collections import Counter, defaultdict

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from config import OUTPUT  # noqa: E402
from step2_sample import template_of  # noqa: E402


# Owner policy changes made AFTER the blind labelling, applied to the blind labels so both sides
# follow the same rules. This re-maps a label name only; it is not a re-judgement of any account.
POLICY_RELABEL = {"audio_analytics": "media_captions"}  # D29 revised 2026-10-14


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def main():
    mine = {r["account_id"]: r for r in json.loads((OUTPUT / "step2_use_cases.json").read_text("utf-8"))}
    sample = json.loads((OUTPUT / "step2_handcheck_sample.json").read_text("utf-8"))
    blind = {r["account_id"]: r for r in json.loads(
        (OUTPUT / "step2_handcheck_blind_labels.json").read_text("utf-8"))}
    adj_path = OUTPUT / "step2_adjudication.json"
    adj = json.loads(adj_path.read_text("utf-8")) if adj_path.exists() else {}
    assert set(blind) == {s["account_id"] for s in sample}, "blind labels do not cover the sample"

    rows, disagreements, unresolved = [], [], []
    for s in sample:
        a = s["account_id"]
        m = mine[a]["use_case"]
        b = POLICY_RELABEL.get(blind[a]["use_case"], blind[a]["use_case"])
        if m == b:
            correct = m
        elif a in adj:
            correct = adj[a]["correct"]
        else:
            correct = None
            unresolved.append(a)
        if m != b:
            disagreements.append((s, m, b, adj.get(a)))
        rows.append((s, m, b, correct))
    n = len(rows)
    agree = sum(m == b for _, m, b, _ in rows)
    if unresolved:
        print(f"{len(unresolved)} disagreements need adjudication:")
        for s, m, b, _ in disagreements:
            if s["account_id"] in unresolved:
                print(f"  {s['account_id']} | {s['industry']} | {s['notes']} | claude={m} "
                      f"blind={b} ({blind[s['account_id']]['why']})")
        return

    my_err = [r for r in rows if r[1] != r[3]]
    k = len(my_err)
    lo, hi = wilson(k, n)
    # population-weighted: per-template error rate x template share of all eligible companies
    all_acc = [a for a in json.loads((OUTPUT / "step1_accounts.json").read_text("utf-8"))
               if a["status"] == "eligible"]
    pop = Counter(template_of(a) for a in all_acc)
    per_t = defaultdict(lambda: [0, 0])
    for s, m, b, c in rows:
        per_t[s["template"]][0] += 1
        per_t[s["template"]][1] += m != c
    weighted = sum(pop[t] * e / tot for t, (tot, e) in per_t.items()) / len(all_acc)

    L = ["# Step 2 hand check — measured error rate", "",
         f"- Sample: **{n}** of {len(all_acc)} eligible companies, stratified so every one of "
         f"the {len(per_t)} note templates is checked (fixed seed, `pipeline/step2_sample.py`).",
         "- Method: an independent Claude sub-agent labelled the sample **blind** (raw notes + "
         "industry + the owner-approved label rules only; it never saw Claude's labels or table). "
         "Every disagreement was then re-read and adjudicated by Claude.",
         f"- Raw agreement between the two labellers: **{agree}/{n} = {agree / n:.1%}**.",
         f"- **Claude's measured error rate: {k}/{n} = {k / n:.1%}** (95% Wilson CI "
         f"{lo:.1%}–{hi:.1%}).",
         f"- Weighted to the full population by note template: **{weighted:.1%}**.",
         "- Limitation: both labellers are Claude, so shared blind spots are possible. The "
         "owner's ground-truth comparison is the real test.", "",
         "## What this error rate does and does not measure", "",
         "It measures whether each company got the label the **owner-approved rules** give it "
         "(reading the notes correctly, applying precedence, no typos or table mistakes). It does "
         "**not** test whether the rules themselves match the ground truth, because the blind "
         "labeller was given the same rules. If the ground truth differs, it will most likely be "
         "in these policy calls, not in reading individual notes:", "",
         "- D26: 783 companies with no speech signal → `none` (ground truth might use industry).",
         "- D29: 44 dispatch radio/phone companies → `media_captions` (owner's call; a loose fit, "
         "since dispatch audio is not published media — ground truth may say `other` or "
         "`call_analytics`). The blind labeller used `audio_analytics` for these before the owner "
         "changed the rule; that label name was re-mapped (`POLICY_RELABEL`), not re-judged.",
         "- D28: 60 podcast / lecture-capture companies → `media_captions` (could be "
         "`meeting_notes`).",
         "- D30: 63 speech-interest-only companies → industry-implied label or `other`.",
         "- 56 \"website mentions AI features but nothing audio-specific\" → `none`.", "",
         "## Disagreements and rulings", "",
         "| account | industry | notes | Claude | blind | correct | ruling |", "|---|---|---|---|---|---|---|"]
    for s, m, b, a in disagreements:
        L.append(f"| {s['account_id']} | {s['industry']} | {' / '.join(s['notes']) or '(blank)'} "
                 f"| {m} | {b} | {a['correct']} | {a['why']} |")
    if not disagreements:
        L.append("| — | | | | | | none |")
    L += ["", "## Per note template", "", "| template | in sample | Claude errors | companies in population |",
          "|---|---|---|---|"]
    for t, (tot, e) in sorted(per_t.items(), key=lambda x: -pop[x[0]]):
        L.append(f"| {t} | {tot} | {e} | {pop[t]} |")
    (OUTPUT / "step2_handcheck_report.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L[:9]))


if __name__ == "__main__":
    main()
