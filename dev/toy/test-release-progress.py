#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-monitoring/scripts/checkin.py skills/workflow-monitoring/scripts/board_lines.py
"""CHK-1 (MON-5): under each release the check-in shows, for each goal, one progress bar per frozen done line with done/total and an
ETA, and a roll-up bar for the release. A fixture has 2 releases and 3 goals: a running goal with 3 done lines (2 with linked rows),
a queued one with 2 done lines and no rows, and a queued one in the second release whose only line has a passing row."""
import datetime
import json
import os
import re
import subprocess
import sys
import tempfile

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, "..", "..", "skills", "workflow-monitoring", "scripts"))
import checkin  # noqa: E402

failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def section(out, goal):
    """The lines of one goal: its goal line, then its bars."""
    rows = out.splitlines()
    start = next(n for n, row in enumerate(rows) if re.match(r"\s+\[.\] %s " % goal, row))
    end = next((n for n in range(start + 1, len(rows)) if not rows[n].startswith("    ") or re.match(r"\s+\[.\] ", rows[n])), len(rows))
    joined = []
    for row in rows[start + 1:end]:  # the check-in wraps at 60 columns: a continuation line starts with 4 spaces
        joined.append(row) if row.startswith("      d") else joined.__setitem__(-1, joined[-1] + " " + row.strip())
    return joined


with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as home:
    for key in ("HOME", "USERPROFILE"):
        os.environ[key] = home
    os.environ["LOOP_MACHINE_NAME"] = "pc"
    root = os.path.join(tmp, "toyrepo")
    subprocess.run(["git", "init", "-q", "-b", "main", root], check=True)
    os.makedirs(os.path.join(root, ".loop", "goals"))
    with open(os.path.join(root, ".loop", "config.json"), "w") as f:
        json.dump({"base": "main", "parallel": 3}, f)
    with open(os.path.join(root, ".loop", "queue.md"), "w") as f:
        f.write("## Batch: v1-0-1\n- slug: run-a | goal: Running a | done: x\n- slug: q-b | goal: Queued b | done: first line | done: second line\n"
                "## Batch: v1-0-2\n- slug: q-c | goal: Queued c | done: only line\n")
    with open(os.path.join(root, ".loop", "goals", "run-a.md"), "w") as f:
        f.write("# Running a\n\n## Done lines\n\nFrozen.\n\n1. Given a, then b\n2. Given c, then d\n3. Given e, then f\n\n## Verify by hand\n\nnone\n")
    with open(os.path.join(root, ".loop", "regression.tsv"), "w") as f:
        f.write("# id\tlevel\tcommand\tgoal\n" + "".join("%s\tland\ttrue\t%s\n" % row for row in (
            ("a1", "run-a:1"), ("a2", "run-a:1"), ("a3", "run-a:2"), ("c1", "q-c:1"))))
    with open(os.path.join(root, ".loop", "regression-runs.tsv"), "w") as f:
        f.write("a1\tPASS\t2026-11-20\t\t\na2\tFAIL\t2026-11-20\t\t\na3\tPASS\t2026-11-20\t\t\nc1\tPASS\t2026-11-20\t\t\n")
    runs = os.path.join(root, ".git", "loop", "runs")
    os.makedirs(runs)
    now = datetime.datetime.now(datetime.timezone.utc)
    stamp = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(os.path.join(runs, "run-a.json"), "w") as f:
        json.dump({"slug": "run-a", "goal": "Running a", "status": "running", "step": "build", "worker": "session", "pid": os.getpid(),
                   "updated": stamp, "report": {"at": stamp, "text": "working"}}, f)
    left = {"run-a": 1800, "q-b": 3600, "q-c": None}
    checkin.bs.left_time = lambda run, runs_, at, root=None: left.get(run["slug"])  # the estimate model needs a history of finished goals
    os.chdir(root)  # the check-in follows the repo it runs in
    out = "\n".join(checkin.render(root=root, at=now, stamp="0000"))
    a, b, c = section(out, "run-a"), section(out, "q-b"), section(out, "q-c")
    check(len(a) == 3 and len(b) == 2 and len(c) == 1, "each goal shows one bar per frozen done line: %d, %d and %d" % (len(a), len(b), len(c)))
    check("d1 [####----] 1/2 " in a[0] and "d2 [########] 1/1 " in a[1], "a line's bar is its linked rows that last passed over the rows linked: %s" % a[:2])
    check("d3 [##------] 2/8 by step" in a[2], "a line with no linked row shows the goal's flow-step progress, marked by step: %s" % a[2])
    check(all(row.rstrip().endswith(")") and "ETA " in row for row in a + b), "every bar of a goal with an estimate shows done/total and an ETA: %s" % a[0])
    check("d1 [--------] 0/8 by step" in b[0] and "d2 [--------] 0/8 by step" in b[1], "a queued goal's done lines come from the queue, with no rows yet: %s" % b)
    check("d1 [########] 1/1 ETA unknown: q-c has no estimate" in c[0], "a goal with no estimate prints ETA unknown with the reason: %s" % c[0])
    check(all(len(row) <= 60 for row in a + b + c), "every bar line is at most 60 columns")
    rolls = [row for row in out.splitlines() if row.strip().startswith("roll-up")]
    check(len(rolls) == 2, "each of the 2 releases shows a roll-up bar: %s" % rolls)
    check(any("1/5 done lines" in row and "ETA " in row and "unknown" not in row for row in rolls), "a roll-up counts the release's done lines complete over all its lines, with its ETA: %s" % rolls)
    check(any("1/1 done lines" in row and "ETA unknown: q-c has no" in row for row in rolls), "negative control: a release with a goal that has no estimate prints ETA unknown, never a time")
    check(sum("by step" in row for row in out.splitlines()) == 3, "negative control: only the lines with no linked row read by step")
    left["q-c"] = 600
    again = "\n".join(checkin.render(root=root, at=now, stamp="0000"))
    check("ETA unknown" not in [row for row in again.splitlines() if "d1 " in row and "1/1" in row][0], "negative control: once the goal has an estimate its bar shows a time")
    os.chdir(here)  # a temp folder can't be removed while it is the working directory

print("ALL PASS" if not failed else "%d FAILED" % len(failed))
sys.exit(1 if failed else 0)
