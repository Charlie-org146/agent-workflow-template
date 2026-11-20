#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-monitoring/scripts/checkin.py skills/workflow-monitoring/scripts/board_lines.py skills/workflow-monitoring/scripts/graph.py
"""CHK-1 (MON-5): the check-in shows each repo's work as a queue: Building now, then Queue, in order, each row with its ETA or
"ETA unknown: <why>". A fixture repo has 2 running and 3 queued goals, one waiting on a running goal, one on a queued goal."""
import datetime
import json
import os
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


def blocks(out):
    """(building lines, queue lines) of the Dependencies section."""
    rows = out.splitlines()
    a, b = rows.index("Building now:"), rows.index("Queue, in order:")
    end = next((n for n in range(b + 1, len(rows)) if not rows[n].startswith("  ")), len(rows))
    def joined(lines):  # the check-in wraps at 60 columns: a continuation line starts with 4 spaces
        out = []
        for line in lines:
            out.append(line) if not (line.startswith("    ") and out) else out.__setitem__(-1, out[-1] + " " + line.strip())
        return out
    return joined(rows[a + 1:b]), joined(rows[b + 1:end])


with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as home:
    for key in ("HOME", "USERPROFILE"):
        os.environ[key] = home
    os.environ["LOOP_MACHINE_NAME"] = "pc"
    root = os.path.join(tmp, "toyrepo")
    subprocess.run(["git", "init", "-q", "-b", "main", root], check=True)
    os.makedirs(os.path.join(root, ".loop"))
    with open(os.path.join(root, ".loop", "config.json"), "w") as f:
        json.dump({"base": "main", "parallel": 2}, f)
    with open(os.path.join(root, ".loop", "queue.md"), "w") as f:
        f.write("- slug: q-free | goal: Starts when a slot frees | done: d\n"
                "- slug: q-on-run | depends-on: run-a | goal: Waits on a running goal | done: d\n"
                "- slug: q-on-q | depends-on: q-on-run | goal: Waits on a queued goal | done: d\n")
    runs = os.path.join(root, ".git", "loop", "runs")
    os.makedirs(runs)
    now = datetime.datetime.now(datetime.timezone.utc)
    stamp = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    for slug, step, pr in (("run-a", "build", "https://example.test/pull/7"), ("run-b", "plan", None)):
        record = {"slug": slug, "goal": "Running " + slug, "status": "running", "step": step, "worker": "session", "pid": os.getpid(),
                  "updated": stamp, "report": {"at": stamp, "text": "working"}}
        record.update({"pr": pr} if pr else {})
        with open(os.path.join(runs, slug + ".json"), "w") as f:
            json.dump(record, f)
    left = {"run-a": 1800, "run-b": 3600, "q-free": 5400, "q-on-run": None, "q-on-q": 600}
    checkin.bs.left_time = lambda run, runs_, at, root=None: left.get(run["slug"])  # the estimate model needs a history of finished goals
    out = "\n".join(checkin.render(root=root, at=now, stamp="0000"))
    building, queue = blocks(out)
    text = "\n".join(building)
    check(len(building) == 2 and "run-a" in building[0] and "run-b" in building[1], "Building now lists the 2 running goals, one row each: %s" % building)
    check("PR 7" in building[0], "a running goal's row shows its PR number")
    check("no PR yet" in building[1], "a running goal with no PR says so")
    check("build" in building[0] and "plan" in building[1] and "/8" in text, "a running goal's row shows its step and progress")
    check(all("ETA " in row for row in building), "every Building now row has an ETA")
    check(len(queue) == 3 and [row.split("|")[0].strip() for row in queue] == ["1. q-free", "2. q-on-run", "3. q-on-q"],
          "Queue, in order lists the 3 queued goals in queue.md order with positions: %s" % queue)
    check("slots full" in queue[0] and "ETA " in queue[0] and "unknown" not in queue[0], "a goal with only a full slot to wait for starts when the first running goal ends: %s" % queue[0])
    check("waits on" in queue[1] and "run-a" in queue[1] and "ETA " in queue[1], "a goal that waits on a running goal names it and starts when it ends: %s" % queue[1])
    check("ETA unknown: q-on-run has no estimate" in queue[2], "a goal behind a queued goal with no estimate prints ETA unknown with the reason: %s" % queue[2])
    check(not any(s in " ".join(queue) for s in ("run-a", "run-b")) or "waits on" in queue[1], "a running goal is not a row of the queue block")
    check(not any(s in text for s in ("q-free", "q-on-run", "q-on-q")), "a queued goal is not a row of the building block")
    # negative controls: a goal that starts leaves the queue for the building block; a running goal with no estimate prints ETA unknown
    with open(os.path.join(runs, "q-free.json"), "w") as f:
        json.dump({"slug": "q-free", "goal": "Now running", "status": "running", "step": "idea", "worker": "session", "pid": os.getpid(),
                   "updated": stamp, "report": {"at": stamp, "text": "working"}}, f)
    left["run-b"] = None
    building, queue = blocks("\n".join(checkin.render(root=root, at=now, stamp="0000")))
    check(any("q-free" in row for row in building) and not any("q-free" in row for row in queue), "negative control: a goal that started moves from the queue block to the building block")
    check(len(building) == 3 and len(queue) == 2, "negative control: the blocks then hold 3 running and 2 queued")
    check(any("run-b" in row and "ETA unknown" in row for row in building), "negative control: a running goal with no estimate prints ETA unknown, never a time")
    with open(os.path.join(root, ".loop", "queue.md"), "w") as f:
        f.write("")
    building, queue = blocks("\n".join(checkin.render(root=root, at=now, stamp="0000")))
    check(queue == ["  (none queued)"], "negative control: an empty queue says so: %s" % queue)

print("ALL PASS" if not failed else "%d FAILED" % len(failed))
sys.exit(1 if failed else 0)
