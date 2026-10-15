"""Rebuild everything from the original CRM exports and run every check.

    python run.py            # full pipeline + checks + web UI, then opens the UI
    python run.py --no-open  # same, without opening a browser

Steps: 1 clean/dedupe/eligibility -> 2 use-case classification -> 3 score/route -> 4 web UI
-> 5 CSV export.
Stops at the first failed check. Close the .xlsx files in Excel first (Windows locks open files).
"""
import subprocess
import sys
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STEPS = [
    ("Step 1  clean, de-duplicate, eligibility", "pipeline/step1_clean.py"),
    ("        verify step 1", "pipeline/verify_step1.py"),
    ("Step 2  classify use cases", "pipeline/step2_classify.py"),
    ("        hand-check report", "pipeline/step2_handcheck.py"),
    ("Step 3  score and route to reps", "pipeline/step3_route.py"),
    ("        verify step 3", "pipeline/verify_step3.py"),
    ("Step 4  build the web UI", "pipeline/step4_build_ui.py"),
    ("Step 5  export final CSVs", "pipeline/step5_export_csv.py"),
    ("Final   check output against rules.md and the brief", "pipeline/verify_rules.py"),
]


def main():
    for label, script in STEPS:
        print(f"\n=== {label}  ({script})")
        r = subprocess.run([sys.executable, str(ROOT / script)], cwd=ROOT)
        if r.returncode != 0:
            sys.exit(f"\nFAILED at: {label}. Nothing after this step was run.")
    ui = ROOT / "web_ui" / "rep_books.html"
    print(f"\nAll steps and checks passed. Web UI: {ui}")
    if "--no-open" not in sys.argv:
        webbrowser.open(ui.as_uri())


if __name__ == "__main__":
    main()
