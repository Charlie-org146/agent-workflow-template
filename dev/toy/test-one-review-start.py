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
open(os.path.join(fake, "sitecustomize.py"), "w").write('''import subprocess
_run = subprocess.run
def run(args, *a, **k):
    if args and args[0] == "gh":
        return subprocess.CompletedProcess(args, 0, '{"url": "https://github.com/o/r/pull/7", "state": "OPEN"}', "")
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

# merge refuses until the start review is answered
done = dict(got, status="done", step="ship", pr="https://github.com/o/r/pull/7", flow={s: "done" for s in ("idea", "plan", "review", "qa", "ship")})
json.dump(done, open(os.path.join(runs, "new-era.json"), "w"))
merge_py = os.path.join(root, "skills", "workflow-release", "scripts", "merge.py")
got = subprocess.run([sys.executable, merge_py, "new-era"], capture_output=True, text=True, cwd=tmp, env=env)
check("ONE_REVIEW_UNANSWERED" in got.stdout + got.stderr, "merge refuses an unanswered goal: %s" % (got.stdout + got.stderr).strip()[:140])
import start_review  # noqa: E402
check(start_review.unanswered({"slug": "x"}) == "" and start_review.unanswered({"slug": "x", "start_required": {"why": "t"}}) != ""
      and start_review.unanswered({"slug": "x", "start_required": {"why": "t"}, "start_answer": {"record": "o1"}}) == ""
      and start_review.unanswered({"slug": "x", "one_review": {"at": "t"}}) != "", "a marked or required goal is unanswered until an answer is saved")

print("ALL PASS" if not failed else "%d FAILED" % len(failed))
sys.exit(1 if failed else 0)
