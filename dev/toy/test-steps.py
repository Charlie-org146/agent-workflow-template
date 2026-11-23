#!/usr/bin/env python3
# reads: skills/steps.py skills/workflow-delivery/scripts/goal.py skills/workflow-release/scripts/release.py
# reads: skills/workflow-monitoring/scripts/sessions.py skills/workflow-docs/scripts/steps_page.py dev/package.py
# reads: skills/workflow-setup/scripts/update.py skills/workflow-delivery/scripts/moved.py
# windows: skip (fcntl)
"""DEL-19 (v110-fast-steps-2): one toy, every case, each printing `CASE <name> PASS|FAIL`; the regression row greps every name,
so a case that never ran fails the row. Each case has a good fixture and a fixture that breaks only its own rule.
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
sys.path.insert(0, SKILLS)
steps = importlib.import_module("steps")
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
tmp = tempfile.mkdtemp()
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
    repo = tempfile.mkdtemp()
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
tmp_root = tempfile.mkdtemp()
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

# 7. causes: only exact keys are read or recorded
case("cause-key-shape", steps.KEY.match("merge:HEAD_MOVED") and not steps.KEY.match("../x:failed") and not steps.KEY.match("merge:lower"))
case("cause-off-list-step-is-freeze", steps.add_cause(c1 := {}, "zzz", "boom (SOME_CODE)") and c1["causes"][0]["key"] == "freeze:SOME_CODE" and steps.add_cause(c2 := {}, "-", "") and c2["causes"][0]["key"] == "freeze:failed" and steps.add_cause({}, "pr", "boom (SOME_CODE)"))
st = {"slug": "c", "step": "build", "status": "running", "log": []}
tmpc = os.path.join(tempfile.mkdtemp(), "runs", "c.json")
steps.commit(tmpc, st, "2026-11-22T10:00:00Z")
stale = json.load(open(tmpc))
later = json.load(open(tmpc))
later.update(status="done")
steps.commit(tmpc, later, "2026-11-22T10:05:00Z")
stale["status"] = "running"
steps.commit(tmpc, stale, "2026-11-22T10:06:00Z")
case("commit-stale-copy-keeps-disk-clock", sum(1 for l in json.load(open(tmpc))["log"] if " end build:" in l) == 1, str(json.load(open(tmpc))["log"]))

# 8. the board's own numbers do not move because of the new log lines (N1)
import datetime
base_log = ["2026-11-22T10:00:00Z start idea", "2026-11-22T10:10:00Z idea done", "2026-11-22T10:20:00Z start plan", "2026-11-22T10:30:00Z plan done",
            "2026-11-22T10:40:00Z session report: worker · x: held at build", "2026-11-22T11:10:00Z resumed", "2026-11-22T11:20:00Z start build"]
extra_log = []
for line in base_log:
    extra_log.append(line)
    if line.endswith("idea done"):
        extra_log.append("2026-11-22T10:10:00Z end idea: 10m active, tokens not reported, done")
    if line.endswith("held at build"):
        extra_log.append("2026-11-22T10:40:00Z began plan")
at = datetime.datetime(2026, 11, 22, 12, 0, tzinfo=datetime.timezone.utc)
board_before = board_log.flow_seconds({"log": base_log, "status": "running", "step": "build"}, at)
board_after = board_log.flow_seconds({"log": extra_log, "status": "running", "step": "build"}, at)
case("board-numbers-unchanged", board_before == board_after and bool(board_before), "%s != %s" % (board_before, board_after))

# 9. a goal left unreleased: its merge ends
left = run_state("release", "done", release="leave", step_clock={"step": "pr", "since": "2026-11-22T10:00:00Z", "active_s": 0})
steps.transition({"step": "release", "status": "done", "release": "leave"}, left, "2026-11-22T10:20:00Z")
waiting = run_state("release", "done", step_clock={"step": "pr", "since": "2026-11-22T10:00:00Z", "active_s": 0})
steps.transition({"step": "release", "status": "done"}, waiting, "2026-11-22T10:20:00Z")
case("merge-ends-for-a-left-goal", any(" end pr:" in l for l in left["log"]) and not any(" end pr:" in l for l in waiting["log"]), str((left["log"], waiting["log"])))

# 10. filing is off; one fix per cause; the one list names the steps in reports
case("filer-writes-nothing", "subprocess.run([\"gh\"" not in text("skills/workflow-docs/scripts/steps_page.py") and "issue" not in text("skills/workflow-docs/scripts/steps_page.py").replace("issues", ""))
case("fix-per-cause", sp.fix_for("merge:failed") != sp.fix_for("merge:HEAD_MOVED") and sp.fix_for("freeze:failed") != sp.fix_for("plan:failed")
     and "(SOME_CODE)" in sp.fix_for("tests:SOME_CODE"), "two causes share a fix")

# 11. a new script that writes JSON must be looked at: every one now writing it is named here (run records go through steps.commit or goal.save)
WRITES = ['audit.py', 'board_lines.py', 'board_model.py', 'controls.py', 'docs.py', 'flow.py', 'govern_hook.py', 'graph.py', 'guards.py', 'lane.py', 'lanekit.py', 'lanes.py', 'layers.py', 'machines.py', 'mailbox.py', 'mend.py', 'monitor.py', 'notify.py', 'replan.py', 'review.py', 'routing.py', 'sessions.py', 'settings.py', 'steps.py', 'sync.py', 'unattended.py', 'update.py', 'workflows.py']
found_writers = sorted({n for dp, _d, fs in os.walk(SKILLS) for n in fs if n.endswith(".py") and "json.dump(" in open(os.path.join(dp, n)).read()})
case("writers-are-all-known", found_writers == WRITES, "new or gone JSON writers: %s" % sorted(set(found_writers) ^ set(WRITES)))

# 12. a record written as write(path, json.dumps(...)) must not appear outside the known non-record files
FORMS = re.compile(r"\bwrite\([^\n]*json\.dumps\(|handle\.write\(json\.dumps\(")
KNOWN_FORMS = ['agents.py', 'auto.py', 'board.py', 'board_page.py', 'board_status.py', 'controls.py', 'defects.py', 'goal.py', 'govern_hook.py', 'lane.py', 'narrow.py', 'operate.py', 'reply_hook.py', 'setup.py', 'slots.py', 'unattended.py']
found_forms = sorted({n for dp, _d, fs in os.walk(SKILLS) for n in fs if n.endswith(".py") and FORMS.search(open(os.path.join(dp, n)).read())})
case("writers-by-dumps-are-known", found_forms == KNOWN_FORMS, "new or gone write(json.dumps) users: %s" % sorted(set(found_forms) ^ set(KNOWN_FORMS)))

# 13. a step stays open across saves until the step changes (autorelease.finish's save order)
seq = run_state("after the merge", "done", log=["2026-11-22T10:00:00Z began after the merge"], release="cut")
seq["step_clock"] = {"step": "after the merge", "since": "2026-11-22T10:00:00Z", "active_s": 0}
prev = dict(seq, step_clock=dict(seq["step_clock"]))
for at in ("2026-11-22T10:05:00Z", "2026-11-22T10:10:00Z"):
    cur = dict(prev, step_clock=dict(prev["step_clock"]))
    steps.transition(dict(prev), cur, at)
    prev = cur
cur = dict(prev, step="release", step_clock=dict(prev["step_clock"]))
steps.transition(dict(prev), cur, "2026-11-22T10:16:00Z")
fin = dict(cur, steps_done=True, step_clock=dict(cur["step_clock"]))
steps.transition(dict(cur), fin, "2026-11-22T10:20:00Z")
rows_seq = {r["step"]: r for r in steps.entries(fin)}
case("a-step-stays-open-across-saves", rows_seq["after the merge"]["minutes"] == 16 and rows_seq["after the merge"]["attempts"] == 1 and rows_seq["release"]["minutes"] == 4,
     str({k: (v["minutes"], v["attempts"]) for k, v in rows_seq.items() if v["state"] != "not run"}))

# 14. a copy loaded before the disk record's last step change cannot move the step or status back
tmps = os.path.join(tempfile.mkdtemp(), "runs", "st.json")
steps.commit(tmps, run_state("build", "running", log=[]), "2026-11-22T10:00:00Z")
stale_copy, fresh = json.load(open(tmps)), json.load(open(tmps))
fresh.update(step="tests")
steps.commit(tmps, fresh, "2026-11-22T10:10:00Z")
stale_copy["note"] = "late"
steps.commit(tmps, stale_copy, "2026-11-22T10:11:00Z")
after = json.load(open(tmps))
case("a-stale-copy-cannot-move-the-step-back", after["step"] == "tests" and after.get("note") == "late", str((after["step"], after.get("note"))))

# 15. layers: a done goal at "after the merge" is a pending merge, not a worker
layers = importlib.import_module("layers")
with tempfile.TemporaryDirectory() as tmp:
    repo = os.path.join(tmp, "r")
    subprocess.run(["git", "init", "-q", "-b", "main", repo], check=True)
    os.makedirs(os.path.join(repo, ".git", "loop", "runs"))
    for slug, step, num in (("late-goal", "after the merge", 3), ("pr-goal", "release", 4)):
        json.dump({"slug": slug, "status": "done", "step": step, "pr": "https://example.test/pull/%d" % num}, open(os.path.join(repo, ".git", "loop", "runs", slug + ".json"), "w"))
    built = layers.build(os.path.join(repo, ".git"), {})
case("layers-list-after-the-merge-as-a-pending-merge", sorted(m["slug"] for m in built["merges"]) == ["late-goal", "pr-goal"] and not built["workers"], str(built["merges"]))

# 16. lanekit.hit saves through the hook, reading inside the lock
lanekit = importlib.import_module("lanekit")
hit_path = os.path.join(tempfile.mkdtemp(), "hk.json")
steps.commit(hit_path, run_state("build", "running", log=["2026-11-22T10:00:00Z first"], slug="hk"), "2026-11-22T10:00:00Z")
lanekit.hit(os.path.dirname(hit_path), "hk", "build", "step", 10, "2m")
hit_rec = json.load(open(hit_path))
case("budget-hit-saves-through-the-hook", hit_rec.get("budget_hits") and any("first" in l for l in hit_rec["log"]) and hit_rec["step_clock"]["since"] > "2026", str(hit_rec.get("step_clock")))

print("ALL PASS" if not failed else "FAILED: %s" % ", ".join(failed))
sys.exit(1 if failed else 0)
