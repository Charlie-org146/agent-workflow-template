#!/usr/bin/env python3
# reads: skills/workflow-regression/scripts/tiers.py skills/workflow-regression/scripts/level_words.py
"""G4-2 (v110-lvl-retire-old-words-2): one set of level words, L0, L1 and L2.

Runs in a temporary folder with its own HOME, no network. Case goal: the goal_levels table (plan D2a), on a levelled table and on one
that is not. usage: test-level-words.py [goal]  (no argument: all)"""
import contextlib
import io
import json
import os
import sys
import tempfile
import types

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(root, "skills", "workflow-regression", "scripts"))
os.environ["HOME"] = os.environ["USERPROFILE"] = tempfile.mkdtemp(prefix="test-level-words-home.")
failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def folder(armed, goal_levels):
    top = tempfile.mkdtemp(prefix="test-level-words.")
    os.makedirs(os.path.join(top, ".loop"))
    os.makedirs(os.path.join(top, ".github", "workflows"))
    head = "# id\tlevel\tcommand\tgoal\tseen_red\tdescription\tcategory\tlink\n"
    open(os.path.join(top, ".loop", "regression.tsv"), "w").write(head + ("lvl-armed\tland\ttrue\t-\t2026-01-01\tA row.\tcriterion\t\n" if armed else ""))
    open(os.path.join(top, ".github", "workflows", "regression-pr.yml"), "w").write("# Written by workflow-regression\n")
    open(os.path.join(top, ".loop", "config.json"), "w").write(json.dumps({"goal_levels": goal_levels} if goal_levels else {}))
    return top


def plan(armed, value):
    """What a goal lane plans from for this goal_levels value: (target, stdout, stderr, exit code or None)."""
    import tiers
    top = folder(armed, value)
    out, err, code, got = io.StringIO(), io.StringIO(), None, None
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            got = tiers.target(top, types.SimpleNamespace(tier="goal", target="land"))
    except SystemExit as stop:
        code = stop.code
    return got, out.getvalue(), err.getvalue(), code


def goal():
    print("== D2a: the goal_levels table")
    # Value: protects=a goal lane plans from the level the setting names, and an old word is read and said; fails_when=L0, L1 or L2 is
    #   ignored, or an old word is read in silence, or a bad value passes on a levelled table; why_new=the setting knew only land and nightly
    for value, want in (("land", "L0"), ("nightly", "L1"), ("L0", "L0"), ("L1", "L1"), ("L2", "L2")):
        got, out, err, code = plan(True, value)
        old = value in ("land", "nightly")
        check(got == want and code is None and (("GOAL_LEVELS_OLD" in out) == old), "levelled table: goal_levels %r plans from %s%s" % (value, want, " and says so" if old else ""))
    for armed in (True, False):
        got, out, err, code = plan(armed, None)
        check(got == "land" and code is None and not out + err, "goal_levels not set: a goal lane plans as it always did, in silence (%s table)" % ("levelled" if armed else "not levelled"))
    got, out, err, code = plan(True, "weekly")
    check(code not in (None, 0) and "REFUSED (GOAL_LEVELS_BAD)" in err and "Nothing was run." in err, "levelled table: goal_levels 'weekly' is refused before any work")
    for value, want in (("land", "land"), ("nightly", "nightly"), ("L0", "land"), ("L1", "nightly"), ("L2", "nightly")):
        got, out, err, code = plan(False, value)
        check(got == want and code is None and "GOAL_LEVELS_OLD" not in out, "table not levelled: goal_levels %r runs as %s" % (value, want))
    got, out, err, code = plan(False, "weekly")
    check(got == "land" and code is None and "GOAL_LEVELS" in out + err, "table not levelled: goal_levels 'weekly' runs as land and is warned about")


cases = {"goal": goal}
for name in (sys.argv[1:] or list(cases)):
    cases[name]()
print("%d failed" % len(failed))
print("ALL PASS" if not failed else "FAILED")
sys.exit(1 if failed else 0)
