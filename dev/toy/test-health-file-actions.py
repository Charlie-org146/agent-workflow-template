#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-health/scripts/file.py
"""HLT-4: health.py file carries out a close or a reopen, and builds only the argument list of the action it runs.

Once `file.args_of` built the argument lists of all four actions in one dict, so a close or a reopen (which has no label
or milestone) raised KeyError and stopped the run before any issue was closed. This calls args_of for each kind, then
file.apply with gh replaced by a recorder, and prints PASS lines. usage: test-health-file-actions.py"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "skills", "workflow-health", "scripts"))
import file as F  # noqa: E402

CLOSE = {"kind": "close", "number": "7", "key": "size:a.py:scripts", "tag": "health:size"}
REOPEN = {"kind": "reopen", "number": "8", "key": "adoption:x", "tag": "health:adoption"}
UPDATE = {"kind": "update", "number": "9", "key": "size:b.py:scripts", "tag": "health:size", "body": "text", "stone": ""}
OPEN = {"kind": "open", "title": "health: size c.py", "tag": "health:size", "label": "backlog", "stone": "", "body": "text",
        "key": "size:c.py:scripts"}
fails = []


def check(name, ok):
    print(("PASS: " if ok else "FAIL: ") + name)
    if not ok:
        fails.append(name)


try:
    close, reopen = F.args_of(CLOSE), F.args_of(REOPEN)
    check("a close builds its own argument list with no label or milestone", close[:3] == ["issue", "close", "7"])
    check("a reopen builds its own argument list with no label or milestone", reopen == ["issue", "reopen", "8"])
except KeyError as error:
    check("a close and a reopen build with no label or milestone (KeyError %s)" % error, False)
check("an update and an open still build", F.args_of(UPDATE)[:3] == ["issue", "edit", "9"] and "--label" in F.args_of(OPEN))

seen = []


def recorder(args, root, body=None):
    seen.append(args[:3])
    return subprocess.CompletedProcess(args, 0, "", "")


F.run = recorder
try:
    F.apply([CLOSE, REOPEN, UPDATE], os.getcwd(), ("size",))
    check("apply closes, reopens and updates in one run", ["issue", "close", "7"] in seen and ["issue", "reopen", "8"] in seen
          and ["issue", "edit", "9"] in seen)
except KeyError as error:
    check("apply closes, reopens and updates in one run (KeyError %s)" % error, False)
print("ALL PASS" if not fails else "%d FAILED" % len(fails))
sys.exit(1 if fails else 0)
