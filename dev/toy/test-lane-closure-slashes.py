#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-regression/scripts/lanes.py
"""lane-closure-slashes (#4457): lanes.closure returns every dep with forward slashes and touches() reads a path with either
slash the same way, so a goal touching .loop/config.json matches the rows that read it on Windows too. A POSIX list reads as before.

Feeds the two walks deps named the Windows way (backslashes), then the same deps named the POSIX way. usage: test-lane-closure-slashes.py"""
import os
import sys

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(root, "skills", "workflow-regression", "scripts"))
sys.dont_write_bytecode = True
import lanes  # noqa: E402

fails = 0


def check(name, ok):
    global fails
    print(("PASS: " if ok else "FAIL: ") + name)
    fails += 0 if ok else 1


def run(deps):
    """closure and touches for a row whose walk names `deps`, as a fresh run."""
    lanes.raw_closure = lambda root_, command, cache: (set(deps), False)
    cache = {}
    got = lanes.closure(root, "row", cache)[0]
    return got, [lanes.touches(root, "row", p, {}) for p in (".loop/config.json", ".loop\\config.json", "skills/x.py")]


windows, w_touch = run({".loop\\config.json", "skills\\x.py"})
posix, p_touch = run({".loop/config.json", "skills/x.py"})
check("closure returns every dep with forward slashes", windows == {".loop/config.json", "skills/x.py"})
check("touches reads either slash form the same way", w_touch == [True, True, True])
check("a POSIX list reads exactly as before", posix == {".loop/config.json", "skills/x.py"} and p_touch == [True, True, True])
check("a path no dep names is still not touched", not lanes.touches(root, "row", "other/y.py", {}))
sys.exit(1 if fails else 0)
