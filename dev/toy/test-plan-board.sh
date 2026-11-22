#!/bin/bash
# reads: skills/workflow-delivery/scripts/planlevel.py skills/workflow-delivery/scripts/planfault.py skills/workflow-delivery/scripts/fit.py skills/workflow-delivery/scripts/fitkit.py
# reads: skills/workflow-delivery/scripts/guards.py skills/workflow-delivery/scripts/flow.py skills/workflow-monitoring/scripts/live_board.py
# DEL-22.5 and done line 7: after a plan the board shows each review's minutes and tokens (or "not reported", never zero); a review recorded at over
# twice its usual shows a flag (needs three earlier reviews of that name); an old state reads "no plan recorded"; a failed load reads "plan info
# unavailable"; and the moved code is byte-identical to main, fit.py still loads by path with no PYTHONPATH and still runs budget_stop, depth_for's
# text is unchanged, and every script this goal touches stays within its size limit. Own temp HOME; stand-ins only. usage: test-plan-board.sh
set -u
unset LOOP_SESSION_TOOL LOOP_OPERATION_SESSION CLAUDE_CODE_HOST_SESSION_ID CLAUDE_CODE_SESSION_ID CLAUDE_SESSION_ID LOOP_POD_ID PYTHONPATH
export LOOP_ROLE=worker
here=$(cd "$(dirname "$0")/../.." && pwd)
. "$here/dev/toy/reap.sh"
export HOME=$(mktemp -d) USERPROFILE="$HOME" LOOP_PRIVATE_NAMES=/dev/null
export TMPDIR="$HOME/tmp"; mkdir -p "$TMPDIR"
toy_on_exit 'rm -rf "$HOME"'
d="$HOME/repo"; mkdir -p "$d" && cd "$d" && git init -q -b main && git config user.email t@example.test && git config user.name Toy
: > f && git add -A && git commit -qm base; mkdir -p .git/loop/runs
export PLAN_HERE="$here" PLAN_SCRIPTS="$here/skills/workflow-delivery/scripts"
python3 - <<'PY'
import ast, json, os, subprocess, sys
sys.path.insert(0, os.environ["PLAN_SCRIPTS"])
import planlevel

fails = []
def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    ok or fails.append(text)

here, scripts = os.environ["PLAN_HERE"], os.environ["PLAN_SCRIPTS"]
runs = os.path.join(os.getcwd(), ".git", "loop", "runs")
planlevel.config = lambda top=None: {}
import fit

def stamps(goal, rows):
    json.dump({"version": 1, "goal": goal, "attempt": "1", "source": "runner", "reviews": rows}, open(os.path.join(runs, goal + ".plan-reviews.json"), "w"))

class Board:
    def __init__(self, seconds):
        self.s = seconds
    def seconds_by_step(self, run, at):
        return {"plan": self.s} if self.s is not None else {}

def record(goal, seconds, rows, level="normal"):
    fit.monitor = lambda *a, **k: Board(seconds)
    planlevel.save(goal, {"attempt": "1"})
    stamps(goal, rows)
    state = {"slug": goal, "plan": {"level": level, "rule": "one area, names DEL-22"}}
    planlevel.record(goal, state, "plan")
    return state, planlevel.note(goal, state)

# the board's lines
check(planlevel.note("none", {"slug": "none"}) == "no plan recorded", "an old state with no plan reads 'no plan recorded', not a level")
check("took" not in planlevel.note("none", {"slug": "none", "plan": {"level": "small", "rule": "r"}}), "a frozen goal with no recorded plan shows its level and rule only")
# seeded history: three earlier eng reviews of 10 seconds each
for i in range(3):
    json.dump({"record": {"reviews": [{"name": "eng", "seconds": 10.0}]}}, open(os.path.join(runs, "h%d.plan.json" % i), "w"))
state, line = record("g1", None, [{"name": "eng", "started": 0.0, "ended": 35.0}, {"name": "ceo", "started": 0.0, "ended": 12.0}])
check("took not reported of 30 min" in line, "minutes the board could not measure read 'not reported', never 0")
check("eng 35.0s, tokens not reported" in line and "ceo 12.0s, tokens not reported" in line, "each review shows its seconds, and its tokens read 'not reported' when none were recorded")
check("eng" in line and "FLAG: past twice its usual" in line.split("eng 35.0s")[1].split("\n")[0], "an eng review of 35 s against a usual of 10 s (three earlier reviews) shows the flag")
check("FLAG" not in line.split("ceo 12.0s")[1], "control: a ceo review with no history has no flag")
state, line = record("g2", None, [{"name": "eng", "started": 0.0, "ended": 12.0}])
check("FLAG" not in line, "control: an eng review of 12 s (not over twice 10 s) has no flag")
for i in range(2):
    json.dump({"record": {"reviews": [{"name": "solo", "seconds": 10.0}]}}, open(os.path.join(runs, "s%d.plan.json" % i), "w"))
state, line = record("g3", None, [{"name": "solo", "started": 0.0, "ended": 35.0}])
check("FLAG" not in line, "control: with only two earlier reviews there is no flag (the usual needs three)")
# the plan's own minutes come from the board's rule (held, owner-answer and stopped time are not counted)
import importlib
bs = fit.monitor.__call__ if False else None
state, line = record("g4", 600, [{"name": "eng", "started": 0.0, "ended": 5.0}], level="small")
check("took 10.0 of 10 min" in line and "MISSED" not in line, "ten minutes against the small limit of ten is not missed (the minutes are board_status.seconds_by_step's)")
state, line = record("g5", 660, [{"name": "eng", "started": 0.0, "ended": 5.0}], level="small")
check("MISSED: slowest review eng" in line, "control: eleven minutes against the small limit of ten is MISSED with its slowest review as the cause")
# the 2x history is the last 50 PLANS, chosen before reading: three hundred newer files of any other kind do not push it out
for i in range(3):
    json.dump({"record": {"reviews": [{"name": "deep", "seconds": 10.0}]}}, open(os.path.join(runs, "d%d.plan.json" % i), "w"))
    os.utime(os.path.join(runs, "d%d.plan.json" % i), (1, 1))
for i in range(300):
    open(os.path.join(runs, "noise-%d.txt" % i), "w").close()
state, line = record("g6", None, [{"name": "deep", "started": 0.0, "ended": 35.0}])
check("FLAG" in line, "three older plan records still make the 2x history under 300 newer files of other kinds")
# a record that fails is STORED and shown, never swallowed
saved = sys.modules.get("planlevel")
sys.modules["planlevel"] = None
failing = {"slug": "g7", "plan": {"level": "normal", "rule": "r"}}
fit.plan_keep(failing, "plan")
check(failing.get("plan_failed", "").startswith("plan info unavailable:"), "a failing record stores 'plan info unavailable: <class>' in the goal's state")
sys.modules["planlevel"] = saved
check("plan info unavailable" in fit.plan_note(failing) and "plan level normal" in fit.plan_note(failing), "the board shows the stored failure line beside the level")
fit.plan_keep({"slug": "g8", "plan": {"level": "normal", "rule": "r"}}, "plan")
# a failed load
saved = sys.modules.get("planlevel")
sys.modules["planlevel"] = None
check(fit.plan_note({"slug": "x"}).startswith("plan info unavailable:"), "a failed load reads 'plan info unavailable: <class>', a different line from 'no plan recorded'")
sys.modules["planlevel"] = saved
check(fit.plan_ask(type("A", (), {"step": "plan", "slug": "g"})(), "base text").startswith("base text"), "the plan prompt never fails: it returns the old text when planlevel cannot run")

# done line 7 and the moved code
def funcs(text, names):
    lines, out = text.splitlines(True), {}
    for n in ast.parse(text).body:
        if isinstance(n, ast.FunctionDef) and n.name in names:
            out[n.name] = "".join(lines[n.lineno - 1:n.end_lineno])
    return out
moved = ["surface", "area", "size_of", "deadline", "sidecar", "view", "pr_open", "main_here", "off_rows", "off_reply", "next_command"]
base = subprocess.run(["git", "-C", here, "show", "origin/main:skills/workflow-delivery/scripts/fit.py"], capture_output=True, text=True).stdout
kit = open(os.path.join(scripts, "fitkit.py")).read()
then = funcs(base, moved)
check(len(then) == len(moved) and all(code in kit for code in then.values()), "every moved helper is byte-for-byte what main's fit.py had (%d of %d found on main)" % (len(then), len(moved)))
check(funcs(open(os.path.join(scripts, "fit.py")).read(), ["depth_for"]) == funcs(base, ["depth_for"]), "fit.depth_for is unchanged: its why-string, which flow.py, role.py and the pull request read, did not move")
check(not any(n in funcs(open(os.path.join(scripts, "fit.py")).read(), moved) for n in moved), "control: none of the moved helpers is still defined in fit.py")
check("import fit" not in kit and "from fit" not in kit, "fitkit imports nothing from fit (no circular import)")
# fit.py loads by path in a fresh process with no PYTHONPATH, as the board loads it, and still runs budget_stop through that load
code = ("import importlib.util, json, sys; sp = importlib.util.spec_from_file_location('fit', %r); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m);"
        "m.budget_stop('g', {'slug': 'g', 'step': 'plan'}, %r, {}); print('LOADED', m.size_of(['a'], ['skills/x/y'])['small'], m.SURFACES[0])") % (os.path.join(scripts, "fit.py"), runs)
done = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env={"PATH": os.environ["PATH"], "HOME": os.environ["HOME"]}, cwd="/")
check(done.returncode == 0 and "LOADED True wiki" in done.stdout, "fit.py loads by path in a fresh process with no PYTHONPATH and runs budget_stop through that load (%s)" % (done.stderr.strip()[-120:] or "ok"))
# sizes
sizes = {"fit.py": 19000, "flow.py": 19000, "fitkit.py": 19000, "planlevel.py": 19000, "planfault.py": 19000, "guards.py": 20480}
for name, limit in sizes.items():
    n = os.path.getsize(os.path.join(scripts, name))
    check(n < limit if limit == 19000 else n <= limit, "%s is %d bytes, within %d" % (name, n, limit))
n = os.path.getsize(os.path.join(here, "skills/workflow-monitoring/scripts/live_board.py"))
check(n < 19000, "live_board.py is %d bytes, under 19,000" % n)
print("ALL PASS" if not fails else "%d FAILED" % len(fails))
sys.exit(1 if fails else 0)
PY
