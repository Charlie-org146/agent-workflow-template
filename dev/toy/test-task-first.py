#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-monitoring/scripts/schedule_load.py skills/workflow-monitoring/scripts/schedule_state.py skills/workflow-monitoring/scripts/schedule.py skills/workflow-monitoring/scripts/graph.py
"""TSK-1 (task first): a goal from the owner's selected release comes before a fix, a fix goes first only on a named reason, a
workaround frees a task goal only when activated, the owner line reorders, and an unreadable input is loud and never idle.
Each blocking guard is shown RED first (the guard removed) and then GREEN. Hermetic: temp repos, temp HOME, a stub issue filer."""
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import time
from unittest import mock

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, "..", "..", "skills", "workflow-monitoring", "scripts"))
import graph  # noqa: E402
import schedule  # noqa: E402
import schedule_load as sl  # noqa: E402
import schedule_state as ss  # noqa: E402

failed = []
tmp = tempfile.mkdtemp()
os.environ.update(HOME=tmp, LOOP_PRIVATE_NAMES=os.path.join(tmp, "names"), SCHEDULE_FILER=sys.executable + " " + os.path.join(tmp, "filer.py"))
os.environ.pop("LOOP_ROLE", None)
open(os.path.join(tmp, "names"), "w").write("plantedname\n")
open(os.path.join(tmp, "filer.py"), "w").write("import os,sys\nopen(os.environ['FILER_LOG'],'a').write(' '.join(sys.argv[1:2])+'\\n')\nprint('FILED #7 ok')\n")
os.environ["FILER_LOG"] = os.path.join(tmp, "filer.log")
json.dump({"command": ["true"], "probe": ["true"], "probe_expect": "", "steps": {k: "s" for k in ("idea", "plan", "review", "qa", "ship")}}, open(os.path.join(tmp, "flow.json"), "w"))
os.environ["LOOP_FLOW"] = os.path.join(tmp, "flow.json")
QUEUE = ("- slug: v110-fix | goal: fix | done: d\n- slug: v110-a | release: v1.1.0 | goal: a | done: d\n- slug: v110-b | release: v1.1.0 | depends-on: v110-a | goal: b | done: d\n"
         "- slug: v110-dep | release: v1.1.0 | depends-on: v110-fix | goal: c | done: d\n- slug: v110-late | goal: late | done: d\n")


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    ok or failed.append(text)


def red(ok_when_broken, text):
    """The guard removed must make its check fail: this line is the RED proof."""
    print(("RED (seen): " if not ok_when_broken else "FAIL: no red, ") + text)
    ok_when_broken and failed.append("not red: " + text)


def repo(queue=QUEUE, briefs=True, branch="main", config=None):
    top = tempfile.mkdtemp(dir=tmp)
    git = lambda *a: subprocess.run(["git", "-C", top, *a], capture_output=True, text=True, check=True)
    git("init", "-q", "-b", branch)
    git("config", "user.email", "t@t")
    git("config", "user.name", "t")
    git("commit", "-q", "--allow-empty", "-m", "i")
    os.makedirs(os.path.join(top, ".loop", "tasks"))
    os.makedirs(os.path.join(top, "docs"))
    open(os.path.join(top, ".loop", "queue.md"), "w").write(queue)
    open(os.path.join(top, ".loop", "config.json"), "w").write(json.dumps(config or {}))
    open(os.path.join(top, "docs", "release-brief-1.1.0.md"), "w").write("brief\n")
    briefs and open(os.path.join(top, ".loop", "tasks", "t.md"), "w").write("# Task first\n\n- Release: v1.1.0\n- Goals: v110-a, v110-b, v110-dep\n- Priority: 1\n")
    os.makedirs(os.path.join(top, ".git", "loop"))
    open(os.path.join(top, ".git", "loop", "owner-words.tsv"), "w").write("o123\tthe owner's words\n")
    return top


def run(top, *argv, role=None):
    old = os.getcwd()
    os.chdir(top)
    out, err = io.StringIO(), io.StringIO()
    env = {"LOOP_ROLE": role} if role else {}
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), mock.patch.dict(os.environ, env):
            code = schedule.main(list(argv))
    finally:
        os.chdir(old)
    return code, out.getvalue(), err.getvalue()


def rows(out):
    return [line.split(". ", 1)[1] for line in out.splitlines() if line[:3].strip().rstrip(".").isdigit()]


def issues():
    return len(open(os.environ["FILER_LOG"]).read().split()) if os.path.exists(os.environ["FILER_LOG"]) else 0


add = ["workaround", "add", "k1", "--fix", "v110-fix", "--applies", "v110-dep", "--kind", "tool", "--feature", "TSK-1", "--found", "r1"]

# TSK-1.1 / 1.2 / 1.5: order, kinds, reasons, strings
top = repo()
code, out, err = run(top, "show")
r = rows(out)
check(code == 0 and r[0].startswith("v110-fix | fix | ahead of v110-a (blocks v110-dep)"), "a fix that blocks a queued task goal sorts ahead and names it: %s" % r[:1])
check(r[1] == "v110-a | task Task first | waits for: -" and r[4].startswith("v110-late | fix | after task goals"), "task goals come before a fix with no reason, the exact row grammar: %s" % r[1:])
check("release: 1.1.0 (source: brief)" in out, "the selected release is shown with its source")
top2 = repo(QUEUE.replace("v110-dep | release: v1.1.0 | depends-on: v110-fix", "v110-dep | release: v1.1.0"))
r = rows(run(top2, "show")[1])
check([x.split(" | ")[0] for x in r] == ["v110-a", "v110-dep", "v110-b", "v110-fix", "v110-late"] and r[3] == "v110-fix | fix | after task goals | waits for: -", "a fix with no reason stays behind the task goals (negative control)")
q = QUEUE.replace("v110-late | goal", "v110-late | first: safety: security | goal")
r = rows(run(repo(q), "show")[1])
check(r[0].startswith("v110-late | fix | ahead of v110-a (safety: security)"), "a first: safety: fix sorts first of all: %s" % r[0])
check(rows(run(repo(q.replace("security", "nonsense")), "show")[1])[4].startswith("v110-late | fix | after task goals"), "a safety class not on the list does not count (negative control)")
code, out, err = run(repo(QUEUE.replace("v110-late | goal", "v110-late | first: v110-gone: SECRETWHY | goal")), "show")
check("SECRETWHY" not in out + err and "not a queued task goal" in out, "a first: naming no queued task goal is ignored with a note, and the WHY text is printed nowhere")
r = rows(run(repo(config={"schedule_policy": "off"}), "show")[1])
check([x.split(" | ")[0] for x in r] == ["v110-fix", "v110-a", "v110-b", "v110-dep", "v110-late"] and all(" | fix" not in x and "task " not in x for x in r), "the policy off switch returns file order and no marks")
nb = repo(briefs=False)
check([x.split(" | ")[0] for x in rows(run(nb, "show")[1])] == ["v110-fix", "v110-a", "v110-b", "v110-dep", "v110-late"] and "task" not in run(nb, "show")[1], "no briefs: today's order, no marks")
want = [g["slug"] for g in map(graph.parse, QUEUE.splitlines()) if g]
check([g["slug"] for g in sl.load(nb)["goals"]] == want and all({k: v for k, v in g.items() if k in graph.parse(QUEUE.splitlines()[0])} == graph.parse(l) for g, l in zip(sl.load(nb)["goals"], QUEUE.splitlines())), "golden: the loader returns what graph.parse returns, line for line, with no brief")
bad = repo(QUEUE + "- slug: Bad Slug | goal: x | done: y\n- slug: v110-a | goal: dup | done: d\n")
check(len(sl.load(bad, True)["goals"]) == 5 and len(sl.load(bad, False)["goals"]) == 6, "golden: a bad slug is skipped, a duplicate is skipped only on the start path")
patch = repo(QUEUE)
open(os.path.join(patch, ".loop", "tasks", "p.md"), "w").write("# Patch\n\n- Release: v1.1.1\n- Goals: v110-late\n")
check(rows(run(patch, "show")[1])[4].startswith("v110-late | fix"), "a patch brief makes nothing a task goal")
dis = repo(QUEUE.replace("v110-a | release: v1.1.0", "v110-a | release: v1.2.0"))
check("release disagreement for v110-a" in run(dis, "show")[1] and rows(run(dis, "show")[1])[2].startswith("v110-b"), "a queue release that differs from its brief makes a fix and one note")
creation = repo(queue="")
made = subprocess.run([sys.executable, os.path.join(here, "..", "..", "skills", "workflow-delivery", "scripts", "goal.py"), "queue", "v110-new", "--goal", "g", "--done", "d", "--release", "v1.1.0"], cwd=creation, capture_output=True, text=True)
check("release: v1.1.0" in open(os.path.join(creation, ".loop", "queue.md")).read(), "goal.py queue --release writes the release key, no hand-written metadata" + (": " + made.stdout[-120:] + made.stderr[-200:] if made.returncode else ""))

# the owner line (TSK-1.5)
top = repo()
code, out, err = run(top, "order", "v110-late", "--by", "o999")
check(code == 2 and "SCHED-E08" in err and not os.path.exists(sl.paths(top)["order"]), "an unknown owner record refuses before anything is written")
code, out, err = run(top, "order", "v110-late", "v110-ghost", "--by", "o123")
check(code == 2 and "SCHED-E03" in err, "an unknown goal refuses and lists the queued ones")
code, out, err = run(top, "order", "v110-late", "--by", "o123")
r = rows(run(top, "show")[1])
check(code == 0 and r[0].startswith("v110-late | fix | ahead of v110-a (ordered by owner (o123))"), "the owner line puts a fix first and says so: %s" % r[0])
code, out, err = run(repo(q), "order", "v110-a", "--by", "o123")
shown = rows(run(repo(q), "show")[1])
topq = repo(q)
run(topq, "order", "v110-a", "--by", "o123")
check(rows(run(topq, "show")[1])[0].startswith("v110-late | fix | ahead of v110-a (safety"), "safety sorts above the owner order")
open(os.path.join(top, ".loop", "queue.md"), "w").write(QUEUE.replace("- slug: v110-late | goal: late | done: d\n", ""))
check("order: pruned v110-late" in run(top, "show")[1], "a merged or unknown slug is pruned on read with one line")

# unreadable input (I): loud, held, same exit code, recoverable; task 3 RED then GREEN
top = repo()
run(top, "order", "v110-late", "--by", "o123")
p = sl.paths(top)
open(p["order"], "w").write("{torn")
code, out, err = run(top, "show")
check(code == 3 and "SCHED-E12" in err and out.startswith("schedule incomplete: order (") and "last-good copy" in out, "a torn order file with a last-good copy: still exit 3 and a loud line, the copy is used")
check("last-good copy" in out and rows(out)[0].startswith("v110-late"), "a torn order file falls back to its last-good copy with a note")
os.unlink(p["good"])
code, out, err = run(top, "show")
check(code == 3 and out.startswith("schedule incomplete: order (") and "repair: schedule.py order --clear" in out and "SCHED-E12" in err, "no usable copy: one loud banner naming the state and the repair, SCHED-E12 on stderr, exit 3")
check("dispatch: conservative" in out and "dispatch: last-good" not in out, "with no usable copy the banner says dispatch is conservative, not last-good")
check(all("held: " in x for x in rows(out)) and not sl.eligible(sl.load(top)["goals"][0], sl.load(top))[0], "every start is held with the reason and eligible() says no")
with mock.patch.object(sl, "read_order", lambda p_: ("", [], "", None, None)):
    silent = run(top, "show")
red(silent[0] == 3 or "held: " in silent[1], "task 3 guard removed: the torn order file is read as nothing and the goals sit idle with no line")
code, out, err = run(top, "order", "--clear")
check(code == 0 and run(top, "show")[0] == 0 and "held: " not in run(top, "show")[1], "order --clear works on the torn file and the hold clears")
open(sl.paths(top)["workaround"], "w").write("{torn\n")
code, out, err = run(top, "show")
check(code == 3 and "SCHED-E11" in err and "schedule incomplete: workaround" in out, "a torn workaround record gives its banner, code and exit 3, and waives nothing")
os.unlink(sl.paths(top)["workaround"])
open(os.path.join(top, ".loop", "tasks", "bad.md"), "wb").write(b"\xff\xfe\x00 not utf8 \x80")
code, out, err = run(top, "show")
check(code == 3 and "SCHED-E10" in err, "an unreadable brief gives its banner, code and exit 3")

# the lock (I)
top = repo()
p = sl.paths(top)
os.makedirs(p["folder"], exist_ok=True)
open(p["lock"], "w").write(str(os.getpid()))
t0 = time.time()
with mock.patch.object(ss.Lock, "__init__", lambda self, paths, wait=0.3: setattr(self, "path", paths["lock"]) or setattr(self, "wait", wait)):
    code, out, err = run(top, "order", "v110-late", "--by", "o123")
check(code == 2 and "SCHED-E04" in err and not os.path.exists(p["order"]), "a held lock refuses after the bounded wait with no write")
os.utime(p["lock"], (time.time() - 120, time.time() - 120))
open(p["lock"], "w").write("999999")
os.utime(p["lock"], (time.time() - 120, time.time() - 120))
code, out, err = run(top, "order", "v110-late", "--by", "o123")
check(code == 0 and "stale schedule lock" in err, "a lock over a minute old whose owner is gone is broken with a note")

# TSK-1.3 and tasks 2, 4: workaround record, preview, name scan
top = repo()
code, out, err = run(top, *add, "wait for the fix to merge")
check(code == 0 and "PREVIEW" in out and issues() == 0 and not os.path.exists(sl.paths(top)["workaround"]), "task 4: without --live nothing is filed and nothing is recorded")
real = ss.file_issue
with mock.patch.object(ss, "file_issue", lambda root, rec, live: real(root, rec, True)):
    run(repo(), *add, "words")
red(issues() == 0, "task 4 guard removed: the preview guard ignored, a run without --live files a real issue (the stub saw it)")
os.unlink(os.environ["FILER_LOG"])
code, out, err = run(top, *add, "wait for the fix to merge", "--live")
check(code == 0 and issues() == 1 and "issue #7" in out, "with --live exactly one issue is filed and the record is done")
code, out, err = run(top, *add, "again", "--live")
check(code == 2 and "SCHED-E09" in err and issues() == 1, "a second add of the same key refuses and files nothing")
r = rows(run(top, "show")[1])
check(all("workaround" not in x for x in r) and r[0].startswith("v110-fix"), "a recorded but unused workaround waives nothing")
code, out, err = run(top, "workaround", "use", "k1", "--goal", "v110-dep")
r = rows(run(top, "show")[1])
check(code == 0 and "wait for the fix to merge" in out and r[0].startswith("v110-a") and any("workaround k1 (fix v110-fix pending)" in x for x in r), "an activated workaround frees the task goal and shows its mark: %s" % [x[:60] for x in r[:3]])
check(sl.load(top)["goals"][[g["slug"] for g in sl.load(top)["goals"]].index("v110-dep")]["depends"] == [], "the wait on the fix is waived for that goal only")
code, out, err = run(top, "workaround", "use", "k1", "--goal", "v110-b")
check(code == 2 and "SCHED-E03" in err, "use for a goal the record does not list is refused")
run(top, "workaround", "fail", "k1", "--goal", "v110-dep", "--reason", "x")
check(not sl.load(top)["waived"] and issues() == 1, "fail restores the wait for that goal")
run(top, "workaround", "use", "k1", "--goal", "v110-dep")
run(top, "workaround", "close", "k1", "--reason", "done")
check(not sl.load(top)["waived"], "close retires the record: it waives nothing")
dep = repo()
run(dep, *add[:2], "k2", *add[3:7], "--kind", "dependency", *add[9:], "w", "--live")
run(dep, "workaround", "use", "k2", "--goal", "v110-dep")
check(not sl.load(dep)["waived"], "a dependency record is never waived")
n0 = issues()
code, out, err = run(repo(), *add, "see plantedname for details", "--live")
check(code == 2 and "SCHED-E06" in err and "plantedname" not in err + out and issues() == n0, "task 2: words with a private name are refused for the issue path, the name is never echoed, nothing is filed")
with mock.patch.object(ss, "outside", lambda root, *t: None):
    code, out, err = run(repo(), *add, "see plantedname for details", "--live")
red(issues() == n0, "task 2 guard removed (issue path): the planted name is filed")
t3 = repo()
run(t3, *add, "see plantedname", "--live") if False else None
code, out, err = run(t3, *add, "fine words", "--live")
open(os.path.join(tmp, "names"), "a").write("fine words\n")
code, out, err = run(t3, "workaround", "use", "k1", "--goal", "v110-dep")
check(code == 2 and "fine words" not in out + err and not sl.load(t3)["waived"], "task 2: stored words that now hit the name scan are not shown and no activation is written")
open(os.path.join(tmp, "names"), "w").write("plantedname\n")
with mock.patch.object(ss, "outside", lambda root, *t: None):
    code, out, err = run(t3, "workaround", "use", "k1", "--goal", "v110-dep")
red("fine words" not in out, "task 2 guard removed (stderr/session path): the words are printed unscanned")
code, out, err = run(repo(), *add, "token ghp_abcdefghijklmnopqrstuvwx1234", "--live")
check(code == 2 and "SCHED-E05" in err and "ghp_" not in out + err, "a secret-shaped value is refused by class and never echoed")

# tasks 1 and 5: GRD-4, worker role
top = repo(branch="loop/v110-dep")
run(top, *add, "w", "--live")
for verb, argv in (("workaround add", add[:2] + ["k9"] + add[3:] + ["w"]), ("workaround use", ["workaround", "use", "k1", "--goal", "v110-dep"]), ("order", ["order", "v110-late", "--by", "o123"])):
    code, out, err = run(top, *argv, role="worker")
    check(code == 2 and "SCHED-E01" in err, "task 1: a worker is refused `%s`" % verb)
    with mock.patch.object(ss, "guard_worker", lambda *a: None):
        code2, out2, err2 = run(top, *argv, role="worker")
    red(code2 == 2 and "SCHED-E01" in err2, "task 1 guard removed: a worker runs `%s`" % verb)
for verb in ("fail", "close"):
    mine = ["workaround", verb, "k1"] + (["--goal", "v110-dep"] if verb == "fail" else []) + ["--reason", "r"]
    code, out, err = run(top, *mine, role="worker")
    check(code == 0, "task 5: a worker may `%s` a record of its own goal" % verb)
other = repo(branch="loop/v110-other")
run(other, *add, "w", "--live")
for verb in ("fail", "close"):
    argv = ["workaround", verb, "k1"] + (["--goal", "v110-dep"] if verb == "fail" else []) + ["--reason", "r"]
    code, out, err = run(other, *argv, role="worker")
    check(code == 2 and "SCHED-E02" in err, "task 5: a worker cannot `%s` another goal's record" % verb)
    with mock.patch.object(ss, "own_goal", lambda: "v110-dep"):
        check(run(other, *argv, role="worker")[0] == 0, "task 5 negative control: the same call succeeds only for the record's own goal")
    with mock.patch.object(ss, "guard_worker", lambda *a: None):
        red(run(other, *argv, role="worker")[0] == 2, "task 5 guard removed: a worker changes another goal's record with `%s`" % verb)

# the four consumers print the same strings (TSK-1.5)
import board_status as bs  # noqa: E402
top = repo()
run(top, "order", "v110-late", "--by", "o123")
cells = [g["cell"] for g in bs.queued(top, [])]
check(all(c == " | ".join(["v110-late"] + sl.load(top)["goals"][0]["marks"]) or c.startswith("v110-") for c in cells) and cells[0].startswith("v110-late | fix | ahead of v110-a (ordered by owner (o123))"), "the board status items carry the loader's exact cell")
import board_lines  # noqa: E402
view = board_lines.queue_view([dict(g, mark="queued", cell=g["cell"], depends=g["depends"]) for g in bs.queued(top, [])], None)
view = [x for x in view if x.startswith("  1.")]
check(view[0].startswith("  1. v110-late | fix | ahead of v110-a (ordered by owner (o123)) | waits for:"), "the queue view prints the same row: %s" % view[0][:70])

print("ALL PASS" if not failed else "%d FAILED" % len(failed))
sys.exit(1 if failed else 0)
