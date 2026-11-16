#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-delivery/scripts/fit.py skills/workflow-monitoring/scripts/board_log.py skills/workflow-monitoring/scripts/auto.py
"""MON-4, issue 4534: a goal's minute budget charges only time a step is running. Calls goal.py's own budget gate
(fit.budget_stop) on fixture run records: no model, no network.

1. A pause (goal.py wait, a session report that says waiting or paused) is never charged: 30 minutes run, 300 paused,
   20 run is 50; the same goal running 350 minutes with no pause is 350 and a budget under it stops it.
2. A session silent past the idle limit with no step running stops being charged until its next entry; a step that runs
   that long is charged in full.
3. goal.py show prints the charged and the wall minutes."""
import datetime
import json
import os
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
for skill in ("delivery", "monitoring"):
    sys.path.insert(0, os.path.join(root, "skills", "workflow-" + skill, "scripts"))
os.environ.pop("LOOP_ROLE", None)
os.environ.pop("LOOP_SESSION_QUIET", None)
import fit  # noqa: E402

failed = []
T0 = datetime.datetime(2026, 11, 16, 0, 0, tzinfo=datetime.timezone.utc)


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def log(*rows):
    return ["%s %s" % ((T0 + datetime.timedelta(minutes=m)).strftime("%Y-%m-%dT%H:%M:%SZ"), text) for m, text in rows]


def charged(rows, minutes, step="build"):
    """The budget gate's minutes for a running goal whose log is rows, read `minutes` after the start."""
    return fit.active_minutes({"slug": "x", "status": "running", "step": step, "log": log(*rows)}, T0 + datetime.timedelta(minutes=minutes), {})


def stops(rows, minutes, budget, step="build"):
    """The refusal fit.budget_stop gives a running goal with that minute budget, '' when it may start a step."""
    state = {"slug": "x", "status": "running", "step": step, "log": log(*rows), "budget": {"minutes": budget, "tokens": 0}}
    try:
        fit.budget_stop("x", state, None, {}, at=T0 + datetime.timedelta(minutes=minutes))
    except SystemExit as stop:
        return str(stop)
    return ""


# 1. held time
for name, wait in (("goal.py wait", "waiting: need the owner's word"), ("a session report that says waiting", "session report: worker · x: step plan, waiting"),
                   ("a session report that says paused", "session report: paused for PC memory")):
    rows = [(0, "start idea"), (30, "idea done (depth full)"), (30, wait), (330, "answered"), (330, "start plan"), (350, "plan done (depth full)")]
    check(charged(rows, 350) == 50, "%s: 30 minutes run, 300 held, 20 run is charged 50 (got %d)" % (name, charged(rows, 350)))
    check(stops(rows, 350, 60) == "" and "BUDGET_MINUTES" in stops(rows, 350, 50), "%s: the gate lets a 60 minute budget run and stops a 50 one" % name)
rows = [(0, "start idea"), (350, "idea done (depth full)")]
check(charged(rows, 350) == 350 and "BUDGET_MINUTES" in stops(rows, 350, 300), "control: a step that runs 350 minutes with no pause is charged 350 and a 300 minute budget stops it")

# 2. idle
rows = [(0, "start idea"), (30, "idea done (depth full)")]
check(charged(rows, 330) == 60, "a session silent for 300 minutes after a finished step is charged the idle limit (30), not 300 (got %d)" % charged(rows, 330))
check(stops(rows, 330, 100) == "", "the gate lets an idle goal start its next step under a 100 minute budget")
rows += [(330, "start plan"), (350, "plan done (depth full)")]
check(charged(rows, 350) == 80, "the goal is charged again from its next step (30 + 30 idle limit + 20 = 80, got %d)" % charged(rows, 350))
rows = [(0, "start idea"), (30, "idea done (depth full)"), (31, "session report: worker · x: step build, running"), (60, "session report: still building"), (90, "session report: still building")]
check(charged(rows, 90) == 90, "a worker that keeps reporting is charged for the time between reports (got %d)" % charged(rows, 90))
rows = [(0, "start qa")]
check(charged(rows, 350, "qa") == 350, "control: a step still running after 350 minutes (start qa, no end) is charged in full (got %d)" % charged(rows, 350, "qa"))
os.environ["LOOP_SESSION_QUIET"] = "3600"
check(charged([(0, "start idea"), (30, "idea done (depth full)")], 330) == 90, "the idle limit follows LOOP_SESSION_QUIET (3600s: 30 + 60 = 90)")
del os.environ["LOOP_SESSION_QUIET"]

# 3. goal.py show
with tempfile.TemporaryDirectory() as tmp:
    for args in (["init", "-q", "-b", "main", "."], ["config", "user.email", "t@example.test"], ["config", "user.name", "t"], ["commit", "-q", "--allow-empty", "-m", "base"]):
        subprocess.run(["git"] + args, cwd=tmp, check=True, capture_output=True)
    now = datetime.datetime.now(datetime.timezone.utc)
    stamp = lambda minutes_ago: (now - datetime.timedelta(minutes=minutes_ago)).strftime("%Y-%m-%dT%H:%M:%SZ")
    os.makedirs(os.path.join(tmp, ".loop"))
    with open(os.path.join(tmp, ".loop", "config.json"), "w") as handle:
        json.dump({"base": "main"}, handle)
    os.makedirs(os.path.join(tmp, ".git", "loop", "runs"))
    state = {"slug": "x", "status": "running", "step": "plan", "tries": 0, "flow": {}, "log": [stamp(300) + " start idea", stamp(270) + " idea done (depth full)"]}
    with open(os.path.join(tmp, ".git", "loop", "runs", "x.json"), "w") as handle:
        json.dump(state, handle)
    shown = subprocess.run([sys.executable, os.path.join(root, "skills", "workflow-delivery", "scripts", "goal.py"), "show", "x"], cwd=tmp,
                           capture_output=True, text=True, env=dict(os.environ, LOOP_ROLE="worker"))
    try:
        minutes = json.loads(shown.stdout).get("minutes") or {}
    except ValueError:
        minutes = {}
    check(minutes.get("charged") == 60 and minutes.get("wall") == 300, "goal.py show prints charged 60 and wall 300 minutes (got %s; %s)" % (minutes, shown.stderr.strip()[:120]))

sys.exit(1 if failed else 0)
