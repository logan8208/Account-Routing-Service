"""Draw the step 2 hand-check sample (reproducible: fixed seed).

Stratified by note template so every distinct note is checked at least 3 times (one wrong table
row would repeat across every company with that note), topped up at random to 150.
Writes output/step2_handcheck_sample.json with ONLY the raw inputs a labeller needs (no labels),
so the blind labeller cannot see Claude's answers.   Run: python pipeline/step2_sample.py
"""
import json
import random
import re
import sys
from collections import defaultdict

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from config import OUTPUT  # noqa: E402

SEED, SIZE, PER_TEMPLATE = 20261014, 150, 3


def template_of(acc):
    """Group key: the entity's notes with numbers blanked; 'Business unit of X' collapsed."""
    keys = []
    for n in acc["entity_notes"]:
        n = "Business unit of X." if n.startswith("Business unit of") else re.sub(r"\d+", "#", n)
        keys.append(n)
    return " + ".join(sorted(keys)) or "(blank)"


def main():
    acc = [a for a in json.loads((OUTPUT / "step1_accounts.json").read_text(encoding="utf-8"))
           if a["status"] == "eligible"]
    rng = random.Random(SEED)
    groups = defaultdict(list)
    for a in acc:
        # multi-note entities are grouped by their single non-admin note where possible
        groups[template_of(a)].append(a)
    picked = []
    for key in sorted(groups):
        members = groups[key][:]
        rng.shuffle(members)
        picked += members[:PER_TEMPLATE]
    rest = [a for a in acc if a not in picked]
    rng.shuffle(rest)
    picked += rest[:max(0, SIZE - len(picked))]
    sample = [{"account_id": a["account_id"], "company_name": a["company_name"],
               "industry": a["industry"], "notes": a["entity_notes"],
               "template": template_of(a)} for a in picked]
    (OUTPUT / "step2_handcheck_sample.json").write_text(json.dumps(sample, indent=1),
                                                         encoding="utf-8")
    print(f"{len(sample)} sampled from {len(acc)} eligible; {len(groups)} note templates covered")


if __name__ == "__main__":
    main()
