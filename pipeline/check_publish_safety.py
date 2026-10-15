"""Pre-publish privacy scan: run before every push to the public repo.

Scans every file git would publish (tracked + untracked, minus .gitignore), including the XML
inside .xlsx files, for: email addresses, personal folder paths, the local OS user name, access
tokens / secret-looking words, and personal names in Office file metadata.
Run: python pipeline/check_publish_safety.py      (exits non-zero if anything is found)
"""
import getpass
import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
user = (os.environ.get("USERNAME") or getpass.getuser() or "").strip()
PATTERNS = {
    "email address": r"[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}",
    "personal folder path": r"[A-Za-z]:[\\/]+Users[\\/]+(?!<user>)[^\\/\s\"'<>]+|/c/Users/[^/\s]+|/home/[^/\s]+",
    "access token": r"\bgh[opsu]_[A-Za-z0-9]{20,}|\bsk-[A-Za-z0-9-]{20,}|AKIA[0-9A-Z]{16}",
    "secret word": r"(?i)\b(password|passwd|secret key|api[_-]?key|bearer token|private key)\b",
}
if len(user) >= 3:
    PATTERNS["local OS user name"] = r"(?i)\b" + re.escape(user) + r"\w*"
ALLOWED_XLSX_AUTHORS = {"", "CRM export", "Account Routing Service pipeline", "openpyxl"}
SELF = Path(__file__).resolve()


def files_to_publish():
    out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"],
                         cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [ROOT / f for f in out.splitlines() if f]


def main():
    findings = []
    files = files_to_publish()
    for f in files:
        if f.resolve() == SELF:
            continue
        rel = f.relative_to(ROOT).as_posix()
        texts = []
        if f.suffix.lower() == ".xlsx":
            with zipfile.ZipFile(f) as z:
                for n in z.namelist():
                    if n.endswith((".xml", ".rels")):
                        t = z.read(n).decode("utf-8", "replace")
                        texts.append((f"{rel}::{n}", t))
                        if n == "docProps/core.xml":
                            for tag in ("dc:creator", "cp:lastModifiedBy"):
                                m = re.search(rf"<{tag}>([^<]*)</{tag}>", t)
                                if m and m.group(1) not in ALLOWED_XLSX_AUTHORS:
                                    findings.append((rel, f"person in file metadata ({tag})", m.group(1)))
        else:
            try:
                texts.append((rel, f.read_text(encoding="utf-8")))
            except UnicodeDecodeError:
                continue
        for where, t in texts:
            for label, pat in PATTERNS.items():
                for m in re.finditer(pat, t):
                    findings.append((where, label, t[max(0, m.start() - 25):m.end() + 25].replace("\n", " ")))
    for where, label, ctx in findings:
        print(f"FOUND {label:24s} {where}: ...{ctx}...")
    print(f"\nScanned {len(files)} files: {len(findings)} finding(s).")
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
