#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-monitoring/scripts/checkin.py skills/workflow-monitoring/scripts/layers.py skills/workflow-monitoring/scripts/machines.py
"""TD481: the check-in's first line counts live goals, not leftover run records, by the rule the machine status file uses.

2 goals hold a busy pool entry and spoke a minute ago; 38 more hold a busy entry but have been silent for hours, and 2 read running with
no pool entry and no pid: 2 running and 40 parked on line 1 and 40 rows marked parked, the status file's live-worker count agrees (2).
A goal waiting on the owner for hours still counts under waiting on you (its session is in the pool, or it has none: a background worker);
a waiting record is parked, in the same count, only when provably over: its pull request merged, the goal retired, or its bound session gone from the pool. Negative control: with machines.live always true the same records
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
import machines  # noqa: E402
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
    base = {"status": "waiting", "step": "plan", "updated": iso(NOW - 5 * 3600), "waiting": {"ask": "Which way?", "recommend": "A", "words": ["A", "B"]}}
    runs["bg"] = dict(base, slug="bg", goal="bg (DEL-1)")  # a background worker's question: no session, no pool entry, still a real question
    runs["merged"] = dict(base, slug="merged", goal="merged (DEL-1)", release="merged", session={"id": "x", "name": "worker merged"})
    runs["retired"] = dict(base, slug="retired", goal="retired (DEL-1)", retired={"reason": "moved on"})
    runs["nosession"] = dict(base, slug="nosession", goal="nosession (DEL-1)", session={"id": "gone", "name": "worker nosession"})  # bound session not in the pool
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
    check(line.startswith("2 running, 2 waiting on you, 0 queued, 43 parked;"),
          "line 1 counts 2 running and 2 waiting, and shows the 40 stale running and the 3 provably-over waiting records once as parked")
    check(sum("| parked |" in row for row in lines) == 0 and sum("| waiting |" in row for row in lines) == 5,
          "the All sessions tables are as they were (MON-14): no row renamed parked, every record still listed")
    check(any("| waiting |" in row and "ask (" in row for row in lines) and any("| waiting |" in row and "bg (" in row for row in lines),
          "a goal waiting on the owner for 5 hours, in the pool or with no session at all, is still listed as waiting, never parked")
    status = layers.build(common, {}, NOW)
    live = layers.live_count(status)
    check(live == 4 and int(line.split(" running")[0]) + 2 == live, "the status file's live-worker count (%d: 2 running and the 2 waiting) agrees with line 1" % live)
    asked = {n["slug"] for n in status["needs_owner"]}
    check({"ask", "bg"} <= asked and not asked & {"merged", "retired", "nosession"}, "the status file asks the owner about the 2 live questions and not about the parked waiting records (%s)" % sorted(asked))
    check(sum(w["status"] == "running" for w in status["workers"]) == int(line.split(" running")[0]), "the status file and the check-in agree on the running count")
    real = machines.live
    machines.live = lambda *a, **k: True  # negative control: every record counts, as the check-in did before
    blind, _ = first_line(root)
    machines.live = real
    check(blind.startswith("42 running, 5 waiting on you, 0 queued;") and "parked" not in blind, "negative control: counting every record reads 42 running and nothing parked (%s)" % blind.split(";")[0])
sys.exit(1 if failed else 0)
