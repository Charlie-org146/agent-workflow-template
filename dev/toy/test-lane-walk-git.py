#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-regression/scripts/lanes.py
"""lane-walk-git (#4151): lanes.py never walks or follows .git, so `affected` stays small on a checkout holding other worktrees.

Done 1: walk of the repo root lists no file under .git, and a text that names ../.git/loop/worktrees/x/dev (a Windows
        normpath makes it a backslash path) follows nothing there; a plain dev/ path is still followed."""
import os
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(root, "skills", "workflow-regression", "scripts"))
sys.dont_write_bytecode = True
import lanes  # noqa: E402

failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


with tempfile.TemporaryDirectory() as tmp:
    for rel in (".git/loop/worktrees/x/dev/a.py", ".git/HEAD", "dev/real.py", "top.py"):
        os.makedirs(os.path.dirname(os.path.join(tmp, rel)), exist_ok=True)
        open(os.path.join(tmp, rel), "w").write("x\n")
    listed = [p.replace("\\", "/") for p in lanes.walk(tmp, "")]
    check(sorted(listed) == ["dev/real.py", "top.py"], "walk of the root lists the repo's files and nothing under .git (%s)" % sorted(listed))
    found, _ = lanes.references(tmp, "see ../.git/loop/worktrees/x/dev/a.py and ../.git/loop/worktrees/x/dev/", "dev", True, {})
    check(not any(p.replace("\\", "/").startswith(".git") for p in found), "a path into .git is not followed (%s)" % sorted(found))
    found, _ = lanes.references(tmp, "see dev/real.py", "", True, {})
    check({p.replace("\\", "/") for p in found} == {"dev/real.py"}, "negative control: a plain repo path is still followed (%s)" % sorted(found))
sys.exit(1 if failed else 0)
