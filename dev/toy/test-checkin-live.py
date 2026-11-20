#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-monitoring/scripts/checkin.py skills/workflow-monitoring/scripts/layers.py skills/workflow-monitoring/scripts/graph.py
"""TD481: the check-in's first line counts live goals, not leftover run records, by the rule the machine status file uses.

2 goals hold a busy pool entry and spoke a minute ago; 38 more hold a busy entry but have been silent for hours, and 2 read running with
no pool entry and no pid: 2 running and 40 parked on line 1 and 40 rows marked parked, the status file's live-worker count agrees (2).
A goal waiting on the owner for hours still counts under waiting on you. Negative control: with graph.live always true the same records
read 42 running and nothing parked, as the check-in did before. usage: test-checkin-live.py"""
import datetime
import json
import os
import subprocess
import sys
import tempfile

here = os.path.dirname(os.path.abspath(__file__))
scripts = os.path.join(here, "..", "..", "skills", "workflow-monitoring", "scripts")
sys.path.insert(0, scripts)
os.environ["LOOP_ROLE"] = "worker"
import checkin  # noqa: E402
import graph  # noqa: E402
import layers  # noqa: E402

failed = []
NOW = 1_800_000_000.0
AT = datetime.datetime.fromtimestamp(NOW, datetime.timezone.utc)


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def iso(at):
    return datetime.datetime.fromtimestamp(at, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as handle:
        handle.write(data if isinstance(data, str) else json.dumps(data))


def fixture(tmp):
    root = os.path.join(tmp, "toyrepo")
    subprocess.run(["git", "init", "-q", "-b", "main", root], check=True)
    write(os.path.join(root, ".loop", "config.json"), {"base": "main", "cadence": "5"})
    write(os.path.join(root, ".loop", "queue.md"), "")
    common = os.path.join(root, ".git")
    pool, runs = {}, {}
    names = [("live1", 60), ("live2", 120)] + [("stale%d" % n, 3 * 3600) for n in range(1, 39)]
    for slug, spoke in names:
        pool["s-" + slug] = {"state": "busy", "slug": slug, "name": "worker " + slug}
        runs[slug] = {"slug": slug, "status": "running", "step": "build", "goal": slug + " (DEL-1)", "updated": iso(NOW - spoke)}
    for slug in ("ghost1", "ghost2"):  # running, no pool entry, no pid
        runs[slug] = {"slug": slug, "status": "running", "step": "build", "goal": slug + " (DEL-1)", "updated": iso(NOW - 30)}
    pool["s-ask"] = {"state": "busy", "slug": "ask", "name": "worker ask"}
    runs["ask"] = {"slug": "ask", "status": "waiting", "step": "plan", "goal": "ask (DEL-1)", "updated": iso(NOW - 5 * 3600),
                   "waiting": {"ask": "Which way?", "recommend": "A", "words": ["A", "B"]}}
    for slug, run in runs.items():
        write(os.path.join(common, "loop", "runs", slug + ".json"), run)
    write(os.path.join(common, "loop", "session-pool.json"), pool)
    return root, common


def first_line(root):
    here_dir = os.getcwd()
    os.chdir(root)
    try:
        lines = checkin.render(root=root, at=AT, stamp="0000")
    finally:
        os.chdir(here_dir)
    return lines[0], lines


with tempfile.TemporaryDirectory() as tmp:
    os.environ["HOME"] = os.environ["USERPROFILE"] = os.path.join(tmp, "home")  # no followed repos, no private settings of this machine
    os.makedirs(os.environ["HOME"])
    root, common = fixture(tmp)
    line, lines = first_line(root)
    print(line)
    check(line.startswith("2 running, 1 waiting on you, 0 queued, 40 parked;"), "line 1 counts 2 running and shows the 40 stale records once as parked")
    check(sum("| parked |" in row for row in lines) == 40 and sum("| running |" in row for row in lines) == 2,
          "the All sessions rows mark the 40 stale records parked and the 2 live ones running")
    check(any("| waiting |" in row and "ask" in row for row in lines), "a goal waiting on the owner for 5 hours is still listed as waiting, never parked")
    status = layers.build(common, {}, NOW)
    live = layers.live_count(status)
    check(live == 3 and int(line.split(" running")[0]) + 1 == live, "the status file's live-worker count (%d: 2 running and the 1 waiting) agrees with line 1" % live)
    check(sum(w["status"] == "running" for w in status["workers"]) == int(line.split(" running")[0]), "the status file and the check-in agree on the running count")
    real = graph.live
    graph.live = lambda *a, **k: True  # negative control: every record counts, as the check-in did before
    blind, _ = first_line(root)
    graph.live = real
    check(blind.startswith("42 running, 1 waiting on you, 0 queued;") and "parked" not in blind, "negative control: counting every record reads 42 running and nothing parked (%s)" % blind.split(";")[0])
sys.exit(1 if failed else 0)
