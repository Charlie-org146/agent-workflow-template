#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-regression/scripts/runs.py skills/workflow-regression/scripts/regression.py
"""owed-close (#3907): recording the real red proof closes the other-machine to-do issue held in .loop/regression-owed.tsv.

Calls runs.owed_clear with gh stubbed: live, it closes the recorded issue once and clears the record; not live, it only
says so and runs nothing."""
import contextlib
import io
import os
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(root, "skills", "workflow-regression", "scripts"))
sys.dont_write_bytecode = True
import runs  # noqa: E402

failed = []
URL = "https://example.invalid/owner/repo/issues/7"


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def fresh(tmp):
    os.makedirs(os.path.join(tmp, ".loop"), exist_ok=True)
    with open(os.path.join(tmp, ".loop", runs.OWED), "w", newline="\n") as handle:
        handle.write("\t".join(("row1", "2026-01-01", "mac", URL)) + chr(10))


calls = []
runs.gh = lambda *args, **kw: calls.append(args)
with tempfile.TemporaryDirectory() as tmp:
    fresh(tmp)
    with contextlib.redirect_stdout(io.StringIO()):
        runs.owed_clear(tmp, "row1", False)
    check(calls == [] and "row1" not in runs.owed_read(tmp), "not live: nothing is closed, the record clears")
    fresh(tmp)
    with contextlib.redirect_stdout(io.StringIO()):
        runs.owed_clear(tmp, "row1", True)
        runs.owed_clear(tmp, "row1", True)
    check(len(calls) == 1 and calls[0][:3] == ("issue", "close", URL) and "row1" not in runs.owed_read(tmp),
          "live: the recorded to-do issue is closed once and the record clears")
sys.exit(1 if failed else 0)
