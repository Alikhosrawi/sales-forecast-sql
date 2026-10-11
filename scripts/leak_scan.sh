#!/usr/bin/env bash
# Scan git-tracked files and commit messages.
# The banned-word expression is read from .leakwords (local, gitignored) or
# from the LEAK_WORDS environment variable (CI). It is never stored here.
# A hit is reported as a location only: path:line, or commit:<sha>:<line>.
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

exec python3 - <<'PY'
import os
import re
import subprocess
import sys

def load_expr():
    env = os.environ.get("LEAK_WORDS", "").strip()
    if env:
        return env
    path = ".leakwords"
    if os.path.isfile(path) and os.path.getsize(path) > 0:
        with open(path, encoding="utf-8") as f:
            lines = [ln.strip() for ln in f.read().splitlines() if ln.strip() and not ln.strip().startswith("#")]
        return "|".join(lines)
    return ""

expr = load_expr()
word_re = None
if expr:
    try:
        word_re = re.compile(expr, re.IGNORECASE)
    except re.error:
        print("Leak scan failed: the word list is not a valid regular expression.", file=sys.stderr)
        sys.exit(1)
else:
    print(
        "WARNING: LEAK_WORDS is unset and .leakwords is missing. "
        "Skipping the word list and running only the credential-assignment check.",
        file=sys.stderr,
    )

# Assignment form only: the key, then = or :, then a non-empty value.
cred_re = re.compile(
    r"(?:^|[^A-Za-z0-9_])(?:secret|password|token)[ \t]*[:=][ \t]*[^\s#]+",
    re.IGNORECASE,
)

def letter_bounded(text, match):
    """A letters-only hit must not sit inside a longer run of letters."""
    lex = match.group(0)
    if not lex.isalpha():
        return True
    i, j = match.start(), match.end()
    before = text[i - 1] if i else ""
    after = text[j] if j < len(text) else ""
    return not before.isalpha() and not after.isalpha()

def hits(text, pattern):
    if pattern is None:
        return False
    return any(letter_bounded(text, m) for m in pattern.finditer(text))

failed = False

files = subprocess.check_output(["git", "ls-files"], text=True).splitlines()
scanned_files = 0
for path in files:
    if path.startswith(".github/workflows/"):
        continue
    if not os.path.isfile(path):
        continue
    scanned_files += 1
    try:
        with open(path, encoding="utf-8", errors="strict") as f:
            lines = f.read().splitlines()
    except UnicodeDecodeError:
        continue
    for n, line in enumerate(lines, start=1):
        if hits(line, word_re) or cred_re.search(line):
            print(f"{path}:{n}")
            failed = True

log = subprocess.check_output(["git", "log", "--format=%H%x1e%B%x1e"], text=True)
commits = 0
chunks = log.split("\x1e")
# chunks are sha, body, sha, body, ... trailing empty
i = 0
while i + 1 < len(chunks):
    sha, body = chunks[i], chunks[i + 1]
    i += 2
    if not sha.strip():
        continue
    commits += 1
    for n, line in enumerate(body.splitlines() or [""], start=1):
        if hits(line, word_re) or cred_re.search(line):
            print(f"commit:{sha}:{n}")
            failed = True

if failed:
    print("Leak scan failed.", file=sys.stderr)
    sys.exit(1)

print(f"Leak scan passed ({scanned_files} tracked files, {commits} commits).")
PY
