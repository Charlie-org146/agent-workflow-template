#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-regression/scripts/runs.py skills/workflow-regression/scripts/regression.py skills/workflow-regression/scripts/slots.py
# reads: skills/workflow-delivery/scripts/lanekit.py
"""lane-env (#4639): a row Windows could not start is ENV, a row that fails is still FAIL, and a lane mostly of ENV rows ends with EXIT_ENV.

Done 1: execute marks a row that exits 0xC0000142, STATUS_NO_MEMORY or the commit limit as ENV (SKIPPED, env) with a rerun hint;
        a row that exits 1 stays FAIL.
Done 2: regression.py exits EXIT_ENV (6; slots.py and lanekit.py agree) when most rows are ENV and none failed, 0 when few are, 1 on a FAIL."""
import contextlib
import io
import os
import subprocess
import sys
import tempfile
from unittest import mock

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
for sub in ("workflow-regression", "workflow-delivery"):
    sys.path.insert(0, os.path.join(root, "skills", sub, "scripts"))
sys.dont_write_bytecode = True
import lanekit  # noqa: E402
import lanes  # noqa: E402
import runs  # noqa: E402
import slots  # noqa: E402

failed = []
TAB, NL = "\t", "\n"


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


# Done 1
CODES = {"dll": 3221225794, "memory": 3221225495, "commit": 3221225773, "one": 1, "good": 0}
picked = [{"id": k, "command": k} for k in CODES]
out = io.StringIO()
with tempfile.TemporaryDirectory() as tmp, mock.patch.object(lanes, "run_row", lambda command, *rest: (CODES[command], "", 1, None)):
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        results, _ = runs.execute(tmp, picked, list(CODES), {}, None, 60, {}, True)
state = {r["id"]: (r["state"], bool(r.get("env"))) for r in results}
check(all(state[k] == ("SKIPPED", True) for k in ("dll", "memory", "commit")), "rows that exit 0xC0000142, no memory or the commit limit are ENV")
check(state["one"] == ("FAIL", False), "negative control: a row that exits 1 is still FAIL")
check(state["good"] == ("PASS", False), "a passing row is PASS")
check("ENV dll (exit 3221225794: could not start; rerun when memory allows)" in out.getvalue(), "the lane prints ENV with a rerun hint")
check(slots.EXIT_ENV == lanekit.EXIT_ENV == 6, "slots.py and lanekit.py agree on EXIT_ENV")

# Done 2
DRIVER = """import sys
sys.path.insert(0, sys.argv[1])
sys.argv = ["regression.py", "run", "land"]
import lanes, regression
lanes.run_row = lambda command, *rest: (int(command), "", 1, None)
sys.exit(regression.main())
"""


def lane_exit(codes):
    """regression.py's exit code and output for a one-commit repo whose rows exit these codes (the row runner is stubbed)."""
    with tempfile.TemporaryDirectory() as tmp:
        git = lambda *a: subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid"] + list(a), cwd=tmp,
                                        capture_output=True, text=True)
        git("init", "-q", "-b", "main")
        os.makedirs(os.path.join(tmp, ".loop"))
        with open(os.path.join(tmp, ".loop", "regression.tsv"), "w", newline=NL) as handle:
            handle.write(TAB.join(("# id", "level", "command", "goal", "seen_red", "describe", "category", "link")) + NL)
            for number, code in enumerate(codes):
                handle.write(TAB.join(("row%d" % number, "land", str(code), "G-1", "2026-11-01", "d", "criterion", "")) + NL)
        git("add", "-A")
        git("commit", "-qm", "rows")
        done = subprocess.run([sys.executable, "-c", DRIVER, os.path.join(root, "skills", "workflow-regression", "scripts")],
                              cwd=tmp, capture_output=True, text=True, env=dict(os.environ, GH_TOKEN="", GITHUB_TOKEN="", LOOP_FREE_GB="99"))
        return done.returncode, done.stdout + done.stderr


ENV = 3221225794
code, said = lane_exit([ENV, ENV, 0])
check(code == slots.EXIT_ENV and "ENV 2 of 3 rows could not start: rerun when memory allows" in said, "a lane of mostly ENV rows exits EXIT_ENV (%s)" % code)
code, said = lane_exit([ENV, 0, 0])
check(code == 0 and "ENV 1 of 3" in said, "a lane with one ENV row in three exits 0 and says so (%s)" % code)
code, said = lane_exit([ENV, ENV, 1])
check(code == 1 and "FAIL row2" in said, "negative control: a FAIL beside ENV rows still exits 1 (%s)" % code)
code, said = lane_exit([1, 1, 0])
check(code == 1 and "ENV" not in said, "negative control: rows that exit 1 are FAIL, never ENV (%s)" % code)
sys.exit(1 if failed else 0)
