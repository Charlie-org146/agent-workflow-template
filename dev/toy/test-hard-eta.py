#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-delivery/scripts/fit.py skills/workflow-delivery/scripts/goal.py skills/workflow-delivery/scripts/flow.py skills/workflow-delivery/scripts/guards.py
# reads: skills/workflow-monitoring/scripts/auto.py skills/workflow-monitoring/scripts/checkin.py skills/workflow-monitoring/scripts/proctree.py
# reads: skills/workflow-health/scripts/rules.py skills/workflow-health/scripts/controls.py skills/workflow-health/scripts/report.py
"""GRD-14: a goal's ETA is a hard limit (owner o52). Calls the real functions in throwaway repos: no model, no network.

1. Freeze records the ETA (the estimate plus a margin) and the goal file shows it.
2. Past the ETA no step starts, the goal waits under Needs you with three choices, and full auto never answers it.
3. goal.py set moves the ETA or raises a budget only with an owner-words record that covers the goal and was never used.
4. Ship now skips what is left, defer retires the goal, an extension lets it run on.
5. The check-in shows each goal's ETA; health warns on no ETA and fails on an extension without a record or an overrun
   that is not under Needs you (each rule's negative control fires)."""
import datetime
import json
import os
import subprocess
import sys
import tempfile
from types import SimpleNamespace

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
for skill in ("delivery", "monitoring", "health"):
    sys.path.insert(0, os.path.join(root, "skills", "workflow-" + skill, "scripts"))
os.environ.pop("LOOP_ROLE", None)
import fit  # noqa: E402
import goal as g  # noqa: E402
import auto  # noqa: E402
import controls  # noqa: E402
import proctree  # noqa: E402
import rules  # noqa: E402

failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def refused(call, *args, **more):
    try:
        call(*args, **more)
    except SystemExit as stop:
        return str(stop)
    return ""


def ago(minutes):
    return (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=minutes)).strftime("%Y-%m-%dT%H:%M:%SZ")


def sh(*args, cwd):
    subprocess.run(["git"] + list(args), cwd=cwd, check=True, capture_output=True)


def record(path, slug, state):
    os.makedirs(os.path.join(path, ".git", "loop", "runs"), exist_ok=True)
    with open(os.path.join(path, ".git", "loop", "runs", slug + ".json"), "w") as handle:
        json.dump(dict({"slug": slug}, **state), handle)


def read(path, slug):
    with open(os.path.join(path, ".git", "loop", "runs", slug + ".json")) as handle:
        return json.load(handle)


def words(path, *rows):
    with open(os.path.join(path, ".git", "loop", "owner-words.tsv"), "w") as handle:
        for n, ids in enumerate(rows, 1):
            handle.write("o%d\t2026-11-15T00:00:00Z\toperation\t%s\t%s\n" % (n, json.dumps("owner words"), ids))


def running(minutes, **more):
    return dict({"status": "running", "step": "build", "flow": {}, "log": [ago(minutes) + " start build"],
                 "eta": {"minutes": 60, "estimate": 48, "basis": "estimate 48m plus a 25% margin"}}, **more)


here = tempfile.mkdtemp(prefix="hard-eta-")
sh("init", "-q", "-b", "main", cwd=here)
sh("config", "user.email", "t@example.invalid", cwd=here)
sh("config", "user.name", "toy", cwd=here)
os.makedirs(os.path.join(here, ".loop"))
with open(os.path.join(here, ".loop", "config.json"), "w") as handle:
    json.dump({"base": "main", "time_budget_minutes": 240}, handle)
open(os.path.join(here, "README.md"), "w").write("toy\n")
sh("add", "-A", cwd=here)
sh("commit", "-q", "-m", "toy", cwd=here)
os.chdir(here)
runs = g.state_dir()

# 1. freeze: an ETA from the estimate (or the time budget when there is none), shown in the goal file
fields = fit.frozen_fields(g, SimpleNamespace(slug="x", goal="a toy goal"), ["1. one", "2. two"], [])
eta = fields["eta"]
check(isinstance(eta.get("minutes"), int) and eta["minutes"] >= 30 and eta["minutes"] % 5 == 0 and eta.get("basis"),
      "freezing a goal records a hard ETA in whole minutes (at least 30, to 5) with its basis: %s" % eta)
check(eta["minutes"] == 240 and "time budget" in eta["basis"], "with no finished goals to estimate from, the ETA is the time budget")
check("- ETA: %d active minutes" % eta["minutes"] in proctree.TEMPLATE.format(goal="g", slug="x", touches="t", eta=fit.eta_line(fields), done="1. one"),
      "the goal file holds an ETA line next to its done lines")
check(auto.ETA_MARGIN == 1.25, "the margin over the estimate is 25 percent")

# 2. the gate: past the ETA nothing starts, the goal waits under Needs you with three choices
record(here, "g", running(90))
state = read(here, "g")
said = refused(fit.budget_stop, "g", state, runs, {"time_budget_minutes": 240}, save=fit.run_saver(runs))
check("ETA_PAST" in said and "goal.py set g" in said and "--owner-record" in said, "a step past the ETA is refused naming goal.py set and an owner record: %s" % said[:90])
waiting = read(here, "g")
check(waiting["status"] == "waiting" and (waiting["waiting"] or {}).get("eta") is True, "the goal is put to waiting for the owner")
check(len(waiting["waiting"]["words"]) == 3 and "ship g now" in waiting["waiting"]["words"] and "defer g" in waiting["waiting"]["words"]
      and any(w.startswith("extend g by") for w in waiting["waiting"]["words"]), "Needs you offers ship now, extend and defer")
check(auto.why_not(waiting["waiting"], {}) != "", "full auto never answers the ETA question: %s" % auto.why_not(waiting["waiting"], {}))
check(refused(fit.budget_stop, "g", running(30), runs, {"time_budget_minutes": 240}) == "", "a goal inside its ETA starts its step")
check(refused(fit.budget_stop, "g", {"slug": "g", "status": "running", "log": [ago(500) + " start build"]}, runs, {}) == "", "a goal frozen without an ETA is not stopped by one")

# 3. goal.py set: an extension or a budget raise needs an owner-words record that covers the goal, once
args = dict(slug="g", depth=None, bump=None, budget_minutes=None, budget_tokens=None, eta_extend=None, eta_choice=None, owner_record="", why="owner said so")


def run_set(**more):
    return refused(fit.cmd_set, g, SimpleNamespace(**dict(args, **more)))


check("ETA_NO_RECORD" in run_set(eta_extend=30), "extending the ETA with no record is refused")
check("ETA_NO_RECORD" in run_set(eta_extend=30, owner_record="o9"), "extending with a record that does not exist is refused")
words(here, "other-goal", "g,Guardrails")
check("ETA_NO_RECORD" in run_set(eta_extend=30, owner_record="o1"), "a record that covers another goal does not count")
check("ETA_NO_RECORD" in run_set(budget_minutes=400), "raising a time budget with no record is refused")
check("ETA_NO_RECORD" in run_set(budget_tokens=0, budget_minutes=None) or run_set(budget_tokens=0) == "", "removing a token limit is a raise too, or there was none to remove")
check(run_set(budget_minutes=120) == "", "lowering a time budget needs no record")
check(read(here, "g")["status"] == "waiting", "a refused extension changes nothing")
check(run_set(eta_extend=45, owner_record="o2") == "", "an extension with a covering record is accepted")
state = read(here, "g")
check(state["status"] == "running" and state["waiting"] is None, "an extension lets the waiting goal go on")
seen = fit.view(state, runs)
check(auto.eta_minutes(seen) == 105 and seen["eta_extend"][0]["record"] == "o2", "the ETA is the frozen minutes plus the extension, with its record kept")
check("ETA_NO_RECORD" in run_set(eta_extend=15, owner_record="o2"), "a record is used once")
check(refused(fit.budget_stop, "g", state, runs, {}) == "", "inside the extended ETA the goal starts a step again")
words(here, "g", "g", "g")
check(run_set(budget_minutes=480, owner_record="o3") == "" and fit.view(read(here, "g"), runs)["budget"]["record"] == "o3", "a budget raise with a record is accepted and keeps it")

check(run_set(budget_minutes=300) == "" and "ETA_NO_RECORD" in run_set(budget_minutes=600, owner_record="o3"), "a record that raised a budget stays used after a later lowering")
check("not both" in run_set(eta_extend=5, eta_choice="ship", owner_record="o1"), "an extension and a choice together are refused")

record(here, "old", {"status": "running", "step": "build", "log": [ago(90) + " start build"]})
words(here, "x", "x", "x", "x", "x", "x", "old")
check(refused(fit.budget_stop, "old", read(here, "old"), runs, {}) == "", "a goal frozen before ETAs existed is not stopped")
check(refused(fit.cmd_set, g, SimpleNamespace(**dict(args, slug="old", eta_extend=60, owner_record="o7"))) == "", "an owner record gives such a goal an ETA")
check(auto.eta_minutes(fit.view(read(here, "old"), runs)) == 60 and refused(fit.budget_stop, "old", read(here, "old"), runs, {}) == "", "inside that ETA it runs on")
check("ETA_PAST" in refused(fit.budget_stop, "old", dict(read(here, "old"), log=[ago(120) + " start build"]), runs, {}), "past that ETA it is stopped like any other")

# 4. ship now and defer
record(here, "s", running(90, flow={"idea": "done", "plan": "done"}))
words(here, "s", "s")
check(refused(fit.cmd_set, g, SimpleNamespace(**dict(args, slug="s", eta_choice="ship", owner_record="o1"))) == "", "ship now is accepted with a record")
state = read(here, "s")
check(all(str(state["flow"].get(step, "")).startswith(("done", "skipped")) for step in fit.STEPS) and "ETA" in state["flow"]["ship"],
      "ship now records every step left as skipped, naming the ETA and the record")
check(refused(fit.budget_stop, "s", state, runs, {}) == "", "after ship now the pull request may go on past the ETA")
record(here, "d", running(90))
words(here, "s", "x", "x", "x", "d")
check(refused(fit.cmd_set, g, SimpleNamespace(**dict(args, slug="d", eta_choice="defer", owner_record="o5"))) == "", "defer is accepted with a record")
check(read(here, "d")["status"] == "retired" and "next release" in read(here, "d")["retired"]["reason"], "defer retires the goal for the next release")

# 5. the check-in shows the ETA; health reads the three rules
at = datetime.datetime.now(datetime.timezone.utc)
check(auto.eta_text(running(10), at).startswith("ETA ") and auto.eta_text(running(90), at) == "ETA passed" and auto.eta_text({}, at) == "no ETA",
      "the check-in cell reads a clock time, ETA passed, or no ETA")
check('auto.eta_text(auto.eta_seen(g["root"], run), at)' in open(os.path.join(root, "skills", "workflow-monitoring", "scripts", "checkin.py")).read(),
      "checkin.py puts it in the All sessions table")
names = {r: [rule for rule, _, _ in auto.eta_rows(here, at) if rule == r] for r in ("eta-missing", "eta-extended", "eta-overrun")}
fresh = tempfile.mkdtemp(prefix="hard-eta-health-")
sh("init", "-q", "-b", "main", cwd=fresh)
record(fresh, "a", {"status": "running", "step": "build", "log": [ago(10) + " start build"]})
record(fresh, "b", running(200))
record(fresh, "c", running(10))
open(os.path.join(fresh, ".git", "loop", "runs", "c.extra.json"), "w").write(json.dumps({"set": {"eta_extend": [{"by": 5, "record": "o7"}]}}))
found = auto.eta_rows(fresh, at)
check(("eta-missing", "WARN") in [(r, level) for r, level, _ in found] and "a has no ETA" in [t for _, _, t in found],
      "health warns on a live goal with no ETA")
check(any(r == "eta-extended" and level == "FAIL" and t.startswith("c ") for r, level, t in found), "health fails on an ETA extended without a record")
check(any(r == "eta-overrun" and level == "FAIL" and t.startswith("b ") for r, level, t in found), "health fails on an overrun goal that is not under Needs you")
record(fresh, "b", running(200, status="waiting", waiting={"ask": "x", "eta": True}))
check(not any(r == "eta-overrun" for r, _, _ in auto.eta_rows(fresh, at)), "an overrun goal waiting under Needs you is clean")
for rule in ("eta-missing", "eta-extended", "eta-overrun"):
    check(rule in controls.CONTROLS and rule in rules.FUNCTIONS, "health has %s with its negative control" % rule)

print("")
print("hard-eta: %d failed" % len(failed) if failed else "hard-eta: all passed")
sys.exit(1 if failed else 0)
