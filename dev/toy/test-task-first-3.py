#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-monitoring/scripts/schedule_load.py skills/workflow-monitoring/scripts/schedule_state.py skills/workflow-monitoring/scripts/schedule.py skills/workflow-monitoring/scripts/watch.py skills/workflow-monitoring/scripts/board.py
"""TSK-1, third toy: what the full-depth plan review found, each case RED on the head before its fix. A workaround's words face the
decision-kind, risky-path and always-ask checks before they are shown and activated; every cause passes the name scan on every channel;
held goals never take a slot from a safety goal; a first: key needs a real block; the JSON board keeps the schedule fields; real dispatch
(watch.plan, freeze, assign) follows the schedule; and TSK-1.4. Hermetic: temp repos, temp HOME, stub filer."""
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
from unittest import mock

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, "..", "..", "skills", "workflow-monitoring", "scripts"))
import schedule  # noqa: E402
import schedule_load as sl  # noqa: E402

failed = []
tmp = tempfile.mkdtemp()
os.environ.update(HOME=tmp, LOOP_PRIVATE_NAMES=os.path.join(tmp, "names"), FILER_LOG=os.path.join(tmp, "filer.log"),
                  SCHEDULE_FILER=sys.executable + " " + os.path.join(tmp, "filer.py"))
os.environ.pop("LOOP_ROLE", None)
open(os.path.join(tmp, "names"), "w").write("plantedname\n")
open(os.path.join(tmp, "filer.py"), "w").write("print('FILED backlog #7 ok')\n")
Q = ("- slug: v110-fix | goal: fix | done: d\n- slug: v110-a | release: v1.1.0 | depends-on: v110-fix | goal: a | done: d\n"
     "- slug: v110-b | release: v1.1.0 | goal: b | done: d\n")


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    ok or failed.append(text)


def repo(queue=Q, config=None, owner_rows=""):
    top = tempfile.mkdtemp(dir=tmp)
    git = lambda *a: subprocess.run(["git", "-C", top, *a], capture_output=True, text=True, check=True)
    git("init", "-q", "-b", "main")
    git("config", "user.email", "t@t")
    git("config", "user.name", "t")
    git("commit", "-q", "--allow-empty", "-m", "i")
    for d in (".loop/tasks", "docs", ".git/loop"):
        os.makedirs(os.path.join(top, d))
    open(os.path.join(top, ".loop", "queue.md"), "w").write(queue)
    open(os.path.join(top, ".loop", "config.json"), "w").write(json.dumps(config or {}))
    open(os.path.join(top, ".loop", "tasks", "t.md"), "w").write("# Task first\n\n- Release: v1.1.0\n- Goals: v110-a, v110-b\n")
    open(os.path.join(top, "docs", "release-brief-1.1.0.md"), "w").write("b\n")
    open(os.path.join(top, ".git", "loop", "owner-words.tsv"), "w").write("o123\tt\tw\tx\ty\n" + owner_rows)
    return top


def run(top, *argv):
    old = os.getcwd()
    os.chdir(top)
    out, err = io.StringIO(), io.StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = schedule.main(list(argv))
    finally:
        os.chdir(old)
    return code, out.getvalue(), err.getvalue()


def A(words, key="k1", live=True):
    return ["workaround", "add", key, "--fix", "v110-fix", "--applies", "v110-a", "--kind", "tool", "--feature", "TSK-1", "--found", "r1", words] + ["--live"] * live


# 1. SAFETY: the words face the decision-kind, risky-path and always-ask checks before they are shown and activated
for label, words, kw in (("a safety-class word (security, deletion)", "skip the security checks and delete the private data", {}),
                         ("a risky path", ".github/workflows/x.yml edit", {"config": {"risky_paths": ["^\\.github/"]}}),
                         ("an always-ask goal", "wait for the fix", {"owner_rows": "o9\tt\tw\tx\talways-ask:v110-a\n"})):
    top = repo(**kw)
    run(top, *A(words))
    code, out, err = run(top, "workaround", "use", "k1", "--goal", "v110-a")
    check(code == 2 and "SCHED-E15" in err and not sl.load(top)["waived"] and words not in out, "use refuses %s and activates nothing" % label)
top = repo()
run(top, *A("wait for the fix to merge"))
code, out, err = run(top, "workaround", "use", "k1", "--goal", "v110-a")
check(code == 0 and sl.load(top)["waived"] == {"v110-a": {"v110-fix"}}, "negative control: plain words activate")

# 1b. SAFETY (design H): order's record must be a real owner record whose covered ids include the goals ordered
rows = "o77\t2026-11-24T00:00:00Z\tsess\t\"words\"\tv110-other\n" + "o78\t2026-11-24T00:00:00Z\tsess\t\"words\"\tv110-fix,v110-a\n"
top = repo(owner_rows=rows)
code, out, err = run(top, "order", "v110-fix", "--by", "o999")
check(code == 2 and "SCHED-E08" in err and not os.path.exists(sl.paths(top)["order"]), "order refuses a made-up record id")
code, out, err = run(top, "order", "v110-fix", "--by", "o77")
check(code == 2 and "SCHED-E08" in err and not os.path.exists(sl.paths(top)["order"]), "order refuses a real record id that covers another scope")
code, out, err = run(top, "order", "v110-fix", "--by", "o123")
check(code == 2 and "SCHED-E08" in err and not os.path.exists(sl.paths(top)["order"]), "order refuses a malformed record (an id with no covered ids)")
code, out, err = run(top, "order", "v110-fix", "v110-a", "--by", "o78")
check(code == 0 and os.path.exists(sl.paths(top)["order"]), "negative control: a real record covering every goal ordered is accepted")
code, out, err = run(top, "order", "v110-fix", "v110-b", "--by", "o78")
check(code == 2, "a record that covers only some of the goals ordered is refused")

# 2. PRIVACY: every cause passes the name scan on every channel, stderr included
top = repo()
open(os.path.join(top, ".loop", "tasks", "plantedname.md"), "wb").write(b"\xff\x80")
code, out, err = run(top, "show")
check(code == 3 and "plantedname" not in out + err, "show hides a private name in an incomplete-input cause on stdout and stderr")
buf = io.StringIO()
with contextlib.redirect_stderr(buf):
    sl.warn(sl.load(top))
check("plantedname" not in buf.getvalue() and "SCHED-E10" in buf.getvalue(), "sl.warn keeps the code and the repair and hides the name on stderr")

# 2b. capacity: held goals are taken out BEFORE slots are allocated, so a held goal never takes the slot a safety goal needs
import watch  # noqa: E402
cap = repo("- slug: v110-late | goal: late | done: d\n- slug: v110-safe | first: safety: security | goal: s | done: d\n")
os.unlink(os.path.join(cap, ".loop", "tasks", "t.md"))
open(os.path.join(cap, ".git", "loop", "order.json"), "w").write("{torn")
old = os.getcwd()
os.chdir(cap)
try:
    with contextlib.redirect_stderr(io.StringIO()):
        start, held = watch.plan(1)
finally:
    os.chdir(old)
check([g["slug"] for g in start] == ["v110-safe"] and [g["slug"] for g, _ in held] == ["v110-late"], "with one slot and a torn order file the safety goal starts, the held goal waits: start %s held %s" % ([g["slug"] for g in start], [g["slug"] for g, _ in held]))

# 3. d1 (TSK-1.2): a first: key promotes a fix only when the fix really blocks that task goal
Q3 = ("- slug: v110-clean | first: v110-b: tidy first | goal: clean | done: d\n- slug: v110-fix | first: v110-a: it blocks | goal: fix | done: d\n"
      "- slug: v110-a | release: v1.1.0 | depends-on: v110-fix | goal: a | done: d\n- slug: v110-b | release: v1.1.0 | goal: b | done: d\n")
top = repo(Q3)
code, out, err = run(top, "show")
rows = [x.split(". ", 1)[1] for x in out.splitlines() if x[:3].strip().rstrip(".").isdigit()]
check([x.split(" | ")[0] for x in rows] == ["v110-fix", "v110-b", "v110-a", "v110-clean"], "an independent fix with first: stays behind the task goals, a real blocker goes first: %s" % [x.split(" | ")[0] for x in rows])
check("v110-clean" in out and "does not block" in out and "tidy first" not in out + err, "the ignored first: key is named with its goal and the why text is not printed")

# 4. d2: the JSON board keeps the loader's schedule fields, and a held goal is not "ready to start"
import board  # noqa: E402
import datetime  # noqa: E402
jb = repo(Q3)
rows, deps = board.collect("n", jb, "main", datetime.datetime.now(datetime.timezone.utc))
by = {d["slug"]: d for d in deps}
check(by["v110-fix"].get("kind") == "fix" and "ahead of" in by["v110-fix"].get("cell", "") and by["v110-b"].get("task") == "Task first" and by["v110-b"]["kind"] == "task", "the JSON board carries kind, task and the exact cell for each queued goal: %s" % {k: by["v110-fix"].get(k) for k in ("kind", "cell")})
open(os.path.join(jb, ".git", "loop", "order.json"), "w").write("{torn")
rows, deps = board.collect("n", jb, "main", datetime.datetime.now(datetime.timezone.utc))
check(all(str(d.get("waits_on")).startswith("held:") for d in deps if d["slug"] != "v110-x"), "a held goal's waits_on says held, never ready to start: %s" % [d["waits_on"][:30] for d in deps])
nb = repo(Q3)
os.unlink(os.path.join(nb, ".loop", "tasks", "t.md"))
rows, deps = board.collect("n", nb, "main", datetime.datetime.now(datetime.timezone.utc))
check(all("kind" not in d and "cell" not in d for d in deps), "with no task briefs the JSON board keeps today's keys (nothing added)")

# 5. d3: real dispatch (watch.plan, watch.freeze, sessions.assign) follows the schedule, frozen records keep the reason and the waiver, a revoked waiver is restored
import sessions  # noqa: E402


def at(top, fn, *a):
    old = os.getcwd()
    os.chdir(top)
    try:
        with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
            return fn(*a)
    finally:
        os.chdir(old)


Q1 = "- slug: v110-fix | goal: fix | done: d\n- slug: v110-b | release: v1.1.0 | goal: b | done: d\n"
d1 = repo(Q1)
start, held = at(d1, watch.plan, 1)
check([g["slug"] for g in start] == ["v110-b"], "TSK-1.1 real dispatch: with one slot the task goal starts before the fix: %s" % [g["slug"] for g in start])
state = at(d1, watch.freeze, start[0], {"base": "main"})
sched = state.get("schedule") or {}
check(sched.get("kind") == "task" and "task Task first" in sched.get("cell", ""), "the frozen record names the reason it started: %s" % sched)
check(at(d1, sessions.assign, state, "prompt", {}) is False and state.get("worker") == "background", "sessions.assign runs on the frozen record (no session tool set: a background worker)")
Q5 = ("- slug: v110-fix | goal: fix | done: d\n- slug: v110-a | release: v1.1.0 | depends-on: v110-fix | goal: a | done: d\n- slug: v110-b | release: v1.1.0 | goal: b | done: d\n")
d5 = repo(Q5)
runs_dir = os.path.join(d5, ".git", "loop", "runs")
start, held = at(d5, watch.plan, 3)
check("v110-a" not in [g["slug"] for g in start], "before any workaround the task goal waits on its fix: start %s" % [g["slug"] for g in start])
run(d5, *A("wait for the fix to merge"))
run(d5, "workaround", "use", "k1", "--goal", "v110-a")
start, held = at(d5, watch.plan, 3)
check("v110-a" in [g["slug"] for g in start], "TSK-1.3 real dispatch: an activated workaround starts the task goal while the fix is unmerged: %s" % [g["slug"] for g in start])
state = at(d5, watch.freeze, [g for g in start if g["slug"] == "v110-a"][0], {"base": "main"})
check((state.get("schedule") or {}).get("waived") == [{"key": "k1", "fix": "v110-fix"}], "the frozen record keeps the waiver's provenance: %s" % (state.get("schedule") or {}).get("waived"))
state["status"] = "running"
json.dump(state, open(os.path.join(runs_dir, "v110-a.json"), "w"))
code, out, err = run(d5, "workaround", "fail", "k1", "--goal", "v110-a", "--reason", "x")
now = json.load(open(os.path.join(runs_dir, "v110-a.json")))
check(now["status"] == "running" and "v110-fix" in now["waits_on"] and "k1" in str(now.get("schedule_revoked")), "a revoked waiver after assignment keeps the slot and restores the wait on the run record: waits_on %s, note %s" % (now.get("waits_on"), now.get("schedule_revoked")))

# 6. a CLOSED record is never revived by reconcile (its uses stay off)
import schedule_state as ss  # noqa: E402
cl = repo(Q5)
run(cl, *A("wait for the fix to merge"))
run(cl, "workaround", "use", "k1", "--goal", "v110-a")
run(cl, "workaround", "close", "k1", "--reason", "retired")
with mock.patch.object(ss, "lookup", lambda *a: 41):
    code, out, err = run(cl, "workaround", "reconcile", "k1")
state = json.loads(open(sl.paths(cl)["workaround"]).read())["state"]
check(state == "closed" and sl.load(cl)["waived"] == {}, "reconcile leaves a closed record closed and waives nothing: state %s" % state)

# 7. the short look: P1 every refusal prints the screened cause, P2 the task title is hidden with the marks, L3 a held list never holds a goal that already runs
p1 = repo()
open(os.path.join(p1, ".loop", "tasks", "plantedname.md"), "wb").write(b"\xff\x80")
for argv in (["order", "v110-fix", "--by", "o123"], A("words")):
    code, out, err = run(p1, *argv)
    check(code == 3 and "SCHED-E10" in err and "plantedname" not in out + err, "P1: `%s` refuses on an unreadable brief without printing the private name on stderr" % argv[0])
p2 = repo(Q3)
open(os.path.join(p2, ".loop", "tasks", "t.md"), "w").write("# plantedname Task\n\n- Release: v1.1.0\n- Goals: v110-a, v110-b\n")
rows, deps = board.collect("n", p2, "main", datetime.datetime.now(datetime.timezone.utc))
res = sl.load(p2)
check("plantedname" not in json.dumps(deps) and all("plantedname" not in json.dumps(g.get("sched")) for g in res["goals"]), "P2: a private name in a brief title is in no JSON board field and no frozen schedule field")
l3 = repo("- slug: v110-late | goal: late | done: d\n- slug: v110-safe | first: safety: security | goal: s | done: d\n")
os.unlink(os.path.join(l3, ".loop", "tasks", "t.md"))
open(os.path.join(l3, ".git", "loop", "order.json"), "w").write("{torn")
os.makedirs(os.path.join(l3, ".git", "loop", "runs"), exist_ok=True)
json.dump({"slug": "v110-late", "status": "running", "pid": os.getpid()}, open(os.path.join(l3, ".git", "loop", "runs", "v110-late.json"), "w"))
for fn in (watch.plan,):
    start, held = at(l3, fn, 3)
check("v110-late" not in [g["slug"] for g, _ in held] and "v110-late" not in [g["slug"] for g in start], "L3: a goal that already has a run record is in neither the start nor the held list when the order file is torn: held %s" % [g["slug"] for g, _ in held])

# 8. revocation is enforced at the next step: goal.py step refuses while the revoked waiver's fix is unmerged, and goes on once it merges
GOAL = os.path.join(here, "..", "..", "skills", "workflow-delivery", "scripts", "goal.py")
json.dump({"command": ["true"], "probe": ["true"], "probe_expect": "", "steps": {k: "s" for k in ("idea", "plan", "review", "qa", "ship")}}, open(os.path.join(tmp, "flow.json"), "w"))


def step(top):
    done = subprocess.run([sys.executable, GOAL, "step", "v110-a", "review"], cwd=top, capture_output=True, text=True, stdin=subprocess.DEVNULL,
                          env={"HOME": tmp, "PATH": os.environ["PATH"], "TERM": "dumb", "LOOP_FLOW": os.path.join(tmp, "flow.json"), "LOOP_ROLE": "worker"})
    return done.returncode, (done.stdout + done.stderr)[-300:]


code, said = step(d5)
check(code != 0 and "SCHED_REVOKED" in said, "goal.py step refuses a running goal whose workaround was revoked while its fix is unmerged: %s" % said.strip()[-120:])
json.dump({"slug": "v110-fix", "status": "done", "release": "merged"}, open(os.path.join(runs_dir, "v110-fix.json"), "w"))
code, said = step(d5)
check(code == 0 and "STEP v110-a review" in said, "once the fix has merged the goal goes on: %s" % said.strip()[-80:])

print("ALL PASS" if not failed else "%d FAILED" % len(failed))
sys.exit(1 if failed else 0)
