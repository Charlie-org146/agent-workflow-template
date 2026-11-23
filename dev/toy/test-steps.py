#!/usr/bin/env python3
# reads: skills/steps.py skills/workflow-delivery/scripts/goal.py skills/workflow-release/scripts/release.py
# reads: skills/workflow-monitoring/scripts/sessions.py skills/workflow-docs/scripts/steps_page.py dev/package.py
# reads: skills/workflow-setup/scripts/update.py skills/workflow-delivery/scripts/moved.py
# windows: skip (fcntl)
"""DEL-19 (v110-fast-steps-2), part 1 of 2 (part 2 is test-steps-more.py): the list, the log, the one writer, the hook, the pack, the
page and the rendered screens. Every case prints `CASE <name> PASS|FAIL`; the regression row greps every name of both parts, so a case that never ran fails the row.
A case that guards a rule against bad input runs it on a fixture that breaks only that rule (the cases named -refused or -break-).
usage: test-steps.py"""
import importlib
import sys
sys.dont_write_bytecode = True  # the shared file lives under skills/, where a cache folder would fail the package check
import json
import os
import re
import subprocess
import sys
import tempfile
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
SKILLS = os.path.join(ROOT, "skills")
sys.path[:0] = [SKILLS, os.path.join(SKILLS, "workflow-monitoring", "scripts")]
steps = importlib.import_module("steps")
import atexit
import shutil

_made = []


def mk():
    """A temp folder this toy makes; it is removed when the toy exits (absolute path, under the system temp root only)."""
    path = tempfile.mkdtemp()
    _made.append(path)
    return path


@atexit.register
def _clean():
    for path in _made:
        if os.path.isabs(path) and path.startswith(os.path.realpath(tempfile.gettempdir())) or path.startswith(tempfile.gettempdir()):
            shutil.rmtree(path, ignore_errors=True)


failed = []


def case(name, ok, why=""):
    print("CASE %s %s%s" % (name, "PASS" if ok else "FAIL", "" if ok else ": " + why))
    ok or failed.append(name)


def text(rel):
    return open(os.path.join(ROOT, rel)).read()


def run_state(step, status, log=None, **more):
    return dict({"slug": "t", "step": step, "status": status, "log": list(log or [])}, **more)


# 1. the list, defined once
case("list-eight-names", steps.STEPS == ("freeze", "plan", "build", "quick checks", "tests", "merge", "after the merge", "release"), str(steps.STEPS))
case("list-legacy-maps", all(steps.name_of(k) in steps.STEPS for k in steps.LEGACY) and steps.name_of("zzz") == "zzz")
sys.path[:0] = [os.path.join(SKILLS, "workflow-delivery", "scripts"), os.path.join(SKILLS, "workflow-monitoring", "scripts")]
flow, fit, proctree, board_log = (importlib.import_module(n) for n in ("flow", "fit", "proctree", "board_log"))
LISTS = {"flow.STEPS": flow.STEPS, "fit.STEPS": fit.STEPS, "proctree.FLOW": proctree.FLOW, "board_log.FLOW": board_log.FLOW}
moved_mon = importlib.import_module("moved_mon")
checkin = importlib.import_module("checkin")
import datetime


def check_in_rows(records):
    """The check-in's session rows for a throwaway repository holding these run records (a real checkin.render)."""
    with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as home:
        env = dict(os.environ, HOME=home, USERPROFILE=home, LOOP_MACHINE_NAME="pc", LOOP_PRIVATE_NAMES="/dev/null")
        root = os.path.join(tmp, "toyrepo")
        subprocess.run(["git", "init", "-q", "-b", "main", root], check=True, env=env)
        os.makedirs(os.path.join(root, ".loop"))
        os.makedirs(os.path.join(root, "docs", "wiki"))
        json.dump({"base": "main"}, open(os.path.join(root, ".loop", "config.json"), "w"))
        runs = os.path.join(root, ".git", "loop", "runs")
        os.makedirs(runs)
        now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        for rec in records:
            json.dump(dict({"goal": "A goal", "worker": "session", "pid": os.getpid(), "updated": now, "machine": "pc",
                            "report": {"at": now, "text": "working"}}, **rec), open(os.path.join(runs, rec["slug"] + ".json"), "w"))
        old = {k: os.environ.get(k) for k in env}
        os.environ.update(env)
        try:
            return "\n".join(checkin.render(root=root, at=datetime.datetime.now(datetime.timezone.utc), stamp="0000"))
        finally:
            for k, v in old.items():
                os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)


rows = check_in_rows([{"slug": "rev-goal", "status": "running", "step": "review"},
                      {"slug": "open-pr", "status": "done", "step": "release", "pr": "https://example.test/pull/7"}])
case("reports-derive-from-the-list", "tests 5/8" in rows and "review 4/8" not in rows, "the check-in names a review goal by the old list")
case("reports-name-an-open-pull-request-merge", "merge 6/8" in rows and "release 8/8" not in rows, "the check-in puts an open pull request at the old last step")
case("reports-break-on-a-label-off-the-list", moved_mon.shown({"step": "zzz", "status": "running"}, "zzz")[1] == 0)  # the fixture that breaks only the rule
case("list-bad-label-refused", subprocess.run([sys.executable, "-B", "-c", "import sys; sys.path.insert(0, %r); import steps; steps.check('build', 'bogus')" % SKILLS],
                                             capture_output=True, text=True).returncode != 0)

# 2. the step log
a = run_state("build", "running")
steps.transition({}, a, "2026-11-22T10:00:00Z")
b = dict(a, step_clock=dict(a["step_clock"]), status="done")
steps.transition(dict(a, status="running"), b, "2026-11-22T10:05:00Z")
rows = steps.entries(b)
build = [r for r in rows if r["step"] == "build"][0]
case("log-eight-rows", len(rows) == 8 and [r["step"] for r in rows] == list(steps.STEPS))
case("log-minutes", build["minutes"] == 5 and build["state"] == "ran" and build["tokens"] == "not reported", str(build))
c = run_state("build", "running")
steps.transition({}, c, "2026-11-22T10:00:00Z")
case("log-open-start", [r for r in steps.entries(c) if r["step"] == "build"][0]["state"] == "open")
x = run_state("build", "running")
steps.transition({}, x, "2026-11-22T10:00:00Z")
x1 = dict(x, step_clock=dict(x["step_clock"]))
steps.transition(dict(x, status="running"), x1, "2026-11-22T10:10:00Z")
x2 = dict(x1, status="waiting", step_clock=dict(x1["step_clock"]))
steps.transition(dict(x1, status="running"), x2, "2026-11-22T10:20:00Z")
x3 = dict(x2, step_clock=dict(x2["step_clock"]))
steps.transition(dict(x2), x3, "2026-11-22T15:00:00Z")
case("log-waiting-gap-not-counted", x3["step_clock"]["active_s"] == 1200, str(x3["step_clock"]))
e = run_state("build", "running")
steps.transition({}, e, "2026-11-22T10:00:00Z")
e2 = dict(e, step_clock=dict(e["step_clock"]), status="done")
steps.transition(dict(e, status="running"), e2, "2026-11-22T10:03:00Z")
e3 = dict(e2, step_clock=dict(e2["step_clock"]), status="running")
steps.transition(dict(e2), e3, "2026-11-22T11:00:00Z")
case("log-rerun-opens-new-start", sum(1 for l in e3["log"] if " began build" in l) == 2, str(e3["log"]))
g = run_state("build", "running", tokens={"build": {"input": 100, "output": 50}})
steps.transition({}, g, "2026-11-22T10:00:00Z")
g2 = dict(g, step_clock=dict(g["step_clock"]), status="done", tokens={"build": {"input": 400, "output": 150}})
steps.transition(dict(g, status="running"), g2, "2026-11-22T10:01:00Z")
case("log-tokens-per-attempt", any("tokens 400" in line for line in g2["log"]), str(g2["log"]))
many = run_state("freeze", "running")
steps.transition({}, many, "2026-11-22T10:00:00Z")
for i, name in enumerate(["plan", "build", "tests"] * 12):
    nxt = dict(many, step=name, step_clock=dict(many["step_clock"]))
    steps.transition(dict(many), nxt, "2026-11-22T10:%02d:00Z" % (i % 59 + 1))
    many = nxt
case("log-over-30-transitions", len(steps.entries(many)) == 8 and sum(r["attempts"] for r in steps.entries(many)) > 30)

# 3. one writer for every record writer
tmp = mk()
path = os.path.join(tmp, "runs", "x.json")
s1 = run_state("build", "running", log=["2026-11-22T10:00:00Z first"])
steps.commit(path, s1, "2026-11-22T10:00:00Z")
s2 = json.load(open(path))
s2["log"] = s2["log"] + ["2026-11-22T10:01:00Z second"]
other_writer = json.load(open(path))
other_writer["log"].append("2026-11-22T10:02:00Z third")
steps.commit(path, other_writer, "2026-11-22T10:02:00Z")
steps.commit(path, s2, "2026-11-22T10:03:00Z")
logs = json.load(open(path))["log"]
case("commit-log-lines-kept", all(any(x in l for l in logs) for x in ("first", "second", "third")), str(logs))
case("commit-writes-start-line", any(" began build" in l for l in logs))
errors = []


def writer(n):
    try:
        for i in range(10):
            st = json.load(open(path))
            st["log"] = st["log"] + ["2026-11-22T10:10:00Z w%d-%d" % (n, i)]
            steps.commit(path, st, "2026-11-22T10:10:00Z")
    except Exception as error:  # noqa: BLE001
        errors.append(error)


threads = [threading.Thread(target=writer, args=(n,)) for n in range(3)]
[t.start() for t in threads]
[t.join() for t in threads]
final = json.load(open(path))["log"]
case("commit-two-writers-lose-nothing", not errors and all(("w%d-%d" % (n, i)) in " ".join(final) for n in range(3) for i in range(10)), str(errors))
case("commit-bad-label-refused", subprocess.run([sys.executable, "-B", "-c", "import sys; sys.path.insert(0, %r); import steps; steps.commit(%r, {'slug': 'x', 'step': 'bogus', 'status': 'running'}, '2026-11-22T10:00:00Z')" % (SKILLS, path)],
                                               capture_output=True, text=True).returncode != 0)

# 4. every writer calls the one hook
SCR = {"goal": "workflow-delivery", "release": "workflow-release", "sessions": "workflow-monitoring"}


def real_save(mod, extra=""):
    """Run one real save of a record by the writer `mod` in a throwaway git repo; return the saved record's log."""
    repo = mk()
    env = dict(os.environ, HOME=repo, USERPROFILE=repo, LOOP_PRIVATE_NAMES="/dev/null", LOOP_ROLE="worker")
    for k in ("CLAUDE_CODE_HOST_SESSION_ID", "CLAUDE_CODE_SESSION_ID", "CLAUDE_SESSION_ID", "LOOP_POD_ID", "LOOP_OPERATION_SESSION"):
        env.pop(k, None)
    subprocess.run(["git", "init", "-q", repo], capture_output=True, env=env)
    code = ("import sys, json; sys.path.insert(0, %r); import %s as w; st = {'slug': 'hk', 'step': 'build', 'status': 'running', 'log': []}; %s"
            "w.save(st, 'one'); st['status'] = 'done'; w.save(st, 'two'); print(json.dumps(st['log']))") % (os.path.join(SKILLS, SCR[mod], "scripts"), mod, extra)
    done = subprocess.run([sys.executable, "-B", "-c", code], cwd=repo, capture_output=True, text=True, env=env)
    try:
        return json.loads(done.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return [done.stderr[-200:]]


for name in ("goal", "release", "sessions"):
    log = real_save(name)
    case("hook-%s-save" % name, any(" began build" in l for l in log) and any(" end build:" in l for l in log), str(log))
writers = []
for dirpath, _dirs, files in os.walk(SKILLS):
    for name in files:
        if name.endswith(".py"):
            body = open(os.path.join(dirpath, name)).read()
            if re.search(r'json\.dump\(state, handle', body) or re.search(r'os\.replace\(path \+ "\.tmp", path\)', body):
                writers.append(name)
case("hook-no-unrouted-writer", not [w for w in writers if w not in ("flow.py", "lanekit.py", "machines.py", "notify.py", "workflows.py")], "unrouted record writers: %s" % writers)

# 5. the package and the page
page = subprocess.run([sys.executable, "-B", os.path.join(SKILLS, "workflow-docs", "scripts", "steps_page.py"), "render"], capture_output=True, text=True).stdout
case("page-equals-render", page.strip() == text("docs/wiki/Steps.md").strip())
case("page-names-the-list", all(n in page for n in steps.STEPS))
sp = importlib.import_module("steps_page") if SKILLS + "/workflow-docs/scripts" in sys.path else None
sys.path.insert(0, os.path.join(SKILLS, "workflow-docs", "scripts"))
sp = importlib.import_module("steps_page")
sp.steps_module()
was = steps.STEPS
steps.STEPS = was + ("zzz",)
changed = sp.render()
steps.STEPS = was
tmp_root = mk()
os.makedirs(os.path.join(tmp_root, "docs", "wiki"))
open(os.path.join(tmp_root, "docs", "wiki", "Steps.md"), "w").write(text("docs/wiki/Steps.md"))
clean = sp.stale(tmp_root)
steps.STEPS = was + ("zzz",)
drift = sp.stale(tmp_root)
steps.STEPS = was
case("page-added-step-makes-docs-check-stale", clean == [] and len(drift) == 1 and "differs from the code" in drift[0], str((clean, drift)))

# 6. bytes (done line 3)
LIM = {}
for rel in ("skills/workflow-delivery/scripts/goal.py", "skills/workflow-release/scripts/release.py", "skills/workflow-monitoring/scripts/sessions.py",
            "skills/workflow-release/scripts/autorelease.py", "skills/workflow-docs/scripts/docs.py", "skills/workflow-regression/scripts/slots.py",
            "skills/steps.py", "skills/workflow-docs/scripts/steps_page.py"):
    LIM[rel] = len(open(os.path.join(ROOT, rel), "rb").read().replace(b"\r\n", b"\n"))
case("size-under-19000", all(n < 19000 for n in LIM.values()), str({k: v for k, v in LIM.items() if v >= 19000}))
case("size-update-not-grown", len(open(os.path.join(ROOT, "skills/workflow-setup/scripts/update.py"), "rb").read()) <= 19419)

# 27. rendered screens (part 2 of this file's cases): one toy repo with goals whose texts name steps by the older labels; every
# screen is rendered and read, and each case has a mutation that must fail it (run by the DEL-19 seen-red proof)
import argparse
import contextlib
import datetime
live_board, moved_mon, board, checkin, board_model = (importlib.import_module(n) for n in ("live_board", "moved_mon", "board", "checkin", "board_model"))
os.environ.update(HOME=mk(), LOOP_PRIVATE_NAMES="/dev/null", PYTHONDONTWRITEBYTECODE="1")  # child scripts leave no cache
repo = mk()
git = lambda *a: subprocess.run(["git", *a], cwd=repo, check=True, capture_output=True)
git("init", "-q"), git("config", "user.email", "t@t.t"), git("config", "user.name", "t"), open(os.path.join(repo, "f"), "w").write("x"), git("add", "."), git("commit", "-qm", "i")
subprocess.run([sys.executable, "-B", os.path.join(SKILLS, "workflow-setup", "scripts", "setup.py"), "--bare"], cwd=repo, check=True, capture_output=True)
os.makedirs(os.path.join(repo, ".git", "loop", "runs"))


def put(slug, status, step, text, **more):
    rec = dict({"slug": slug, "goal": "g", "step": step, "status": status, "worker": "session", "pid": os.getpid(), "updated": "2026-11-22T10:00:00Z",
                "reports": [{"at": "2026-11-22T09:30:00Z", "step": "review", "status": status, "text": text}], "log": ["2026-11-22T09:00:00Z start idea"]}, **more)
    json.dump(rec, open(os.path.join(repo, ".git", "loop", "runs", slug + ".json"), "w"))
    return rec


@contextlib.contextmanager
def nine():
    """The list one step longer, and always put back, even when a case raises."""
    was = steps.STEPS
    steps.STEPS = was + ("extra",)
    try:
        yield
    finally:
        steps.STEPS = was


goal = put("zz", "running", "zzz", "worker zz: step ship, running")
at = datetime.datetime(2026, 11, 22, 10, 5, tzinfo=datetime.timezone.utc)
os.chdir(repo)
screen = "\n".join(live_board.render(repo, at))
mon = "\n".join(checkin.render(repo, at, "0000"))
with nine():
    nine_screen, nine_mon = "\n".join(live_board.render(repo, at)), "\n".join(checkin.render(repo, at, "0000"))
case("the-bar-counts-the-lists-length", "- zz  [#####-----] 50%" in screen and "- zz  [####------] 44%" in nine_screen, str((screen.split("\n")[8:10], nine_screen.split("\n")[8:10])))
lines = mon.split("\n")
at_row = next((i for i, l in enumerate(lines) if l.startswith("| session worker") and "tests 5/8" in l), 0)
row = " ".join(l.strip() for l in lines[at_row:at_row + 2])  # the check-in wraps its table rows
case("the-checkin-says-the-list-name", "step tests" in row and "step ship" not in row, row)
flat = " ".join(nine_mon.split())
case("the-checkin-count-is-the-list-length", "| running | tests 5/9 |" in flat and "no PR yet | session worker · zz | tests 5/9" in flat, flat[:700])
was = board_model.stalled
board_model.stalled = lambda *a, **k: ("review", 200.0, 10.0)
try:
    stall = "\n".join(moved_mon.stall_lines([goal], at))
finally:
    board_model.stalled = was
case("the-stall-line-says-the-list-name", "zz is stalled: tests has run" in stall and "review" not in stall, stall)
out_file = os.path.join(mk(), "handoff.md")
board.cmd_handoff(argparse.Namespace(at=None, out=out_file))
hand = open(out_file).read()
case("the-handoff-names-the-last-known-step-not-the-label", "step tests" in hand and "step zzz" not in hand, hand[:600])
# a stored step reads the list's name in a CHANGE line, and a label change that is the same step is no change
case("change-lines-say-the-list-name", board.changes({"r/zz": {"step": "plan"}}, {"r/zz": {"step": "ship"}}) == ["CHANGE r/zz step: plan -> tests"]
     and board.changes({"r/zz": {"step": "qa"}}, {"r/zz": {"step": "ship"}}) == [], str(board.changes({"r/zz": {"step": "plan"}}, {"r/zz": {"step": "ship"}})))
# a waiting goal's report on the live board, and a failed goal's ask in the handoff, say the list's name
put("ww", "waiting", "build", "worker ww: step ship needs you")
put("ff", "failed", "build", "worker ff: step ship failed", report={"text": "worker ff: step ship failed"})
put("ww", "waiting", "build", "x", report={"text": "worker ww: step ship needs you"})
waiting = "\n".join(live_board.render(repo, at))
case("the-waiting-text-says-the-list-name", "ww is waiting: worker ww: step tests needs you" in waiting and "step ship needs you" not in waiting, waiting[:900])
board.cmd_handoff(argparse.Namespace(at=None, out=out_file))
hand = open(out_file).read()
case("the-failed-ask-says-the-list-name", "ff" in hand and "failed: worker ff: step tests failed" in hand and "step ship failed" not in hand, hand[-900:])

print("ALL PASS" if not failed else "FAILED: %s" % ", ".join(failed))
sys.exit(1 if failed else 0)
