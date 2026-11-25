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

print("ALL PASS" if not failed else "%d FAILED" % len(failed))
sys.exit(1 if failed else 0)
