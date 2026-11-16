#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-regression/scripts/notrun.py skills/workflow-regression/scripts/runs.py
# reads: skills/workflow-regression/scripts/regression.py skills/workflow-delivery/scripts/role.py
"""not-runnable (#4492, GRD-11): a lane row this machine cannot run is told apart from a real failure.

Done 1: execute marks a missing tool or POSIX-only import as NOTRUN (a SKIPPED state), a real failure stays FAIL.
Done 2: a lane whose only non-passing rows are not runnable exits 0 and names them; a real failure still exits 1;
        role.lane_note reads 'N pass; M not runnable here' from the lane line.
Done 3: one other-machine to-do per goal lists them, a second call files nothing; a dry run files nothing."""
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import types

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
for sub in ("workflow-regression", "workflow-delivery"):
    sys.path.insert(0, os.path.join(root, "skills", sub, "scripts"))
sys.dont_write_bytecode = True
import notrun  # noqa: E402
import role  # noqa: E402
import runs  # noqa: E402

failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


MISSING = "echo 'pnpm: command not found' >&2; exit 1"
POSIX = "echo \"ModuleNotFoundError: No module named 'fcntl'\" >&2; exit 1"
REAL = "echo 'AssertionError: 1 != 2' >&2; exit 1"
GOOD = "exit 0"

# Done 1
check(notrun.unrunnable(127, "") and notrun.unrunnable(1, "pnpm: command not found"), "exit 127 and a missing tool are not runnable")
check(notrun.unrunnable(1, "ModuleNotFoundError: No module named 'fcntl'"), "a POSIX-only import is not runnable")
check(not notrun.unrunnable(1, "AssertionError: 1 != 2") and not notrun.unrunnable(0, "command not found"),
      "a real failure, and a pass that merely prints the words, are not 'not runnable'")
with tempfile.TemporaryDirectory() as tmp:
    picked = [{"id": k, "command": c} for k, c in (("good", GOOD), ("pnpm", MISSING), ("posix", POSIX), ("real", REAL))]
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        results, _ = runs.execute(tmp, picked, [r["id"] for r in picked], {}, None, 60, {}, True)
    state = {r["id"]: (r["state"], r.get("notrun")) for r in results}
    check(state["pnpm"] == ("SKIPPED", True) and state["posix"] == ("SKIPPED", True), "the two rows this machine cannot run are NOTRUN")
    check(state["real"] == ("FAIL", False), "negative control: a real failure stays FAIL")
    check("NOTRUN pnpm" in out.getvalue() and "FAIL real" in out.getvalue(), "the lane prints NOTRUN apart from FAIL")

# Done 2
check(role.lane_note(tmp, "x", "qa") == "", "no lane record, no note")
with tempfile.TemporaryDirectory() as tmp:
    with open(os.path.join(tmp, "g.qa-lane.last"), "w") as handle:
        json.dump({"line": "LANE qa AFFECTED 5/5 in 9s; 3 pass; 2 not runnable here (a, b)"}, handle)
    check(role.lane_note(tmp, "g", "qa") == "3 pass; 2 not runnable here", "qa is recorded as 'N pass; M not runnable here'")
    with open(os.path.join(tmp, "h.qa-lane.last"), "w") as handle:
        json.dump({"line": "LANE qa AFFECTED 5/5 in 9s"}, handle)
    check(role.lane_note(tmp, "h", "qa") == "", "a lane with nothing unrunnable adds no note")


def lane_exit(rows):
    """regression.py run over a one-commit repo holding these rows: (exit code, output)."""
    with tempfile.TemporaryDirectory() as tmp:
        git = lambda *a: subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid"] + list(a), cwd=tmp,
                                        capture_output=True, text=True)
        git("init", "-q", "-b", "main")
        os.makedirs(os.path.join(tmp, ".loop"))
        with open(os.path.join(tmp, ".loop", "regression.tsv"), "w", newline="\n") as handle:
            handle.write("# id\tlevel\tcommand\tgoal\tseen_red\tdescribe\tcategory\tlink\n")
            for key, command in rows:
                handle.write("\t".join((key, "land", command, "G-1", "2026-11-01", "d", "criterion", "")) + "\n")
        git("add", "-A")
        git("commit", "-qm", "rows")
        done = subprocess.run([sys.executable, os.path.join(root, "skills", "workflow-regression", "scripts", "regression.py"), "run", "land"],
                              cwd=tmp, capture_output=True, text=True, env=dict(os.environ, GH_TOKEN="", GITHUB_TOKEN=""))
        return done.returncode, done.stdout + done.stderr


code, said = lane_exit([("good", GOOD), ("pnpm", MISSING)])
check(code == 0 and "NOTRUNNABLE 1: pnpm" in said, "only a not-runnable row left: the run exits 0 and names it (%s)" % code)
code, said = lane_exit([("good", GOOD), ("pnpm", MISSING), ("real", REAL)])
check(code == 1 and "NOTRUNNABLE 1" in said, "negative control: a real failure beside it still exits 1")

# Done 3
calls = []


def gh(*args, body=None):
    calls.append((args, body))
    if args[:2] == ("issue", "list"):
        mine = [{"url": "https://example.invalid/i/9", "body": b} for a, b in calls if a[:2] == ("issue", "create")]
        return types.SimpleNamespace(returncode=0, stdout=json.dumps(mine))
    return types.SimpleNamespace(returncode=0, stdout="https://example.invalid/i/9\n")


with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()):
    os.makedirs(os.path.join(tmp, "docs", "wiki"))
    with open(os.path.join(tmp, "docs", "wiki", "P.md"), "w") as handle:
        handle.write("Milestone: https://example.invalid/o/r/milestone/7\n[a](Tests#t-a) [b](Tests#t-b)\n")
    check(notrun.todo(tmp, "g", ["a", "b"], False, gh) == "" and not calls, "a dry run files nothing")
    first = notrun.todo(tmp, "g", ["a", "b"], True, gh)
    second = notrun.todo(tmp, "g", ["a", "b"], True, gh)
made = [c for c in calls if c[0][:2] == ("issue", "create")]
check(first and second == first and len(made) == 1, "one to-do per goal: the second call files none")
check(made and "- `a`" in made[0][1] and "- `b`" in made[0][1] and "other-machine" in made[0][0], "it lists the rows and carries the other-machine label")
sys.exit(1 if failed else 0)
