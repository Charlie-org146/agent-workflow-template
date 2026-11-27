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

# the start review: the items, one code, and the one answer (E1, B1, DX D3, D4, RT1, RT7, RT14)
sh(tmp, "reset", "-q", "--hard")
sh(tmp, "worktree", "remove", "--force", os.path.join(tmp, ".git", "loop", "worktrees", "bg"))
os.rmdir(os.path.join(tmp, ".git", "loop", "worktrees"))
fresh("ask")
tool("step", "ask", "plan")


def words(text, who="operation", at=None):
    rows = os.path.join(tmp, ".git", "loop", "owner-words.tsv")
    n = (len(open(rows).read().splitlines()) if os.path.exists(rows) else 0) + 1
    open(rows, "a").write("o%d\t%s\t%s\t%s\task\n" % (n, at or "2099-01-01T00:00:%02dZ" % n, who, json.dumps(text)))
    return "o%d" % n


def items(slug, rows, role="operation"):
    path = os.path.join(home, "items.json")
    json.dump(rows, open(path, "w"))
    return tool("start-items", slug, "--file", path, role=role)


def answer(slug, rid, role="operation"):
    return tool("start", slug, "--owner-record", rid, role=role)


def code_of(said):
    return (said.split("approve start ask ", 1)[1].split()[0]) if "approve start ask " in said else "none"


said = tool("start-review", "ask", role="operation")
check("no start review yet" in said and "start-items ask" in said, "before the items are recorded the review says so: " + said.strip()[:100])
check("no start review yet" in answer("ask", words("approve start ask abc123")), "an answer before the message is refused")
TWO = [{"class": "a test loosened or deleted", "action": "delete one old test", "files": ["a.py"], "recommend": "approve"},
       {"class": "security and sandbox settings", "action": "edit the loop config", "files": [".loop/config.json"], "recommend": "refuse"}]
check("a worker can't" in items("ask", TWO, role="worker"), "a worker records no items")
for bad, why in (([dict(TWO[0], files=["."])], "the repository"), ([dict(TWO[0], files=["skills/x/scripts"])], "a scripts folder"),
                 ([dict(TWO[0], files=["nowhere/"])], "a folder that is not there"), ([dict(TWO[0], **{"class": "made up"})], "an unknown class"),
                 ([dict(TWO[0], files=["../x"])], "a path outside")):
    got = items("ask", bad)
    check("ONE_REVIEW_ITEMS" in got and "start_review" not in record("ask"), "items naming %s are refused: %s" % (why, got.strip()[:90]))
said = items("ask", TWO)
shown = tool("start-review", "ask", role="operation")
code = code_of(shown)
check(len(code) == 6 and "1. a test loosened or deleted: delete one old test (a.py); recommended: approve" in shown
      and "2. security and sandbox settings" in shown and "1. ask works" in shown and "reject start ask " + code in shown
      and "Without an answer" in shown, "the message has the done lines, numbered items, one code and every answer form: %s" % shown[:200])
old_code = code
items("ask", TWO[:1] + [dict(TWO[1], action="edit two keys of the loop config")])
code = code_of(tool("start-review", "ask", role="operation"))
check(code != old_code, "a changed item changes the code")


def refusal(rid, why, expect):
    got = answer("ask", rid)
    check(expect in got and "start_answer" not in record("ask") and code in got, "%s is refused with the current code: %s" % (why, got.strip()[:130]))


refusal(words("approve start ask " + old_code), "an old code", "ONE_REVIEW_ANSWER")
refusal(words("yes, go on"), "other words", "ONE_REVIEW_ANSWER")
refusal(words("approve start ask %s and also merge it" % code), "extra words", "ONE_REVIEW_ANSWER")
refusal(words("approve start frz " + code), "another goal's name", "ONE_REVIEW_ANSWER")
refusal(words("approve start ask " + code, at="2000-01-01T00:00:00Z"), "a record older than the message", "ONE_REVIEW_ANSWER")
refusal(words("approve start ask " + code, who="operation-top:delegated:TD1:DOC-2:r1"), "a delegated record", "ONE_REVIEW_ANSWER")
refusal(words("approve start ask " + code, who="operation-top"), "a relayed record when there are safety items", "ONE_REVIEW_ANSWER")
refusal(words("approve start ask %s except 3" % code), "an item that is not there", "ONE_REVIEW_ANSWER")
refusal("o999", "a missing record", "ONE_REVIEW_ANSWER")
rid = words("approve start ask %s except 2" % code)
check("a worker can't" in answer("ask", rid, role="worker"), "a worker answers nothing")
said = answer("ask", rid)
got = record("ask").get("start_answer") or {}
check("STARTED ask" in said and got.get("record") == rid and got.get("text") == "approve start ask %s except 2" % code
      and [(i["n"], i["approved"], i["files"]) for i in got.get("items", [])] == [(1, True, ["a.py"]), (2, False, [".loop/config.json"])]
      and ledger("ask") == ["mark", "start", "refused-item"], "the answer keeps each item and the record's text: %s" % said.strip()[:160])
check("accepted once" in answer("ask", words("approve start ask " + code)), "an answer is accepted once")
check("STEP ask build" in tool("step", "ask", "build"), "build goes on once answered")
check("accepted once" in items("ask", TWO), "the items are final after the answer")
fresh("no-go")
items("no-go", [])
shown = tool("start-review", "no-go", role="operation")
code = shown.split("approve start no-go ", 1)[1].split()[0] if "approve start no-go " in shown else "none"
said = answer("no-go", words("reject start no-go " + code, who="operation-top"))
check("REJECTED no-go" in said and record("no-go").get("status") == "stopped" and "stop" in (ledger("no-go") or []),
      "a reject stops the goal for good: " + said.strip()[:140])
check("stopped for good" in tool("resume", "no-go", "--why", "again", role="operation") or "ONE_REVIEW" in tool("step", "no-go", "build"),
      "a rejected goal doesn't build")

# a goal adopted with a start review required is marked only by its answer, in the record and the committed goal file
sh(tmp, "reset", "-q", "--hard")
branch("older-ans", base=OFF)
commit(tmp, ".loop/config.json", json.dumps(dict(CONFIG, one_review=False)), "keep off")
json.dump({"slug": "older-ans", "status": "running", "step": "idea", "flow": {}, "pid": None, "branch": "loop/older-ans", "worktree": tmp,
           "touches": ["a.py"], "goal": "Do older", "log": [], "tries": 0, "done_sha": __import__("hashlib").sha256(b"1. older-ans works").hexdigest(),
           "start_required": {"why": "t"}}, open(os.path.join(runs, "older-ans.json"), "w"))
items("older-ans", [])
shown = tool("start-review", "older-ans", role="operation")
code = shown.split("approve start older-ans ", 1)[1].split()[0] if "approve start older-ans " in shown else "none"
said = answer("older-ans", words("approve start older-ans " + code))
check("STARTED older-ans" in said and record("older-ans").get("one_review") and "- Review: one" in goal_in_head("older-ans")
      and "- Review: one" in sh(tmp, "show", "origin/loop/older-ans:.loop/goals/older-ans.md") and ledger("older-ans") == ["mark", "start"],
      "an older goal's answer marks it, commits the mark and pushes it: %s" % said.strip()[:200])

# a start answer is no other permission: every other reader of owner records leaves it out (E15, M1)
sh(tmp, "reset", "-q", "--hard")
START = words("approve start ask abc123", who="operation")
ALSO = words("  Reject   Start zzz 000000", who="operation")
PLAIN = words("keep going", who="operation")
common = os.path.join(tmp, ".git", "loop")
rows = [line.split("\t") for line in open(os.path.join(common, "owner-words.tsv")).read().splitlines()]
open(os.path.join(common, "owner-words.tsv"), "w").write("".join("\t".join(r[:4] + ["ask,v9.0.0,full-auto-rule,always-ask:*"]) + "\n" for r in rows))
put(tmp, "docs/wiki/D.md", "### DOC-2\n\n| rev | date |\n|---|---|\n| r1 | x |\n")
delegated = words("approve start ask abc123", who="operation-top:delegated:TD1:DOC-2:r1")
put(tmp, ".loop/queue.md", "")
put(tmp, ".loop/goals/ask.plan.md", "plan\n")
probe = r"""
import argparse, json, os, subprocess, sys
root, tmp, common, START, ALSO, PLAIN, DEL = sys.argv[1:]
for skill in ("workflow-monitoring", "workflow-docs", "workflow-release"):
    sys.path.append(os.path.join(root, "skills", skill, "scripts"))
os.chdir(tmp)
git = lambda *a: subprocess.run(["git"] + list(a), capture_output=True, text=True, check=True).stdout.strip()
def said(call):
    try:
        return "got %r" % (call(),)
    except SystemExit as stop:
        return "refused %s" % stop.code
import auto, board_log, board_model, notify, deployments, criteria, milestones, review
out = {}
ids = [r[0] for r in auto.owner_rows(tmp)]
out["rows"] = [START in ids, ALSO in ids, PLAIN in ids]
out["count"] = auto.add_owner_words(argparse.Namespace(text="more words", delegated="", via="owner", doc2=""), ["x"]) == len(open(os.path.join(common, "owner-words.tsv")).readlines())
red = board_log.red_dir(tmp); os.makedirs(red, exist_ok=True)
json.dump({"sha": board_log.plan_sha(tmp, "ask"), "breaks": [{"principle": 1, "text": "b"}]}, open(os.path.join(red, "plan-ask.json"), "w"))
out["plan_accept"] = [said(lambda r=r: board_model.plan_accept(tmp, "ask", 1, r)) for r in (START, PLAIN)]
pending = os.path.join(common, "toy-plan.json"); json.dump({"status": "pending", "goals": []}, open(pending, "w"))
out["approve"] = said(lambda: notify.approve(argparse.Namespace(owner_record=START, rest=[]), pending, tmp, os.path.dirname(common)))
args = lambda r: argparse.Namespace(owner_record=r, command="review", ids=["ask"])
out["docs"] = [said(lambda r=r: deployments.owner_words(args(r), git)) for r in (START, PLAIN)]
out["delegated"] = criteria.delegated(tmp, DEL, "plain")
out["milestone"] = [bool(milestones.record(r, "ask", "ask")) for r in (START, PLAIN)]
table = [r[0] for r in review.table(tmp, "owner-words.tsv")]
out["release"] = [START in table, PLAIN in table]
print("OUT " + json.dumps(out))
"""
ran = subprocess.run([sys.executable, "-c", probe, root, tmp, common, START, ALSO, PLAIN, delegated], capture_output=True, text=True, env=env)
got = json.loads(ran.stdout.split("OUT ", 1)[1]) if "OUT " in ran.stdout else {}
got or print(ran.stderr[-1500:])
check(got.get("rows") == [False, False, True], "the shared reader leaves start answers out: %s" % got.get("rows"))
check(got.get("count") is True, "record numbers still count every record")
acc = got.get("plan_accept") or ["", ""]
check(acc[0].startswith("refused") and acc[1].startswith("got 'ACCEPTED"), "a start answer accepts no plan break: %s" % acc[0][:90])
check("takes the owner's words" in got.get("approve", ""), "a start answer approves no plan round: %s" % got.get("approve", "")[:90])
docs = got.get("docs") or ["", ""]
check("ONE_REVIEW_UNAPPROVED" in docs[0] and docs[1].startswith("got 'record "), "the docs commands refuse it: %s" % docs[0][:110])
check(got.get("delegated") in (False, None), "it is no delegated approval: %r" % got.get("delegated"))
check(got.get("milestone") == [False, True], "it is no milestone record: %s" % got.get("milestone"))
check(got.get("release") == [False, True], "it is no release record or waiver: %s" % got.get("release"))

# the start mail: sent once per code, after the items are recorded, with no other answer words (E6, CEO B2, DX D1)
import http.server  # noqa: E402
import threading  # noqa: E402
posts, refuse_mail = [], [False]


class Stub(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        got = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
        refuse_mail[0] or posts.append(got)
        body = b'{"success": false}' if refuse_mail[0] else b'{"success": true, "result": {}}'
        self.send_response(400 if refuse_mail[0] else 200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


server = http.server.HTTPServer(("127.0.0.1", 0), Stub)
threading.Thread(target=server.serve_forever, daemon=True).start()
mail_env = os.path.join(home, "mail.env")
open(mail_env, "w").write("DIGEST_TO=owner@example.invalid\nDIGEST_FROM=loop@example.invalid\nCLOUDFLARE_ACCOUNT_ID=a\nCLOUDFLARE_EMAIL_TOKEN=toy\n")
os.chmod(mail_env, 0o600)
env.update(LOOP_MAIL_ENV=mail_env, DIGEST_MAIL_RETRY_SECONDS="0", DIGEST_MAIL_API="http://127.0.0.1:%d" % server.server_address[1])
sh(tmp, "reset", "-q", "--hard")
for other in os.listdir(runs):  # only this goal's events are mailed in this part
    os.remove(os.path.join(runs, other))
fresh("mailed")


def mail_on(on):
    open(os.path.join(home, "flow.json"), "w").write(json.dumps({"notify_email": on, "steps": {s: "x" for s in ("idea", "plan", "review", "qa", "ship")}}))


mail_on(False)
said = items("mailed", [])
check("NOT MAILED" in said and "mail is off" in said and not posts, "with mail off the command says it was not mailed and why: " + said.strip()[-120:])
mail_on(True)
refuse_mail[0] = True
said = items("mailed", [])
check("NOT MAILED" in said and not posts, "a refused send is reported: " + said.strip()[-120:])
refuse_mail[0] = False
said = items("mailed", [])
text = posts[0].get("text", "") if posts else ""
check(len(posts) == 1 and "MAILED mailed" in said and "approve start mailed " in text and "1. mailed works" in text
      and "Reply with a number" not in text and '"approve"' not in text, "the next run sends the whole message once, with no other answer words: %s" % said.strip()[-90:])
said = items("mailed", [])
subprocess.run([sys.executable, os.path.join(root, "skills", "workflow-monitoring", "scripts", "notify.py"), "send", "--root", tmp], cwd=tmp, env=env, capture_output=True)
check(len(posts) == 1 and "already mailed" in said, "the same code is not sent again: " + said.strip()[-90:])
items("mailed", [{"class": "money", "action": "buy one seat", "files": [], "recommend": "refuse"}])
check(len(posts) == 2 and "buy one seat" in posts[-1].get("text", ""), "a new code is sent once more")
server.shutdown()

# an approved requirement change: one comparison of the whole unit at revise, review, guard, pr and merge (E1, B1, B2, M1, M3)
sh(tmp, "reset", "-q", "--hard")
sh(tmp, "switch", "-q", "-c", "pagebase", "origin/main")
PAGE = ("# F\n\n## Requirements\n\n- AB-1: **Reviewed 2026-11-01** Old heading <!-- reviewed deadbeef -->\n  - old sub [AB-1]\n\n"
        "- AB-2: **Reviewed 2026-11-01** Second one <!-- reviewed deadbeef -->\n\n## Revisions\n\n"
        "### AB-1\n\n| rev | date | text | why | approved |\n|---|---|---|---|---|\n| r1 | 2026-11-01 | Old heading <br> old sub [AB-1] | x | o1 |\n\n"
        "### AB-2\n\n| rev | date | text | why | approved |\n|---|---|---|---|---|\n| r1 | 2026-11-01 | Second one | x | o1 |\n")
commit(tmp, "docs/wiki/F.md", PAGE, "a page")
sh(tmp, "push", "-q", "origin", "HEAD:main")
fresh("page")
NEW = "New heading\n  - new sub [AB-1]"
items("page", [{"class": "a change to what a feature promises", "action": "reword AB-1", "files": ["docs/wiki/F.md"], "recommend": "approve",
                "page": "docs/wiki/F.md", "id": "AB-1", "text": NEW}])
shown = tool("start-review", "page", role="operation")
code = shown.split("approve start page ", 1)[1].split()[0] if "approve start page " in shown else "none"
rid = words("approve start page " + code)
rows = os.path.join(tmp, ".git", "loop", "owner-words.tsv")
text = open(rows).read().split("\n")
text = [line.rsplit("\t", 1)[0] + "\tpage,AB-1,AB-2,F" if line.startswith(rid + "\t") else line for line in text]
open(rows, "w").write("\n".join(text))
said = answer("page", rid)
check("STARTED page" in said, "a requirement item is answered: " + said.strip()[:100])


def docs(*args):
    got = subprocess.run([sys.executable, os.path.join(root, "skills", "workflow-docs", "scripts", "criteria.py")] + list(args),
                         capture_output=True, text=True, cwd=tmp, env=env)
    return got.returncode, (got.stdout + got.stderr).strip()


def revise(key, text, record_id=None):
    put(home, "new.txt", text.replace("\n  - ", "\n- ") + "\n")
    return docs("revise", key, "--owner-record", record_id or rid, "--why", "approved at the start", "--text-file", os.path.join(home, "new.txt"))


def page():
    return open(os.path.join(tmp, "docs", "wiki", "F.md")).read()


for key, text, why in (("AB-1", "New heading\n  - another sub [AB-1]", "another sub-bullet"), ("AB-1", "Newer heading\n  - new sub [AB-1]", "another heading"),
                       ("AB-1", "New heading", "a dropped sub-bullet"), ("AB-2", "Changed second", "an ID that wasn't approved")):
    code_, said = revise(key, text)
    check(code_ != 0 and "ONE_REVIEW_UNAPPROVED" in said and page() == PAGE, "revise refuses %s: %s" % (why, said[:110]))
code_, said = docs("retire", "AB-1", "--owner-record", rid, "--why", "x", "--as", "retired")
check(code_ != 0 and page() == PAGE, "the start record retires nothing: " + said[:90])
code_, said = revise("AB-1", NEW)
check(code_ == 0 and "**Unreviewed** New heading" in page() and "new sub [AB-1]" in page(), "revise takes exactly the approved unit: " + said[:130])
kept = page()
sh(tmp, "checkout", "-q", "--", "docs/wiki/F.md")
code_, said = revise("AB-1", NEW)
check(code_ != 0 and "already used" in said, "a record is used once for one ID and command: " + said[:110])
put(tmp, "docs/wiki/F.md", kept)
code_, said = docs("review", "F", "--user", "--owner-record", rid)
check(code_ != 0 and page() == kept, "it reviews no whole page: " + said[:100])
code_, said = docs("review", "AB-2", "--user", "--owner-record", rid)
check(code_ != 0 and page() == kept, "it reviews no other ID: " + said[:100])
code_, said = docs("review", "AB-1", "--user", "--owner-record", rid)
check(code_ == 0 and "- AB-1: **Reviewed " in page() and "New heading" in page(), "it reviews the approved ID: " + said[:130])
sh(tmp, "add", "docs/wiki/F.md")
sh(tmp, "commit", "-qm", "AB-1 as approved")


def guard():
    return docs("guard", "origin/main", "page")


def unapproved():
    state = record("page")
    return start_review_answer.unapproved(tmp, runs, state, "origin/main", "HEAD")


import start_answer as start_review_answer  # noqa: E402
os.chdir(tmp)
code_, said = guard()
check(code_ == 0 and unapproved() == [], "the guard and the comparison pass the approved unit: %s %s" % (said[:110], unapproved()))
good = page()
commit(tmp, "docs/wiki/F.md", good.replace("Second one <!--", "Second changed <!--"), "another promise, quietly")
check(unapproved() == ["AB-2 on docs/wiki/F.md"], "a change outside the approval is found: %s" % unapproved())
code_, said = guard()
check(code_ != 0 and "AB-2" in said, "and the guard refuses it: " + said[:100])
goal_file = ".loop/goals/page.md"
commit(tmp, goal_file, open(os.path.join(tmp, goal_file)).read().replace("1. page works", "1. page works and AB-2 changes"), "name it in a done line")
code_, said = guard()
check(code_ != 0 and "AB-2" in said, "on a marked goal a done line naming the ID doesn't pass the guard: " + said[:100])
sh(tmp, "reset", "-q", "--hard", "HEAD~2")
commit(tmp, "docs/wiki/F.md", good.replace("new sub [AB-1]", "slipped sub [AB-1]"), "edit the approved unit")
check(unapproved() == ["AB-1 on docs/wiki/F.md"], "an edit under the approved heading is found: %s" % unapproved())
sh(tmp, "reset", "-q", "--hard", "HEAD~1")
state = record("page")
# pr and merge run the same comparison; the guard alone doesn't see a newly added Reviewed requirement
commit(tmp, "docs/wiki/F.md", good.replace("\n## Revisions", "- AB-3: **Reviewed 2026-11-01** A new promise\n\n## Revisions"), "add a promise")
wired = r"""
import os, sys
root, tmp = sys.argv[1:]
for skill in ("workflow-delivery", "workflow-monitoring", "workflow-release"):
    sys.path.append(os.path.join(root, "skills", skill, "scripts"))
os.chdir(tmp)
import goal, role_gate, merge, machines
state = goal.load("page")
for name, call in (("PR", lambda: role_gate.requirement_gate(goal, "page")),
                   ("MERGE", lambda: merge.one_review_unapproved(state, tmp, os.path.join(tmp, ".git", "loop", "runs"), "main", "HEAD")),
                   ("BATCH", lambda: machines.batch_ready(merge, tmp, "main", dict(state, status="done", step="ship", pr="u", release="", flow={s: "done" for s in goal.FLOW})))):
    try:
        print(name, call())
    except SystemExit as stop:
        print(name, "refused", stop.code)
    except Exception as error:
        print(name, "error", type(error).__name__, error)
"""
ran = subprocess.run([sys.executable, "-c", wired, root, tmp], capture_output=True, text=True, env=env)
lines = {x.split(" ", 1)[0]: x for x in (ran.stdout + ran.stderr).splitlines() if x.split(" ", 1)[0] in ("PR", "MERGE", "BATCH")}
check("ONE_REVIEW_UNAPPROVED" in lines.get("PR", "") and "AB-3" in lines.get("PR", ""), "pr refuses an unapproved Reviewed requirement: %s" % lines.get("PR", ran.stderr[-300:])[:160])
check("AB-3" in lines.get("MERGE", "") and "ONE_REVIEW_UNAPPROVED" in lines.get("MERGE", ""), "merge's check refuses it on the head given: %s" % lines.get("MERGE", "")[:160])
check("merges on its own" in lines.get("BATCH", ""), "a one-review goal never joins a batch: %s" % lines.get("BATCH", "")[:160])
sh(tmp, "reset", "-q", "--hard", "HEAD~1")
sh(tmp, "switch", "-q", "-c", "moved-base", "origin/main")
commit(tmp, "docs/wiki/F.md", PAGE.replace("old sub [AB-1]", "someone else's newer sub [AB-1]"), "another goal changed AB-1")
sh(tmp, "switch", "-q", "loop/page")
check(start_review_answer.unapproved(tmp, runs, record("page"), "moved-base", "HEAD") == ["AB-1 on docs/wiki/F.md"],
      "an approval doesn't overwrite a unit the base changed since the start message")
for status in ("stopped", "failed", "retired"):
    check(start_review_answer.unapproved(tmp, runs, dict(state, status=status), "origin/main", "HEAD") != [], "no use while the goal is %s" % status)
sys.path.insert(0, delivery)
import decisions as ledger_tool  # noqa: E402
ledger_tool.stop(runs, "page", "t", "t")
check(unapproved() != [], "a permanent stop voids the approval for good")
os.chdir(root)

os.environ.get("TOY_SHOW") and print(open(os.path.join(home, "last.txt")).read())
print("ALL PASS" if not failed else "%d FAILED" % len(failed))
sys.exit(1 if failed else 0)
