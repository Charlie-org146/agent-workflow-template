#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-monitoring/scripts/govern_hook.py
"""Issue 4892: the quiet hook's remember() uses a plain import, not __import__ (dev/package.py's safety scan flags it),
and still writes the check-in signature that held() reads back."""
import os
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
scripts = os.path.join(root, "skills", "workflow-monitoring", "scripts")
sys.path.insert(0, scripts)
import govern_hook  # noqa: E402

failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


with open(os.path.join(scripts, "govern_hook.py"), encoding="utf-8") as handle:
    check("__import__" not in handle.read(), "govern_hook.py has no __import__ call")
with tempfile.TemporaryDirectory() as tmp:
    os.makedirs(os.path.join(tmp, "loop"))
    govern_hook.remember(tmp, "Check-in: all quiet", now=1234.0)
    seen = govern_hook.held(tmp)
    check(seen == (govern_hook.signature("Check-in: all quiet"), 1234.0), "remember() still writes what held() reads back")
sys.exit(1 if failed else 0)
