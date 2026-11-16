#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-delivery/scripts/fit.py skills/workflow-delivery/scripts/goal.py skills/workflow-monitoring/scripts/replan.py
# reads: skills/workflow-monitoring/scripts/auto.py skills/workflow-monitoring/scripts/graph.py skills/workflow-monitoring/scripts/checkin.py
"""eta-preflight (#4535): a goal asks every owner decision it can foresee once, at freeze, and its hard ETA starts at the answers.

Calls the real functions in a throwaway repo (no model, no network): fit.frozen_fields (what goal.py new stores), replan.preflight_lines
(the check-in's Needs-you line), auto.eta_text and eta_over (the ETA cell and the gate), fit.cmd_set --preflight (the owner's answers),
and goal.cmd_pr itself up to the queue join, through graph.pr_queue (a pr_join TypeError once slipped through tests that called the function)."""
import datetime
import io
import json
import os
import subprocess
import sys
import tempfile
from contextlib import redirect_stdout
from types import SimpleNamespace

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
for skill in ("delivery", "monitoring"):
    sys.path.insert(0, os.path.join(root, "skills", "workflow-" + skill, "scripts"))
sys.dont_write_bytecode = True
os.environ.pop("LOOP_ROLE", None)
import auto  # noqa: E402
import fit  # noqa: E402
import goal as g  # noqa: E402
import replan  # noqa: E402

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


def sh(*args, cwd):
    subprocess.run(["git"] + list(args), cwd=cwd, check=True, capture_output=True)


def ago(minutes):
    return (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=minutes)).strftime("%Y-%m-%dT%H:%M:%SZ")


def read(slug):
    with open(os.path.join(g.state_dir(), slug + ".json")) as handle:
        return json.load(handle)


def write(slug, state):
    with open(os.path.join(g.state_dir(), slug + ".json"), "w") as handle:
        json.dump(dict({"slug": slug}, **state), handle)


def config(**more):
    with open(os.path.join(here, ".loop", "config.json"), "w") as handle:
        json.dump(dict({"base": "main", "time_budget_minutes": 240}, **more), handle)


def freeze(**more):
    config(**more)
    return fit.frozen_fields(g, SimpleNamespace(slug="x", goal="a toy goal"), ["1. one"], ["docs"])["preflight"]["items"]


here = tempfile.mkdtemp(prefix="eta-preflight-")
sh("init", "-q", "-b", "main", cwd=here)
sh("config", "user.email", "t@example.invalid", cwd=here)
sh("config", "user.name", "toy", cwd=here)
os.makedirs(os.path.join(here, ".loop"))
os.makedirs(os.path.join(here, "docs", "wiki"))
open(os.path.join(here, "docs", "wiki", "Zebrapage.md"), "w").write("page\n")
open(os.path.join(here, "docs", "a.md"), "w").write("a\n")
sh("add", "-A", cwd=here)
sh("commit", "-q", "-m", "toy", cwd=here)
os.chdir(here)
names = os.path.join(here, "names.txt")
open(names, "w").write("# no names\n")
os.environ.update(LOOP_PRIVATE_NAMES=names, LOOP_FREE_GB="16", LOOP_API_QUOTA="5000")

# 1. freeze: plan approval and the time budget are always listed (plan only while auto_approve is off); a dry run only when it would refuse
items = freeze()
ids = [i["id"] for i in items]
check(ids == ["plan", "budget"], "a quiet goal lists its plan approval and its time budget: %s" % ids)
check(all(i["options"] and i["recommend"] in i["options"] for i in items), "every item has its options and a recommendation among them")
check([i["id"] for i in freeze(auto_approve=True)] == ["budget"], "negative control: with auto_approve on there is no plan-approval item")
check([i["id"] for i in freeze(min_free_memory_gb=0.5)] == ["plan", "budget"], "negative control: a memory floor below the free memory lists nothing")
os.environ["LOOP_FREE_GB"] = "1"
check("memory" in [i["id"] for i in freeze(min_free_memory_gb=4)], "a memory floor above the free memory is listed at freeze")
os.environ["LOOP_FREE_GB"] = "16"
open(names, "w").write("zebra\n")
hit = [i for i in freeze() if i["id"] == "private"]
check(len(hit) == 1 and "<private>" in hit[0]["ask"] and "Zebra" not in hit[0]["ask"], "a list line matching a page file name is listed, the name redacted: %s" % (hit[0]["ask"] if hit else ""))
open(names, "w").write("# no names\n")
check("private" not in [i["id"] for i in freeze()], "negative control: a clean list lists nothing")
os.environ["LOOP_API_QUOTA"] = "0"
check("quota" in [i["id"] for i in freeze()], "an empty GitHub API quota is listed")
os.environ["LOOP_API_QUOTA"] = "5000"
check("quota" not in [i["id"] for i in freeze()], "negative control: a full quota lists nothing")

# 2. the check-in line and the ETA cell: one line, the take-all word, "after your answers" until answered
items = freeze()
run = {"slug": "p", "status": "running", "step": "build", "flow": {}, "log": [ago(90) + " start build"],
       "eta": {"minutes": 60, "estimate": 48, "basis": "estimate 48m plus a 25% margin"}, "preflight": {"items": items}}
write("p", run)
at = datetime.datetime.now(datetime.timezone.utc)
lines = replan.preflight_lines([auto.eta_seen(here, run)])
check(len(lines) == 1 and lines[0].startswith("p pre-flight, 2 open") and '"recommended"' in lines[0] and "plan:" in lines[0] and "budget:" in lines[0],
      "the check-in puts the goal's whole list in one Needs-you line with the take-all word: %s" % (lines[0][:90] if lines else lines))
check(auto.eta_text(auto.eta_seen(here, run), at) == "ETA after your answers (2 open)", "the ETA cell reads 'after your answers (2 open)'")
check(not auto.eta_over(auto.eta_seen(here, run), 500) and refused(fit.budget_stop, "p", run, g.state_dir(), {}) == "",
      "with items open the ETA never trips, however long the goal has run")
check('replan.preflight_lines([auto.eta_seen(root, r) for r in live])' in open(os.path.join(root, "skills", "workflow-monitoring", "scripts", "checkin.py")).read(),
      "the check-in adds these lines to Needs you")
check(replan.preflight_lines([dict(run, preflight={"items": []})]) == [] and "ETA " in auto.eta_text(dict(run, preflight={}), at) and "after" not in auto.eta_text(dict(run, preflight={}), at),
      "negative control: a goal with no items has no line and the plain ETA (goals frozen before pre-flight read as before)")

# 3. the answers: owner words only, once; the ETA clock starts at the last answer
args = dict(slug="p", depth=None, bump=None, budget_minutes=None, budget_tokens=None, eta_extend=None, eta_choice=None, preflight="", owner_record="", why="owner said so")


def run_set(**more):
    return refused(fit.cmd_set, g, SimpleNamespace(**dict(args, **more)))


def words(*rows):
    with open(os.path.join(here, ".git", "loop", "owner-words.tsv"), "w") as handle:
        for n, ids in enumerate(rows, 1):
            handle.write("o%d\t2026-11-15T00:00:00Z\toperation\t%s\t%s\n" % (n, json.dumps("owner words"), ids))


check("ETA_NO_RECORD" in run_set(preflight="recommended"), "answering with no owner record is refused")
words("p", "p", "p")
check("not an open item" in run_set(preflight="nope=keep", owner_record="o1") and "not an open item" in run_set(preflight="budget=sideways", owner_record="o1"),
      "an answer for an unknown item or outside its options is refused")
said = run_set(preflight="plan=approve ahead", owner_record="o1")
check(said == "", "one item answered by its id: %s" % said[:200])
seen = fit.view(read("p"), g.state_dir())
check(len(auto.eta_open(seen)) == 1 and auto.eta_text(seen, at) == "ETA after your answers (1 open)" and not auto.eta_over(seen, 500),
      "one item left: the ETA still reads 'after your answers (1 open)' and does not trip")
check("ETA_NO_RECORD" in run_set(preflight="recommended", owner_record="o1"), "a record answers once")
check(run_set(preflight="recommended", owner_record="o2") == "", "the take-all word answers every item left")
seen = fit.view(read("p"), g.state_dir())
check(auto.eta_open(seen) == [] and seen["preflight_answers"]["answers"] == {"plan": "approve ahead", "budget": "keep"}, "every item is answered with its recommendation")
check(fit.plan_ahead(read("p"), g.state_dir(), "plan") and not fit.plan_ahead(read("p"), g.state_dir(), "build") and not fit.plan_ahead(run, g.state_dir(), "plan"),
      "goal.py record auto-approves a pending plan only after the owner answered plan=approve ahead (negative controls: another step, no answer)")
check(auto.eta_start(seen) >= 90 and auto.eta_text(seen, at).startswith("ETA ") and "after" not in auto.eta_text(seen, at),
      "the ETA has a clock time again: its clock started at the answers (the goal had run 90 minutes before)")
check(not auto.eta_over(seen, 100) and auto.eta_over(seen, 90 + 61), "past the ETA is counted from the answers, not from the start")
check(replan.preflight_lines([seen]) == [], "an answered list leaves Needs you")

# 4. goal.cmd_pr runs the dry runs again, through graph.pr_queue, and logs what the freeze list missed
lines = ["1. one"]


def goal_state(slug, **more):
    """A goal at pr with a real goal file (goal.py checks the frozen done lines) and its run record."""
    os.makedirs(os.path.dirname(g.goal_file(slug)), exist_ok=True)
    open(g.goal_file(slug), "w").write(g.TEMPLATE.format(goal="toy", slug=slug, touches="docs", eta="60 active minutes", done="\n".join(lines)))
    write(slug, dict({"status": "running", "step": "pr", "flow": {s: "done" for s in g.FLOW}, "log": [ago(5) + " start pr"], "touches": ["docs"], "goal": "toy",
                      "branch": "loop/" + slug, "done_sha": g.done_sha(lines), "eta": run["eta"], "preflight": {"items": freeze()}}, **more))


goal_state("q")
goal_state("z")  # an earlier goal at pr holds the turn, so goal.py pr stops at the wait and starts no lane
os.makedirs(os.path.join(g.state_dir(), "..", "pr-queue"), exist_ok=True)
open(os.path.join(g.state_dir(), "..", "pr-queue", "z"), "w").write("1")
open(os.path.join(g.state_dir(), "..", "pr-queue", "z.beat"), "w").close()


def pr(slug):
    out = io.StringIO()
    with redirect_stdout(out):
        try:
            g.cmd_pr(SimpleNamespace(slug=slug))
        except SystemExit as stop:
            return str(stop) + out.getvalue()
    return out.getvalue()


said = pr("q")
check("WAITING pr queue: z first" in said and "TypeError" not in said and not read("q").get("missed_preflight"),
      "negative control: goal.py pr on a clean dry run reaches its turn or a wait, logs no missed item: %s" % said[:100])
os.environ["LOOP_FREE_GB"] = "1"
config(min_free_memory_gb=4)
open(names, "w").write("zebra\n")
said = pr("q")
missed = {m["id"]: m for m in read("q").get("missed_preflight", [])}
check(set(missed) == {"memory", "private"} and "MISSED PRE-FLIGHT memory" in said and "WAITING pr queue: z first" in said,
      "goal.py pr's dry runs find the memory floor and the private-name hit that the freeze list did not have, and the pr queue still answers: %s" % sorted(missed))
check(all(m["why"].startswith("not on the freeze list") and m["at"] for m in missed.values()) and any("missed pre-flight item memory" in line for line in read("q")["log"]),
      "each is logged as a missed pre-flight item with why it was not foreseen, and in the run's log")
pr("q")
check(len(read("q")["missed_preflight"]) == 2, "negative control: a second pr does not log the same miss again")
goal_state("l", preflight={"items": [{"id": "memory", "ask": "x", "options": ["a"], "recommend": "a"}, {"id": "private", "ask": "x", "options": ["a"], "recommend": "a"}]})
pr("l")
check(not read("l").get("missed_preflight"), "negative control: an item that was on the freeze list is not a missed one")
check('queue("preflight", ME, state)' in open(os.path.join(root, "skills", "workflow-delivery", "scripts", "goal.py")).read() and
      'pods and pods.pr_queue("join", ME, state)' in open(os.path.join(root, "skills", "workflow-delivery", "scripts", "goal.py")).read(),
      "goal.py's pr runs the pre-flight dry runs before the queue join")
sys.exit(1 if failed else 0)
