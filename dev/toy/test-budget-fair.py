#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-delivery/scripts/fit.py skills/workflow-monitoring/scripts/board_log.py skills/workflow-monitoring/scripts/board_log.py
"""budget-fair (#4261): a pr lane lost to a moved base is held time, never charged to time_budget_minutes. Replays five
15-minute lanes that each end in `merge refused (exit 2)` (BASE_MOVED) and `main moved, try not counted`, against the real
fit.active_minutes / fit.budget_stop, and checks that a lane that really failed, and time truly spent on steps, stay charged."""
import datetime
import os
import sys

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
for part in ("workflow-delivery", "workflow-monitoring"):
    sys.path.insert(0, os.path.join(root, "skills", part, "scripts"))
import fit  # noqa: E402
import board_log  # noqa: E402

fails = 0
T0 = datetime.datetime(2026, 11, 14, 21, 0, 0, tzinfo=datetime.timezone.utc)


def check(name, ok):
    global fails
    print(("PASS: " if ok else "FAIL: ") + name)
    fails += 0 if ok else 1


def run(*entries):
    """A running goal at pr whose log entries are (minutes after freeze, text); 'now' is the last entry."""
    log = ["%s %s" % ((T0 + datetime.timedelta(minutes=m)).strftime("%Y-%m-%dT%H:%M:%SZ"), text) for m, text in entries]
    return {"slug": "g", "status": "running", "step": "pr", "log": log}, T0 + datetime.timedelta(minutes=entries[-1][0])


def minutes(*entries):
    state, at = run(*entries)
    return fit.active_minutes(state, at)


def stopped(state, at, budget):
    try:
        fit.budget_stop("g", state, "/none", {"time_budget_minutes": budget, "token_budget": 0}, at)
    except SystemExit as exit:
        return str(exit.code)
    return ""


STEPS = [(0, "frozen 1 done lines"), (5, "idea done"), (10, "plan done"), (15, "build done"), (20, "review done"), (25, "qa done"), (30, "ship done")]
LANE = 15  # a pr lane, in minutes


def lanes(count, ending="merge refused (exit 2): run goal.py pr, then merge.py again"):
    """count lanes after ship, each a 'pr' entry LANE minutes in, then a refusal two minutes later."""
    entries, now = list(STEPS), 30
    for _ in range(count):
        now += LANE
        entries.append((now, "pr"))
        now += 2
        entries.append((now, ending))
    return entries


check("five BASE_MOVED lanes leave only the 30 minutes of steps spent", minutes(*lanes(5)) == 30)
state, at = run(*lanes(5))
check("a 60 minute budget is not stopped by five lost lanes (it was, at 30 + 5 x 17 = 115)", stopped(state, at, 60) == "")
check("a 400 minute budget is not stopped by 24 lost lanes", stopped(*run(*lanes(24)), 400) == "")
check("`main moved, try not counted` is a lost lane as well", minutes(*STEPS, (45, "main moved, try not counted (1 of 5)")) == 30)
check("a lane that opens a pull request and merges still counts", minutes(*STEPS, (45, "pr"), (47, "merged https://x/pull/1 (auto_merge)")) == 47)
check("a lane that really failed (try N failed) stays charged", minutes(*STEPS, (45, "try 1 failed: regression lane failed: x")) == 45)
check("steps that ran before a refusal stay charged", minutes((0, "frozen 1 done lines"), (50, "build done"), (52, "merge refused (exit 2): run goal.py pr, then merge.py again")) == 50)
check("a goal that truly runs past its budget is still stopped, lost lanes or not", "minutes spent" in stopped(*run(*lanes(5), (200, "stopped: x"), (200, "start qa"), (400, "qa done")), 300))
real = [(0, "frozen 1 done lines")] + [(60 * i, "%s done" % s) for i, s in enumerate(("idea", "plan", "build", "review", "qa", "ship"), 1)]
check("a goal that truly runs 360 minutes of steps is stopped at 300", "360 minutes spent" in stopped(*run(*real), 300))
check("lost_lanes names the refusals and the pr lane before each", board_log.lost_lanes([m for m in ("t pr", "t merge refused (exit 2): x", "t try 1 failed", "t main moved, try not counted (1 of 5)")]) == {0, 1, 3})
sys.exit(1 if fails else 0)
