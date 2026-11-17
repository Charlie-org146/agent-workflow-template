#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-regression/scripts/runs.py skills/workflow-regression/scripts/regression.py skills/workflow-regression/scripts/slots.py
"""lane-dll-init (#4639): a row Windows could not start (0xC0000142) is rerun once, after the other rows. One still dying is ENV
(not run, with its exit code), never FAIL, and a real FAIL still fails the lane.

Done 1: execute reruns a start-code row once. A row that dies once and then passes is PASS, and one that always dies is ENV
        with its exit code. With the budget spent before its second turn, it keeps its first result (ENV), never LEFT.
        A lane of only dying rows exits EXIT_ENV, which costs no try. A row that exits 1 is never rerun.
Done 2: regression.py run over one row exiting 1 beside three dying rows exits 1 with the dying rows ENV, and an ENV row
        never overwrites a row's last FAIL or PASS in regression-runs.tsv."""
import contextlib
import io
import os
import subprocess
import sys
import tempfile
from unittest import mock

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
scripts = os.path.join(root, "skills", "workflow-regression", "scripts")
sys.path.insert(0, scripts)
sys.dont_write_bytecode = True
import lanes  # noqa: E402
import runs  # noqa: E402
import slots  # noqa: E402

failed = []
TAB, NL = "\t", "\n"
DLL = 3221225794


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def lane(plan, limit=None, clock=None):
    """execute over rows whose exits follow plan[id] (a list, one exit per run; the last repeats): (states, calls, output)."""
    calls = []

    def run_row(command, *rest):
        calls.append(command)
        seq = plan[command]
        return seq[min(calls.count(command), len(seq)) - 1], "", 1, None

    out = io.StringIO()
    with tempfile.TemporaryDirectory() as tmp, mock.patch.object(lanes, "run_row", run_row), \
            contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        patch = mock.patch.object(runs.time, "time", clock) if clock else contextlib.nullcontext()
        with patch:
            results, left = runs.execute(tmp, [{"id": k, "command": k} for k in plan], list(plan), {}, limit, 60, {}, True)
    return {r["id"]: (r["state"], bool(r.get("env"))) for r in results}, left, calls, out.getvalue()


# Done 1
state, left, calls, said = lane({"once": [DLL, 0], "dead": [DLL], "good": [0], "one": [1]})
check(state["once"] == ("PASS", False) and calls.count("once") == 2, "a row that could not start once, then passes, is PASS after one rerun")
check(state["dead"] == ("SKIPPED", True) and calls.count("dead") == 2, "a row that dies twice is ENV (not run), never FAIL")
check("ENV dead (exit %d: could not start" % DLL in said and "FAIL dead" not in said, "its line names the exit code as the cause")
check(calls.count("one") == 1 and calls.count("good") == 1, "negative control: a row that exits 1, or passes, runs once")
check(calls == ["once", "dead", "good", "one", "once", "dead"], "the reruns come after every other row (%s)" % calls)
ticks = iter([0, 0, 0, 0, 100, 100, 100, 100, 100, 100])
state, left, calls, said = lane({"dead": [DLL], "good": [0]}, limit=50, clock=lambda: next(ticks, 100))
check(state.get("dead") == ("SKIPPED", True) and "dead" not in left and calls.count("dead") == 1,
      "with the budget spent before its rerun, the row keeps its first result (ENV), not LEFT")

DRIVER = """import sys, json
sys.path.insert(0, sys.argv[1])
sys.argv = ["regression.py", "run", "land"]
import lanes, regression
seen = {}
def run_row(command, *rest):
    plan = json.loads(command.replace("'", '"'))
    seen[command] = seen.get(command, 0) + 1
    return plan[min(seen[command], len(plan)) - 1], "", 1, None
lanes.run_row = run_row
sys.exit(regression.main())
"""


def lane_exit(plans, runs_tsv=""):
    """regression.py run land over a one-commit repo whose rows exit per plans (the runner stubbed): (exit, output, runs tsv)."""
    with tempfile.TemporaryDirectory() as tmp:
        git = lambda *a: subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid"] + list(a), cwd=tmp,
                                        capture_output=True, text=True)
        git("init", "-q", "-b", "main")
        os.makedirs(os.path.join(tmp, ".loop"))
        with open(os.path.join(tmp, ".loop", "regression.tsv"), "w", newline=NL) as handle:
            handle.write(TAB.join(("# id", "level", "command", "goal", "seen_red", "describe", "category", "link")) + NL)
            for number, plan in enumerate(plans):
                handle.write(TAB.join(("row%d" % number, "land", str(plan).replace(" ", ""), "G-1", "2026-11-01", "d", "criterion", "")) + NL)
        if runs_tsv:
            with open(os.path.join(tmp, ".loop", "regression-runs.tsv"), "w", newline=NL) as handle:
                handle.write(runs.HEADER + runs_tsv)
        git("add", "-A")
        git("commit", "-qm", "rows")
        done = subprocess.run([sys.executable, "-c", DRIVER, scripts], cwd=tmp, capture_output=True, text=True,
                              env=dict(os.environ, GH_TOKEN="", GITHUB_TOKEN="", LOOP_FREE_GB="99"))
        kept = open(os.path.join(tmp, ".loop", "regression-runs.tsv")).read() if os.path.exists(os.path.join(tmp, ".loop", "regression-runs.tsv")) else ""
        return done.returncode, done.stdout + done.stderr, kept


code, said, _ = lane_exit([[DLL], [DLL], [DLL]])
check(code == slots.EXIT_ENV and "ENV 3 of 3 rows could not start" in said, "a lane of only dying rows exits EXIT_ENV, not a counted try (%s)" % code)
code, said, _ = lane_exit([[DLL, 0], [DLL, 0], [0]])
check(code == 0 and "ENV" not in said and "FAIL" not in said, "rows that start on their rerun pass, and the lane exits 0 (%s)" % code)

# Done 2
code, said, _ = lane_exit([[1], [DLL], [DLL], [DLL]])
check(code == 1 and "FAIL row0" in said and said.count("ENV row") == 3, "negative control: a real FAIL beside three dying rows still exits 1 (%s)" % code)
code, said, kept = lane_exit([[DLL], [DLL], [0]], "row0%sFAIL%s2026-11-15%s\nrow1%sPASS%s2026-11-15%s\n" % ((TAB,) * 6))
check("row0%sFAIL%s2026-11-15" % (TAB, TAB) in kept and "row1%sPASS%s2026-11-15" % (TAB, TAB) in kept,
      "an ENV row keeps its last FAIL or PASS in regression-runs.tsv")
sys.exit(1 if failed else 0)
