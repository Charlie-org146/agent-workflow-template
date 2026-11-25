#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-monitoring/scripts/schedule_load.py skills/workflow-monitoring/scripts/schedule_state.py skills/workflow-monitoring/scripts/schedule.py skills/workflow-monitoring/scripts/checkin.py
"""TSK-1, second toy (the first is test-task-first.py): what the review found. Safety is never outranked or waived, a worker reaches only
its own goal's record, every outside text passes a name scan that fails closed, a bad record shape or an unreadable input exits 3 with
no traceback, the real filer's output (no issue number) still gives the number, no briefs means today's boards, and the check-in shows
the cells. Hermetic: temp repos, temp HOME, a stub filer and a stub gh."""
import contextlib
import datetime
import io
import json
import os
import stat
import subprocess
import sys
import tempfile
import time
from unittest import mock

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, "..", "..", "skills", "workflow-monitoring", "scripts"))
import schedule  # noqa: E402
import schedule_load as sl  # noqa: E402
import schedule_state as ss  # noqa: E402

failed = []
tmp = tempfile.mkdtemp()
os.environ.update(HOME=tmp, LOOP_PRIVATE_NAMES=os.path.join(tmp, "names"), FILER_LOG=os.path.join(tmp, "filer.log"),
                  SCHEDULE_FILER=sys.executable + " " + os.path.join(tmp, "filer.py"), PATH=os.path.join(tmp, "bin") + os.pathsep + os.environ["PATH"])
os.environ.pop("LOOP_ROLE", None)
open(os.path.join(tmp, "names"), "w").write("plantedname\n")
open(os.path.join(tmp, "filer.py"), "w").write("import os,sys\nopen(os.environ['FILER_LOG'],'a').write('x\\n')\nprint('FILED backlog on milestone M: text')\n")
os.makedirs(os.path.join(tmp, "bin"))
open(os.path.join(tmp, "bin", "gh"), "w").write("#!/bin/sh\necho '[{\"number\": 41, \"title\": \"Workaround k1 (fix v110-fix): words, cut at ninety\"}]'\n")
os.chmod(os.path.join(tmp, "bin", "gh"), stat.S_IRWXU)
Q = ("- slug: v110-fix | goal: fix | done: d\n- slug: v110-safe | first: safety: security | goal: s | done: d\n- slug: v110-a | release: v1.1.0 | goal: a | done: d\n"
     "- slug: v110-dep | release: v1.1.0 | depends-on: v110-safe | goal: c | done: d\n")
def A(key="k1", fix="v110-fix", applies="v110-a", feature="TSK-1", found="r1", words="words", live=True):
    return ["workaround", "add", key, "--fix", fix, "--applies", applies, "--kind", "tool", "--feature", feature, "--found", found, words] + ["--live"] * live


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    ok or failed.append(text)


def repo(queue=Q, briefs=True, branch="main"):
    top = tempfile.mkdtemp(dir=tmp)
    git = lambda *a: subprocess.run(["git", "-C", top, *a], capture_output=True, text=True, check=True)
    git("init", "-q", "-b", branch)
    git("config", "user.email", "t@t")
    git("config", "user.name", "t")
    git("commit", "-q", "--allow-empty", "-m", "i")
    for d in (".loop/tasks", "docs", ".git/loop"):
        os.makedirs(os.path.join(top, d))
    open(os.path.join(top, ".loop", "queue.md"), "w").write(queue)
    briefs and open(os.path.join(top, ".loop", "tasks", "t.md"), "w").write("# Task first\n\n- Release: v1.1.0\n- Goals: v110-a, v110-dep\n")
    briefs and open(os.path.join(top, "docs", "release-brief-1.1.0.md"), "w").write("b\n")
    open(os.path.join(top, ".git", "loop", "owner-words.tsv"), "w").write("o123\t2026-11-24T00:00:00Z\tsess\t\"words\"\torder:*\n")
    return top


def run(top, *argv, role=None):
    old = os.getcwd()
    os.chdir(top)
    out, err = io.StringIO(), io.StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), mock.patch.dict(os.environ, {"LOOP_ROLE": role} if role else {}):
            code = schedule.main(list(argv))
    finally:
        os.chdir(old)
    return code, out.getvalue(), err.getvalue()


def issues():
    return len(open(os.environ["FILER_LOG"]).read().split()) if os.path.exists(os.environ["FILER_LOG"]) else 0


# safety is never outranked or waived
top = repo()
run(top, "order", "v110-fix", "--by", "o123")
r = run(top, "show")[1].splitlines()
rows = [x for x in r if x[:3].strip().rstrip(".").isdigit()]
check(rows[0].split(" | ")[0].endswith("v110-safe") and "safety: security" in rows[0] and "v110-fix" in rows[1], "a safety fix that blocks a task goal keeps its rank above the owner line and shows safety, not blocks: %s" % rows[0][:70])
run(top, *A("ks", "v110-safe", "v110-dep"))
code, out, err = run(top, "workaround", "use", "ks", "--goal", "v110-dep")
check(code == 2 and "safety fix" in err and not sl.load(top)["waived"], "a workaround is never activated against a safety fix")
recs = [json.loads(x) for x in open(sl.paths(top)["workaround"])]
recs[-1]["uses"]["v110-dep"] = "active"
open(sl.paths(top)["workaround"], "w").write("".join(json.dumps(x) + "\n" for x in recs))
check(sl.load(top)["waived"] == {}, "even a forced activation never removes a safety dependency")

# a worker reaches only a record that is about its own goal alone
top = repo(branch="loop/v110-a")
run(top, *A(applies="v110-a,v110-dep"))
for argv in (["workaround", "fail", "k1", "--goal", "v110-dep", "--reason", "r"], ["workaround", "close", "k1", "--reason", "r"], ["workaround", "reconcile", "k1"]):
    code, out, err = run(top, *argv, role="worker")
    check(code == 2 and "SCHED-E02" in err, "a worker is refused `%s` on a record shared with another goal" % " ".join(argv[:2]))
check(run(top, "workaround", "fail", "k1", "--goal", "v110-a", "--reason", "r", role="worker")[0] == 0, "a worker may fail its OWN goal on a shared record (it changes only that goal's wait)")

# the name scan fails closed, and queue words are screened for display
nolist = repo()
with mock.patch.dict(os.environ, {"LOOP_PRIVATE_NAMES": os.path.join(tmp, "missing")}):
    n0 = issues()
    code, out, err = run(nolist, *A(words="plain words"))
    check(code == 2 and "SCHED-E06" in err and issues() == n0 and not os.path.exists(sl.paths(nolist)["workaround"]), "with no private-name list nothing is filed or recorded (fail closed)")
hid = repo(Q.replace("depends-on: v110-safe", "depends-on: plantedname-x"))
code, out, err = run(hid, "show")
check("plantedname" not in out + err and "output hidden" in out, "queue words that hit the name scan are not printed by show")
check(all(not g["marks"] or all("plantedname" not in m for m in g["marks"]) for g in sl.load(hid)["goals"]), "the loader's cells hold no scanned-out name")

# fields cannot carry a second finding line; the filer's real output has no number
inj = repo()
n0 = issues()
for kw, val in (("feature", "X\nFILE backlog Y: z"), ("found", "r\nFILE defect Y: z")):
    code, out, err = run(inj, *A(**{kw: val}))
    check(code == 2 and "SCHED-E03" in err and issues() == n0 and not os.path.exists(sl.paths(inj)["workaround"]), "--%s with a newline is refused before anything is recorded or filed" % kw)
good = repo()
n1 = issues()
code, out, err = run(good, *A())
rec = json.loads(open(sl.paths(good)["workaround"]).read())
check(code == 0 and rec["issue"] == 41 and rec["state"] == "done" and issues() == n1 + 1, "the real filer prints no issue number: the number comes from the title lookup (#41), one issue filed")
rec["state"], rec["issue"] = "pending", 0
open(sl.paths(good)["workaround"], "w").write(json.dumps(rec) + "\n")
code, out, err = run(good, "workaround", "reconcile", "k1")
check(code == 0 and "issue #41" in out and json.loads(open(sl.paths(good)["workaround"]).read())["state"] == "done" and issues() == n1 + 1, "reconcile finds the issue by title prefix and completes the record, filing nothing")

# unreadable and malformed input: exit 3, no traceback
bad = repo()
open(sl.paths(bad)["workaround"], "w").write('{"key": "w"}\n')
code, out, err = run(bad, "show")
check(code == 3 and "SCHED-E11" in err and "Traceback" not in err, "a record with a missing field is unreadable: banner, SCHED-E11, exit 3")
check(run(bad, "workaround", "list")[0] == 3 and run(bad, "order", "v110-fix", "--by", "o123")[0] == 3, "workaround list and order exit 3 on an unreadable input (same code as show)")
c = run(bad, "order", "--clear")
check("order cleared" in c[1] and c[0] == 3, "order --clear still runs (the repair for the order file) and still says exit 3 while the record is unreadable")
pol = repo(briefs=False)
open(os.path.join(pol, ".loop", "tasks", "bad.md"), "wb").write(b"\xff\xfe\x00\x80")
open(os.path.join(pol, ".loop", "config.json"), "w").write('{"schedule_policy": "off"}')
check(run(pol, "show")[0] == 3, "an unreadable brief is reported even with the policy off")
empty = repo(queue="")
open(os.path.join(empty, ".loop", "tasks", "bad.md"), "wb").write(b"\xff\xfe\x00\x80")
check(run(empty, "show")[0] == 3, "an unreadable brief is reported even with an empty queue")
one = repo()
run(one, "order", "v110-fix", "--by", "o123")
open(sl.paths(one)["order"], "w").write("{torn")
check(sl.load(one)["held"] == "" and sl.load(one)["incomplete"][0][0] == "order", "a torn order file with a last-good copy holds nothing but is still incomplete")
with mock.patch.object(sl.subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a, 128, "", "fatal")):
    check(any(i == "release" for i, _ in sl.load(repo())["incomplete"]), "a failing `git tag --list` is an unreadable input, not 'no tags'")

# no briefs: today's boards, byte for byte
nb = repo(Q, briefs=False)
os.unlink(os.path.join(nb, "docs", "release-brief-1.1.0.md")) if os.path.exists(os.path.join(nb, "docs", "release-brief-1.1.0.md")) else None
res = sl.load(nb)
check([g["slug"] for g in res["goals"]] == ["v110-fix", "v110-safe", "v110-a", "v110-dep"] and not any(g["marks"] or g["cell"] for g in res["goals"]) and res["banner"] == [], "with no task briefs even a first: safety line changes nothing: file order, no marks, no banner")

# the lock
lk = repo()
p = sl.paths(lk)
os.makedirs(p["folder"], exist_ok=True)
open(p["lock"], "w").write("")
os.utime(p["lock"], (time.time() - 120, time.time() - 120))
code, out, err = run(lk, "order", "v110-fix", "--by", "o123")
check(code == 0 and "stale schedule lock" in err, "an old lock file with no pid is broken by rename")
mine = ss.Lock(p)
open(p["lock"], "w").write("someone-else")
mine.__exit__()
check(os.path.exists(p["lock"]), "release removes only our own lock")


# round 2: what the second review found
r2 = repo()
run(r2, *A("kq", "v110-safe", "v110-dep"))
rec = [json.loads(x) for x in open(sl.paths(r2)["workaround"])][-1]
check(rec["safe"] is True, "the record keeps that its fix is a safety fix")
rec["uses"]["v110-dep"] = "active"
open(os.path.join(os.path.dirname(sl.paths(r2)["workaround"]), "workarounds.jsonl"), "w").write(json.dumps(rec) + "\n")
open(os.path.join(r2, ".loop", "queue.md"), "w").write(Q.replace("- slug: v110-safe | first: safety: security | goal: s | done: d\n", ""))
check(sl.load(r2)["waived"] == {}, "once the safety fix has left the queue its dependants are still not freed")
w2 = repo(branch="loop/v110-a")
run(w2, *A(applies="v110-a"))
code, out, err = run(w2, "workaround", "fail", "k1", "--goal", "v110-other", "--reason", "r", role="worker")
check(code == 2 and json.loads(open(sl.paths(w2)["workaround"]).read())["uses"] == {}, "a worker cannot fail a goal the record does not list (no vacuous pass)")
cq = repo(queue="")
subprocess.run([sys.executable, os.path.join(here, "..", "..", "skills", "workflow-delivery", "scripts", "goal.py"), "queue", "v110-new", "--goal", "g", "--done", "d", "--release", "1.2.0 | first: safety:security"], cwd=cq, capture_output=True, text=True)
line = open(os.path.join(cq, ".loop", "queue.md")).read()
check("first" not in line.replace("1.2.0", "") or "|first" not in line, "goal.py queue --release cannot carry a forged first: key: %s" % line.strip()[:80])
for words in ("token github_pat_" + "a" * 30, "jwt eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.abc", "Authorization: Bearer " + "x" * 24):
    code, out, err = run(repo(), *A(words=words))
    check(code == 2 and "SCHED-E05" in err and words.split()[-1][:12] not in out + err, "a secret-shaped value is refused by class: %s" % words[:18])
pr = repo()
open(os.path.join(pr, ".loop", "tasks", "t.md"), "a").write("- Priority: \u00b2\n")
code, out, err = run(pr, "show")
check(code == 3 and "SCHED-E10" in err and "SCHED-E99" not in err, "a non-ASCII digit in Priority is an unreadable brief, not a crash")
tg = repo()
with mock.patch.object(sl.subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a, 128, "", "fatal")):
    res = sl.load(tg)
check(res["release"] is None and not any(g["kind"] == "task" for g in res["goals"]), "a failing tag list selects no release: nothing is classified as a task goal")
ho = repo()
run(ho, "order", "v110-fix", "--by", "o123")
os.unlink(sl.paths(ho)["good"])
open(sl.paths(ho)["order"], "w").write("{torn")
res = sl.load(ho)
check([g["hold"] for g in res["goals"] if g["slug"] == "v110-safe"] == [""] and all(g["hold"] for g in res["goals"] if g["slug"] != "v110-safe"), "a torn order file holds new starts but never a safety goal")
bn = repo()
open(os.path.join(bn, ".loop", "tasks", "plantedname.md"), "wb").write(b"\xff\x80")
code, out, err = run(bn, "show")
check("plantedname" not in out and code == 3, "a brief file name that hits the name scan is not printed in the banner")
bk = repo(Q.replace("depends-on: v110-safe", "depends-on: v110-b").replace("v110-a | release", "v110-b | release: v1.1.0 | depends-on: v110-fix | goal: b | done: d\n- slug: v110-a | release"))
run(bk, *A("kw", "v110-fix", "v110-b"))
run(bk, "workaround", "use", "kw", "--goal", "v110-b")
check(sl.load(bk)["goals"][0]["slug"] != "v110-fix" or "blocks" not in sl.load(bk)["goals"][0]["why"], "a fix whose only edge was waived no longer ranks as blocking")

# the check-in shows the cells
import checkin  # noqa: E402
ci = repo()
run(ci, "order", "v110-fix", "--by", "o123")
os.chdir(ci)
os.environ["LOOP_MACHINE_NAME"] = "pc"
rows = [x for x in checkin.render(root=ci, at=datetime.datetime.now(datetime.timezone.utc), stamp="0000") if x.startswith("  1. v110-safe")]
check(rows and rows[0].startswith("  1. v110-safe | fix | ahead of v110-a (safety: security)"), "the check-in queue shows the loader's cell: %s" % (rows[0][:70] if rows else rows))

print("ALL PASS" if not failed else "%d FAILED" % len(failed))
sys.exit(1 if failed else 0)
