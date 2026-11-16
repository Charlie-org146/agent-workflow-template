#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-docs/scripts/audit.py
"""audit-cd-path (#4502): the docs audit reads a row's test path from the folder its command cd's into.

`cd sub && bash test.sh` is not 'test no longer matches' when sub/test.sh exists, and still is when it is missing; a row
with no cd is read from the repo root as before (the control)."""
import os
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(root, "skills", "workflow-docs", "scripts"))
sys.dont_write_bytecode = True
import audit  # noqa: E402

failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


with tempfile.TemporaryDirectory() as tmp:
    os.makedirs(os.path.join(tmp, "sub"))
    open(os.path.join(tmp, "sub", "test.sh"), "w").close()
    open(os.path.join(tmp, "top.sh"), "w").close()
    check(not audit.missing(tmp, "cd sub && bash test.sh"), "cd sub, sub/test.sh exists: not missing")
    check(audit.missing(tmp, "cd sub && bash gone.sh"), "cd sub, sub/gone.sh missing: still reported")
    check(audit.missing(tmp, "cd sub && bash top.sh"), "cd sub, the script is only at the root: reported (read from sub)")
    check(not audit.missing(tmp, "bash top.sh") and audit.missing(tmp, "bash gone.sh"), "control: no cd reads from the root as before")
    check(not audit.missing(tmp, "cd $WORK && bash top.sh"), "a cd target that is no folder here (a variable) reads from the root as before")
sys.exit(1 if failed else 0)
