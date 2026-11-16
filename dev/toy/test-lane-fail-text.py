#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-regression/scripts/runs.py
# reads: skills/workflow-regression/scripts/actions.py skills/workflow-regression/scripts/lanes.py
"""lane-fail-text (#3911): a row that ends in `| grep -q PATTERN` and fails shows its own output in the lane, not a bare FAIL.

Runs runs.execute as a lane does (reuse on) over a failing row whose quiet grep stage hides its text, and over one that
prints plainly, and reads what the lane printed to stderr."""
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


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


QUIET = 'echo THE-REAL-REASON 2>&1 | grep -q "PASS: never printed"'
PLAIN = "echo PLAIN-OUTPUT; exit 1"
with tempfile.TemporaryDirectory() as tmp:
    picked = [{"id": "quiet", "command": QUIET}, {"id": "plain", "command": PLAIN}]
    err, out = io.StringIO(), io.StringIO()
    with contextlib.redirect_stderr(err), contextlib.redirect_stdout(out):
        results, _ = runs.execute(tmp, picked, ["quiet", "plain"], {}, None, 60, {}, True)
    check([r["state"] for r in results] == ["FAIL", "FAIL"], "both rows fail")
    check("THE-REAL-REASON" in err.getvalue(), "a failing grep -q row shows its own text in the lane, not a bare FAIL")
    check("PLAIN-OUTPUT" in err.getvalue(), "a row that prints keeps its output in the lane")
sys.exit(1 if failed else 0)
