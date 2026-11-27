#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-delivery/scripts/start_review.py skills/workflow-delivery/scripts/goal.py skills/workflow-monitoring/scripts/batch.py skills/workflow-release/scripts/merge.py
"""One review (DLF-1.3), a goal's start: adopt marks no goal and refuses one with any sign of a mark or with history it
can't read; a goal first committed where the setting is on needs a start review, and merge refuses until it is answered.
Throwaway repos with a bare origin, their own home and a stand-in gh; no network."""
import json
import os
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
delivery = os.path.join(root, "skills", "workflow-delivery", "scripts")
sys.path.insert(0, delivery)
home = tempfile.mkdtemp()
fake = os.path.join(home, "py")
os.makedirs(fake)
open(os.path.join(fake, "sitecustomize.py"), "w").write('''import os
import subprocess
_run = subprocess.run
def run(args, *a, **k):
    if args and args[0] == "gh":
        out = os.environ.get("TOY_PRS", "[]") if "list" in args else '{"url": "https://github.com/o/r/pull/7", "state": "OPEN"}'
        return subprocess.CompletedProcess(args, 0, out, "")
    return _run(args, *a, **k)
subprocess.run = run
''')
open(os.path.join(home, "names"), "w").write("zz-dummy-private-name\n")
env = dict(os.environ, HOME=home, USERPROFILE=home, GIT_CONFIG_NOSYSTEM="1", PYTHONPATH=fake, LOOP_ROLE="worker",
           LOOP_PRIVATE_NAMES=os.path.join(home, "names"), LOOP_FLOW=os.path.join(home, "flow.json"),
           GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.invalid")
env.pop("CLAUDE_CODE_HOST_SESSION_ID", None)
os.environ.update(env)

failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def sh(cwd, *args):
    return subprocess.run(["git", "-C", cwd] + list(args), capture_output=True, text=True, check=True).stdout.strip()


def put(cwd, rel, text):
    os.makedirs(os.path.dirname(os.path.join(cwd, rel)), exist_ok=True)
    open(os.path.join(cwd, rel), "w").write(text)


def commit(cwd, rel, text, message):
    put(cwd, rel, text)
    sh(cwd, "add", rel)
    sh(cwd, "commit", "-qm", message)


def goal_text(slug, mark=False):
    return "# %s\n\n- Slug: %s\n%s- Touches: a.py\n\n## Done lines\n\n1. %s works\n" % (slug, slug, "- Review: one\n" if mark else "", slug)


origin = os.path.join(home, "origin.git")
tmp = os.path.join(home, "repo")
subprocess.run(["git", "init", "-q", "--bare", "-b", "main", origin], check=True)
subprocess.run(["git", "clone", "-q", origin, tmp], check=True, capture_output=True)
CONFIG = {"base": "main", "auto_merge": True}
commit(tmp, ".loop/config.json", json.dumps(CONFIG), "setting off")
sh(tmp, "push", "-q", "origin", "HEAD:main")
OFF = sh(tmp, "rev-parse", "HEAD")
commit(tmp, ".loop/config.json", json.dumps(dict(CONFIG, one_review=True)), "setting on")
sh(tmp, "push", "-q", "origin", "HEAD:main")
runs = os.path.join(tmp, ".git", "loop", "runs")
os.makedirs(runs)
goal_py = os.path.join(delivery, "goal.py")


def branch(slug, base="origin/main", mark=False, push=True):
    sh(tmp, "switch", "-q", "-c", "loop/" + slug, base)
    commit(tmp, ".loop/goals/%s.md" % slug, goal_text(slug, mark), "Goal: " + slug)
    push and sh(tmp, "push", "-q", "origin", "loop/" + slug)


def adopt(slug, cwd=tmp):
    got = subprocess.run([sys.executable, goal_py, "adopt", slug], capture_output=True, text=True, cwd=cwd, env=env)
    return got.stdout + got.stderr


def record(slug):
    try:
        return json.load(open(os.path.join(runs, slug + ".json")))
    except OSError:
        return {}


def refused_unrecorded(slug, said, why):
    check("ONE_REVIEW_ADOPT" in said and not record(slug), "adopt refuses %s: %s" % (why, said.strip()[:100]))


branch("now", mark=True)
refused_unrecorded("now", adopt("now"), "a goal file that carries the mark")

branch("later", mark=True)
commit(tmp, ".loop/goals/later.md", goal_text("later"), "drop the line")
sh(tmp, "push", "-q", "origin", "loop/later")
refused_unrecorded("later", adopt("later"), "a mark removed by a later commit")

branch("side", push=False)
sh(tmp, "switch", "-q", "-c", "other")
commit(tmp, ".loop/goals/side.md", goal_text("side", True), "marked on a side branch")
sh(tmp, "switch", "-q", "loop/side")
commit(tmp, "a.py", "x = 1\n", "work")
sh(tmp, "merge", "-q", "--no-ff", "-X", "ours", "-m", "merge side", "other")
commit(tmp, ".loop/goals/side.md", goal_text("side"), "no mark now") if "Review: one" in open(os.path.join(tmp, ".loop/goals/side.md")).read() else None
sh(tmp, "push", "-q", "origin", "loop/side")
refused_unrecorded("side", adopt("side"), "a mark only on a merged side branch")

branch("ledger")
open(os.path.join(runs, "ledger.decisions.jsonl"), "w").write('{"n": 1, "kind": "mark"}\n')
refused_unrecorded("ledger", adopt("ledger"), "a decisions file left here without a run record")

branch("stale")
json.dump({"slug": "stale", "status": "running", "flow": {}, "pid": None, "start_answer": {"record": "o1"}}, open(os.path.join(runs, "stale.json"), "w"))
said = adopt("stale")
check("ONE_REVIEW_ADOPT" in said and record("stale").get("start_answer") == {"record": "o1"}, "a stale record with a sign is not replaced: " + said.strip()[:90])
branch("sidecar")
open(os.path.join(runs, "sidecar.extra.json"), "w").write("{}")
refused_unrecorded("sidecar", adopt("sidecar"), "a side file left here without a run record")
branch("again", base=OFF)
json.dump({"slug": "again", "status": "running", "flow": {}, "pid": None, "start_required": {"why": "kept"}}, open(os.path.join(runs, "again.json"), "w"))
said = adopt("again")
check("ADOPTED again" in said and record("again").get("start_required") == {"why": "kept"}, "adopting again keeps the need for a start review: " + said.strip()[:90])


def handover(slug, rec):
    got = subprocess.run(["git", "-C", tmp, "hash-object", "-w", "--stdin"], input=json.dumps(rec), capture_output=True, text=True, check=True)
    sh(tmp, "push", "-q", "-f", "origin", got.stdout.strip() + ":refs/loop/handover/" + slug)


branch("handed")
handover("handed", {"to": "elsewhere", "at": 1, "state": {"slug": "handed", "one_review": {"at": "t"}}})
refused_unrecorded("handed", adopt("handed"), "a mark in an old handover only")
branch("carried", base=OFF)
handover("carried", {"to": "elsewhere", "at": 1, "state": {"slug": "carried", "start_required": {"why": "carried"}}})
said = adopt("carried")
check("ADOPTED carried" in said and record("carried").get("start_required") == {"why": "carried"}, "a handover record's need for a start review is kept: " + said.strip()[:90])
branch("broken")
got = subprocess.run(["git", "-C", tmp, "hash-object", "-w", "--stdin"], input="not json", capture_output=True, text=True, check=True)
sh(tmp, "push", "-q", "origin", got.stdout.strip() + ":refs/loop/handover/broken")
refused_unrecorded("broken", adopt("broken"), "a handover it can't read")

branch("shallow")
thin = os.path.join(home, "thin")
subprocess.run(["git", "clone", "-q", "--depth", "1", "--branch", "loop/shallow", "file://" + origin, thin], check=True, capture_output=True)
said = adopt("shallow", thin)
check("ONE_REVIEW_ADOPT" in said and "shallow" in said, "adopt refuses a shallow copy: " + said.strip()[:100])

branch("new-era")
said = adopt("new-era")
got = record("new-era")
check("ADOPTED new-era" in said and got.get("start_required") and not got.get("one_review")
      and not os.path.exists(os.path.join(runs, "new-era.decisions.jsonl")),
      "a goal first committed with the setting on is adopted unmarked, with a start review required: %s" % said.strip()[:120])
check("start review" in said, "adopt says a start review is required")
branch("old-era", base=OFF)
said = adopt("old-era")
check("ADOPTED old-era" in said and "start_required" not in record("old-era"), "an older goal is adopted as today: " + said.strip()[:80])

# a freeze marks the goal where the setting is on, in the committed goal file, the record and a new ledger
open(os.path.join(home, "flow.json"), "w").write(json.dumps({"steps": {s: "x" for s in ("idea", "plan", "review", "qa", "ship")}}))


def tool(*args, role="worker", **more):
    got = subprocess.run([sys.executable, goal_py] + list(args), capture_output=True, text=True, cwd=tmp,
                         env=dict(env, LOOP_ROLE=role, **more))
    open(os.path.join(home, "last.txt"), "a").write(got.stderr)
    return got.stdout + got.stderr


def ledger(slug):
    try:
        return [json.loads(line)["kind"] for line in open(os.path.join(runs, slug + ".decisions.jsonl"))]
    except OSError:
        return None


def goal_in_head(slug):
    return sh(tmp, "show", "HEAD:.loop/goals/%s.md" % slug)


def fresh(slug, base="origin/main"):
    sh(tmp, "reset", "-q", "--hard")
    sh(tmp, "switch", "-q", "-c", "loop/" + slug, base)
    return tool("new", slug, "--here", "--goal", "Do " + slug, "--done", slug + " works", "--touches", "a.py")


said = fresh("frz")
check("FROZEN frz" in said and "\n- Review: one\n" in goal_in_head("frz") and record("frz").get("one_review")
      and ledger("frz") == ["mark"], "a freeze with the setting on marks the goal: " + said.strip()[:150])
said = tool("step", "frz", "build")
check("ONE_REVIEW_UNANSWERED" in said and record("frz").get("step") == "idea", "build waits for the start review: " + said.strip()[:110])
lost = {k: v for k, v in record("frz").items() if k != "one_review"}
json.dump(lost, open(os.path.join(runs, "frz.json"), "w"))
check("ONE_REVIEW_UNANSWERED" in tool("step", "frz", "build"), "the committed mark holds a record that lost it")
said = fresh("plain", OFF)
check("FROZEN plain" in said and "Review: one" not in goal_in_head("plain") and "one_review" not in record("plain")
      and ledger("plain") is None, "a freeze with the setting off is as today: " + said.strip()[:120])
os.remove(os.path.join(runs, "plain.json"))
head = sh(tmp, "rev-parse", "HEAD")
said = tool("new", "plain", "--here", "--goal", "again", "--done", "other")
check("goal.py recover plain" in said and sh(tmp, "rev-parse", "HEAD") == head, "new never freezes a committed goal file twice: " + said.strip()[:110])


def lose(slug, keep_ledger=False):
    os.remove(os.path.join(runs, slug + ".json"))
    keep_ledger or (os.path.exists(os.path.join(runs, slug + ".decisions.jsonl")) and os.remove(os.path.join(runs, slug + ".decisions.jsonl")))


def recover(slug, role="operation", **more):
    return tool("recover", slug, role=role, **more)


for slug, keep in (("rec-none", False), ("rec-ledger", True)):
    fresh(slug)
    lose(slug, keep)
    said = recover(slug)
    got = record(slug)
    check("RECOVERED " + slug in said and got.get("one_review") and not got.get("start_answer") and got.get("release") == "ask"
          and got.get("step") == "idea" and got.get("done_sha") and got.get("eta") is not None and ledger(slug) == ["mark"],
          "recovery %s gives a marked, unanswered record that asks about release: %s" % (slug, said.strip()[:140]))
    check("ONE_REVIEW_UNANSWERED" in tool("step", slug, "build"), "build still waits after recovery of " + slug)

fresh("rec-queued")
queued = dict(record("rec-queued"), status="queued", step="", release="", waits_on=["frz"], batch=True)
queued.pop("one_review", None)
json.dump(queued, open(os.path.join(runs, "rec-queued.json"), "w"))
os.path.exists(os.path.join(runs, "rec-queued.decisions.jsonl")) and os.remove(os.path.join(runs, "rec-queued.decisions.jsonl"))
said = tool("step", "rec-queued", "plan")
check("goal.py recover rec-queued" in said, "a half-frozen goal takes no step until it is recovered: " + said.strip()[:110])
before = record("rec-queued")
for script, args in (("sessions.py", ["assign", "rec-queued", "--text", "text"]), ("sessions.py", ["bind", "rec-queued", "local_x"]),
                     ("machines.py", ["handover", "rec-queued", "--to", "elsewhere"])):
    ran = subprocess.run([sys.executable, os.path.join(root, "skills", "workflow-monitoring", "scripts", script)] + args,
                         capture_output=True, text=True, cwd=tmp, env=dict(env, LOOP_ROLE="operation"))
    check("goal.py recover rec-queued" in ran.stdout + ran.stderr and record("rec-queued") == before,
          "%s %s refuses a half-frozen goal: %s" % (script, args[0], (ran.stdout + ran.stderr).strip()[:110]))
said = recover("rec-queued")
got = record("rec-queued")
check("RECOVERED" in said and got.get("waits_on") == ["frz"] and got.get("release") == "" and got.get("batch") is True
      and got.get("status") == "queued" and got.get("step") == "idea" and got.get("one_review"),
      "recovery keeps every field of a queued record: " + said.strip()[:140])


def no_recovery(slug, why, prepare, role="operation", **more):
    fresh(slug)
    lose(slug)
    prepare(slug)
    said = recover(slug, role, **more)
    check("REFUSED" in said and "RECOVERED" not in said and "invalid choice" not in said and record(slug).get("step") != "idea",
          "recovery refuses %s: %s" % (why, said.strip()[:120]))


def side(name, text="{}"):
    return lambda slug: open(os.path.join(runs, name % slug), "w").write(text)


def queued_with(**more):
    return lambda slug: json.dump(dict({"slug": slug, "status": "queued", "step": "", "flow": {}, "pid": None}, **more),
                                  open(os.path.join(runs, slug + ".json"), "w"))


no_recovery("no-worker", "a worker", lambda slug: None, role="worker")
no_recovery("no-later", "a later commit", lambda slug: commit(tmp, "a.py", "y = 2\n", "later work"))
no_recovery("no-dirty", "a changed working copy", lambda slug: open(os.path.join(tmp, ".loop/goals/%s.md" % slug), "a").write("2. more\n"))
no_recovery("no-extra", "a side file", side("%s.extra.json"))
no_recovery("no-step", "a step file", side("%s.plan.ran", "x"))
no_recovery("no-used", "a ledger with a decision", side("%s.decisions.jsonl", '{"n": 1, "kind": "mark"}\n{"n": 2, "kind": "decision"}\n'))
no_recovery("no-pushed", "a branch on origin", lambda slug: sh(tmp, "push", "-q", "origin", "loop/" + slug))
no_recovery("no-handed", "a handover record", lambda slug: handover(slug, {"state": {"slug": slug}}))
no_recovery("no-pr", "a pull request", lambda slug: None, TOY_PRS='[{"number": 7}]')
no_recovery("no-read", "an unreadable pull request list", lambda slug: None, TOY_PRS="nonsense")
no_recovery("no-flow", "a record with a finished step", queued_with(flow={"idea": "done"}))
no_recovery("no-session", "a record with a session", queued_with(session={"id": "s1"}))
sh(tmp, "remote", "set-url", "origin", os.path.join(home, "gone.git"))
fresh("no-origin")
lose("no-origin")
said = recover("no-origin")
check("REFUSED" in said and "origin" in said and not record("no-origin"), "recovery refuses an origin it can't reach: " + said.strip()[:110])
sh(tmp, "remote", "set-url", "origin", origin)

# the background starter marks the same way
sh(tmp, "switch", "-q", "main")
sh(tmp, "reset", "-q", "--hard", "origin/main")
made = subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, %r); import watch\n"
                       "watch.freeze({'slug': 'bg', 'goal': 'Do bg', 'done': ['bg works'], 'touches': ['a.py'], 'depends': []}, {'base': 'main'})"
                       % os.path.join(root, "skills", "workflow-monitoring", "scripts")], capture_output=True, text=True, cwd=tmp, env=env)
got = record("bg")
check(got.get("one_review") and got.get("step") == "idea" and ledger("bg") == ["mark"]
      and "- Review: one" in sh(tmp, "show", "loop/bg:.loop/goals/bg.md"), "watch's freeze marks the goal: %s" % made.stderr.strip()[-160:])

os.remove(os.path.join(runs, "bg.json"))
again = subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, %r); import watch\n"
                        "watch.freeze({'slug': 'bg', 'goal': 'Do bg', 'done': ['other'], 'touches': [], 'depends': []}, {'base': 'main'})"
                        % os.path.join(root, "skills", "workflow-monitoring", "scripts")], capture_output=True, text=True, cwd=tmp, env=env)
check("goal.py recover bg" in again.stderr and not record("bg"), "watch never freezes a committed goal twice: %s" % again.stderr.strip()[-120:])

# merge refuses until the start review is answered
done = dict(record("new-era"), status="done", step="ship", pr="https://github.com/o/r/pull/7", flow={s: "done" for s in ("idea", "plan", "review", "qa", "ship")})
json.dump(done, open(os.path.join(runs, "new-era.json"), "w"))
merge_py = os.path.join(root, "skills", "workflow-release", "scripts", "merge.py")
got = subprocess.run([sys.executable, merge_py, "new-era"], capture_output=True, text=True, cwd=tmp, env=env)
check("ONE_REVIEW_UNANSWERED" in got.stdout + got.stderr, "merge refuses an unanswered goal: %s" % (got.stdout + got.stderr).strip()[:140])
lost = {k: v for k, v in done.items() if k not in ("one_review", "start_required")}
lost.update(slug="bg", goal="Do bg", branch="loop/bg")
json.dump(lost, open(os.path.join(runs, "bg.json"), "w"))
got = subprocess.run([sys.executable, merge_py, "bg"], capture_output=True, text=True, cwd=tmp, env=env)
check("ONE_REVIEW_UNANSWERED" in got.stdout + got.stderr,
      "merge reads the committed mark when the record lost it: %s" % (got.stdout + got.stderr).strip()[:140])
import start_review  # noqa: E402
check(start_review.unanswered({"slug": "x"}) == "" and start_review.unanswered({"slug": "x", "start_required": {"why": "t"}}) != ""
      and start_review.unanswered({"slug": "x", "start_required": {"why": "t"}, "start_answer": {"record": "o1"}}) == ""
      and start_review.unanswered({"slug": "x", "one_review": {"at": "t"}}) != "", "a marked or required goal is unanswered until an answer is saved")

os.environ.get("TOY_SHOW") and print(open(os.path.join(home, "last.txt")).read())
print("ALL PASS" if not failed else "%d FAILED" % len(failed))
sys.exit(1 if failed else 0)
