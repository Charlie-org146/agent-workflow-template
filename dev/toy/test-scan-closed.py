#!/usr/bin/env python3
# windows: skip
# reads: skills/workflow-delivery/scripts/private.py skills/workflow-release/scripts/autorelease.py skills/workflow-monitoring/scripts/replan.py
# reads: skills/workflow-delivery/scripts/routing.py skills/workflow-regression/scripts/actions.py
"""scan-fail-closed (o675, TD527, DEL-9): with no private-name list the scan stops, it never reads clean.

The toy keeps its own fixture lists and prints only paths and counts. 1. `private.py scan`: no list exits 2 with one line naming the
missing list (unexpanded, no home path); an empty list passes; a list with a planted hit fails and names the place; a list that
doesn't hit passes (negative control: only the list differs). 2. The hooks (staged, message, push) exit 2 with no list and 0 with an
empty one. 3. Each caller stops: refusal() (goal.py pr, guards finding), autorelease.private_check (merge.py, release, wiki),
replan's pre-flight and routing finish's gate (the same `private.py scan`). 4. A row's environment carries an explicit empty list
(row_env) unless one is set, and the scheduled workflow sets it for its steps, so CI passes honestly instead of silently."""
import importlib.util
import os
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
skills = os.path.join(root, "skills")
PRIVATE = os.path.join(skills, "workflow-delivery", "scripts", "private.py")
sys.dont_write_bytecode = True
failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def load(name, *parts):
    sys.path.insert(0, os.path.join(skills, parts[0], "scripts"))
    spec = importlib.util.spec_from_file_location(name, os.path.join(skills, *parts))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git(cwd, *args):
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t"] + list(args), cwd=cwd, check=True, capture_output=True)


with tempfile.TemporaryDirectory() as tmp:
    home = os.path.join(tmp, "home")
    os.makedirs(home)
    repo = os.path.join(tmp, "repo")
    os.makedirs(repo)
    git(repo, "init", "-q", "-b", "main")
    open(os.path.join(repo, "a.txt"), "w").write("base\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "base")
    git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
    git(repo, "checkout", "-qb", "goal")
    open(os.path.join(repo, "b.txt"), "w").write("an ordinary change\nplantedword is here\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "change")
    empty = os.path.join(tmp, "empty-list")
    open(empty, "w").close()
    quiet = os.path.join(tmp, "quiet-list")
    open(quiet, "w").write("# nothing private\nnomatchword\n")
    planted = os.path.join(tmp, "planted-list")
    open(planted, "w").write("# the fixture's own list\nplantedword\n")
    base = {k: v for k, v in os.environ.items() if k not in ("LOOP_PRIVATE_NAMES", "LOOP_HOOK_RANGE", "LOOP_ROLE")}
    base.update(HOME=home, USERPROFILE=home)

    def run(args, names=None, stdin=""):
        env = dict(base, LOOP_PRIVATE_NAMES=names) if names is not None else dict(base)
        done = subprocess.run([sys.executable, PRIVATE] + args, cwd=repo, env=env, capture_output=True, text=True, input=stdin)
        return done.returncode, done.stdout + done.stderr

    code, out = run(["scan", "--base", "origin/main"])
    lines = [x for x in out.splitlines() if x.strip()]
    check(code == 2 and len(lines) == 1 and "no private-name list at ~/.workflow-loop/private-names" in out and "(PRIVATE_LIST)" in out and home not in out,
          "no list: scan exits 2 with one line naming the missing list, unexpanded (exit %d, %d line)" % (code, len(lines)))
    code, out = run(["scan", "--base", "origin/main"], empty)
    check(code == 0 and "REFUSED" not in out, "an empty list passes the scan (exit %d)" % code)
    code, out = run(["scan", "--base", "origin/main"], quiet)
    check(code == 0 and "HIT" not in out, "negative control: a list that does not hit passes, only the missing list stopped the scan (exit %d)" % code)
    code, out = run(["scan", "--base", "origin/main"], planted)
    check(code == 2 and "HIT b.txt:2" in out and "plantedword" not in out.replace("plantedword is", ""), "a planted hit fails, naming the place and never the text (exit %d)" % code)
    code, out = run(["scan", "--base", "origin/main"], os.path.join(tmp, "absent-list"))
    check(code == 2 and "PRIVATE_LIST" in out and "doesn't exist" in out, "a list named by LOOP_PRIVATE_NAMES that is missing still stops (exit %d)" % code)

    msg = os.path.join(tmp, "msg")
    open(msg, "w").write("an ordinary message\n")
    git(repo, "checkout", "-q", "main")
    open(os.path.join(repo, "c.txt"), "w").write("staged\n")
    git(repo, "add", "c.txt")
    for mode, arg, stdin in (("staged", [], ""), ("message", [msg], ""), ("push", [], "refs/heads/goal %s refs/heads/goal %s\n" % ("0" * 40, "0" * 40))):
        code, out = run(["hook", mode] + arg, stdin=stdin)
        check(code == 2 and "PRIVATE_LIST" in out and "no private-name list at" in out, "hook %s with no list stops (exit %d)" % (mode, code))
        code, out = run(["hook", mode] + arg, empty, stdin)
        check(code == 0, "negative control: hook %s with an empty list passes (exit %d)" % (mode, code))

    os.environ.update(HOME=home, USERPROFILE=home)
    os.environ.pop("LOOP_PRIVATE_NAMES", None)
    private = load("private", "workflow-delivery", "scripts", "private.py")
    found = private.scan(repo, "origin/main", {"pr-title": "a title"})
    stop = private.refusal(found, "origin/main")
    check(found["state"] == "none" and stop and stop[2] == "PRIVATE_LIST" and "no private-name list at" in stop[0],
          "refusal() (goal.py pr and the finding guard) stops on no list with PRIVATE_LIST")
    os.environ["LOOP_PRIVATE_NAMES"] = empty
    check(private.refusal(private.scan(repo, "origin/main", {"pr-title": "a title"}), "origin/main") is None, "negative control: refusal() lets an empty list go on")
    os.environ.pop("LOOP_PRIVATE_NAMES")
    auto = load("autorelease", "workflow-release", "scripts", "autorelease.py")
    stop = auto.private_check(repo, "origin/main", {"release notes": "notes"})
    check(stop and stop[2] == "PRIVATE_LIST", "autorelease.private_check (merge.py, release, wiki publish) stops on no list")
    os.environ["LOOP_PRIVATE_NAMES"] = empty
    check(auto.private_check(repo, "origin/main", {"release notes": "notes"}) is None, "negative control: private_check lets an empty list go on")
    os.environ.pop("LOOP_PRIVATE_NAMES")
    replan = load("replan", "workflow-monitoring", "scripts", "replan.py")
    hits = replan.private_hits(repo, ["a.txt"])
    check(len(hits) == 1 and "no private-name list at" in hits[0], "replan's pre-flight asks about a missing list instead of reading clean")
    os.environ["LOOP_PRIVATE_NAMES"] = empty
    check(replan.private_hits(repo, ["a.txt"]) == [], "negative control: replan's pre-flight is clean with an empty list")
    os.environ.pop("LOOP_PRIVATE_NAMES")
    routing_src = open(os.path.join(skills, "workflow-delivery", "scripts", "routing.py")).read()
    check('gate(os.path.join(here, "private.py"), "scan", "--base", base)' in routing_src,
          "routing finish gates on private.py scan, whose exit 2 above is its stop")

actions = load("actions", "workflow-regression", "scripts", "actions.py")
os.environ.pop("LOOP_PRIVATE_NAMES", None)
check(actions.row_env()["LOOP_PRIVATE_NAMES"] == os.devnull, "a row's environment carries an explicit empty list when none is set")
os.environ["LOOP_PRIVATE_NAMES"] = "/somewhere/list"
check(actions.row_env()["LOOP_PRIVATE_NAMES"] == "/somewhere/list", "negative control: a list that is set is kept")
flow = actions.render("17 */4 * * *")
check("LOOP_PRIVATE_NAMES: /dev/null" in flow, "the scheduled workflow sets the explicit empty list for the rows it runs")
committed = os.path.join(root, ".github", "workflows", "regression.yml")
check(not os.path.exists(committed) or "LOOP_PRIVATE_NAMES: /dev/null" in open(committed).read(), "the committed regression.yml sets it too")
sys.exit(1 if failed else 0)
