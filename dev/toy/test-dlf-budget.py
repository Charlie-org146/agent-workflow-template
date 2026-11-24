#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-delivery/scripts/dlf.py skills/workflow-delivery/scripts/fit.py
"""DLF-1.2 (done line 2): the budget rule. New budget = max(held, min(spend + what is left, 2 x estimate)); 240 spent of 240 with 100
left goes to 340; remaining 0 gets a floor of 25 percent; past the cap the budget stays at the cap and one cap line is due; a held
budget above the cap is kept; zero tokens means unlimited. Calls dlf.raise_budget and dlf.budget_stop in a throwaway run record."""
import contextlib
import io
import json
import os
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
for skill in ("delivery", "monitoring"):
    sys.path.insert(0, os.path.join(root, "skills", "workflow-" + skill, "scripts"))
import dlf  # noqa: E402

failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


r = dlf.raise_budget
check(r(240, 240, 240, 140) == (340, False), "240 of 240 with 100 left goes to 340 and files no line")
check(r(360, 288, 360, 288) == (432, False), "remaining 0 with held 360, estimate 288, spend 360 gives 432 (floor of 25 percent) and no line")
check(r(480, 240, 480, 100) == (480, True), "spend at 2 x the estimate: the budget stays at the cap and the one cap line is due")
check(r(480, 240, 480, 100, finished=True) == (480, False), "a goal that finishes at the cap files none")
check(r(600, 240, 600, 100) == (600, True), "a held budget above the cap is kept, not lowered, and not raised")
check(r(400, 240, 400, 100) == (480, False), "a raise never takes the budget above 2 x the estimate")
check(r(0, 240, 500, 0) == (0, False), "a held budget of zero is unlimited: the rule does not apply")
check(r(240, 0, 240, 0) == (240, False), "no estimate: the rule does not apply")

# the real stop, in a throwaway repo: a goal at its budget keeps working and the raise is logged with both figures
tmp = tempfile.mkdtemp()
runs = os.path.join(tmp, "runs")
os.makedirs(runs)
import fit  # noqa: E402
import guards  # noqa: E402
fit.active_minutes = lambda state, at=None, cfg=None: 240
state = {"slug": "g1", "eta": {"minutes": 288, "estimate": 240, "basis": "x"}, "flow": {"idea": "done", "plan": "done", "build": "done"}, "log": []}
guards.add_set(runs, "g1", "budget", {"minutes": 240, "tokens": 0}, "set")
os.makedirs(os.path.join(tmp, ".loop"))
json.dump({"deliver_first": {}}, open(os.path.join(tmp, ".loop", "config.json"), "w"))
out = io.StringIO()
with contextlib.redirect_stdout(out):
    dlf.budget_stop("g1", state, runs, {}, top=tmp)
seen = fit.view(state, runs)
check(seen["budget"]["minutes"] > 240, "at 240 of 240 the stop does not refuse and the budget rises (%s)" % seen["budget"])
check("240 ->" in out.getvalue() and str(seen["budget"]["minutes"]) in out.getvalue(), "the raise prints the old and new figures: %s" % out.getvalue().strip())
check("raised the minutes budget 240 to" in json.dumps(guards.extra(runs, "g1")["log"]), "the raise is logged with both figures")
json.dump({"deliver_first": {"goal": {"g1": False}}}, open(os.path.join(tmp, ".loop", "config.json"), "w"))
guards.add_set(runs, "g1", "budget", {"minutes": 240, "tokens": 0}, "set")
try:
    dlf.budget_stop("g1", state, runs, {}, top=tmp)
    refused = ""
except SystemExit as stop:
    refused = str(stop)
check("BUDGET_MINUTES" in refused, "with the setting off the budget stop refuses as it always did: %s" % refused[:60])

# the ETA stop follows the raised budget, so a goal past its ETA keeps working (the health row eta-overrun agrees)
import auto  # noqa: E402
state2 = {"slug": "g2", "eta": {"minutes": 288, "estimate": 240, "basis": "x"}, "flow": {"idea": "done"}, "log": []}
fit.active_minutes = lambda state, at=None, cfg=None: 300
json.dump({"deliver_first": {}}, open(os.path.join(tmp, ".loop", "config.json"), "w"))
check(auto.eta_over(fit.view(state2, runs), 300), "a goal at 300 minutes is past its ETA of 288")
with contextlib.redirect_stdout(io.StringIO()):
    dlf.budget_stop("g2", state2, runs, {}, top=tmp)
check(not auto.eta_over(fit.view(state2, runs), 300), "after the raise the ETA stop no longer fires, and the goal keeps working")
sys.exit(1 if failed else 0)
