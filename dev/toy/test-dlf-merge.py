#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-release/scripts/merge.py skills/workflow-release/scripts/autorelease.py skills/workflow-delivery/scripts/dlf.py skills/workflow-delivery/scripts/guards.py
"""DLF-1.1 (merge on green): a goal with open deliver-first lines on its release issue still merges: lines never hold a merge, only the
full GitHub run (here, the pull request being open at the head the lane passed) does. A goal that failed for another reason is still
refused (negative control). Throwaway repo with a bare origin; gh is stood in for inside this process; the lines are filed through a fake
gh on PATH with a planted private-name list. No network."""
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(root, "skills", "workflow-release", "scripts"))
sys.path.insert(0, os.path.join(root, "skills", "workflow-delivery", "scripts"))
os.environ["LOOP_ROLE"] = "worker"
fails = 0


def check(name, ok, extra=""):
    global fails
    print(("PASS: " if ok else "FAIL: ") + name + ("" if ok else "  " + extra))
    fails += 0 if ok else 1


def git(*args, cwd=None):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "core.autocrlf=false"] + list(args),
                          cwd=cwd or repo, capture_output=True, text=True)


tmp = tempfile.mkdtemp(prefix="dlf-merge-")
os.makedirs(os.path.join(tmp, "bin"))
os.symlink(os.path.join(root, "dev", "toy", "dlf-gh"), os.path.join(tmp, "bin", "gh"))
os.makedirs(os.path.join(tmp, "fake"))
open(os.path.join(tmp, "names"), "w").write("acmesecret\n")
os.environ.update(HOME=tmp, USERPROFILE=tmp, PATH=os.path.join(tmp, "bin") + os.pathsep + os.environ["PATH"], DLF_FAKE_DIR=os.path.join(tmp, "fake"), LOOP_PRIVATE_NAMES=os.path.join(tmp, "names"))
origin, repo = os.path.join(tmp, "origin.git"), os.path.join(tmp, "repo")
git("init", "-q", "--bare", "-b", "main", origin, cwd=tmp)
git("clone", "-q", origin, repo, cwd=tmp)
git("config", "user.name", "t"); git("config", "user.email", "t@t")  # repo-local: release.py commits in a subprocess that the -c options above do not reach (a runner has no global identity)
os.makedirs(os.path.join(repo, ".loop"))
open(os.path.join(repo, ".loop", "config.json"), "w").write('{"auto_merge": true, "base": "main"}\n')
open(os.path.join(repo, "a.txt"), "w").write("a\n")
git("add", "-A"); git("commit", "-q", "-m", "base"); git("push", "-q", "origin", "main")
base = git("rev-parse", "HEAD").stdout.strip()
git("switch", "-q", "-c", "loop/g"); open(os.path.join(repo, "a.txt"), "a").write("a2\n")
git("commit", "-q", "-am", "goal work"); git("push", "-q", "origin", "loop/g")
head = git("rev-parse", "HEAD").stdout.strip()
common = os.path.abspath(os.path.join(repo, git("rev-parse", "--git-common-dir").stdout.strip()))
record = os.path.join(common, "loop", "runs", "g.json")
os.makedirs(os.path.dirname(record), exist_ok=True)

import merge  # noqa: E402

gh_merge_rc = [1]
real_run = subprocess.run


def fake_run(args, *a, **k):
    if args and args[0] == "gh":
        if args[1:3] == ["pr", "view"]:
            return subprocess.CompletedProcess(args, 0, json.dumps({"state": "OPEN", "headRefOid": head}), "")
        if args[1:3] == ["pr", "merge"]:
            return subprocess.CompletedProcess(args, gh_merge_rc[0], "", "merge refused by the branch rule" if gh_merge_rc[0] else "")
        if args[1:3] == ["release", "view"]:
            return subprocess.CompletedProcess(args, 1, "", "release not found")
        return subprocess.CompletedProcess(args, 0, "https://example.test/release/1\n", "")
    return real_run(args, *a, **k)


def write(**more):
    state = {"slug": "g", "branch": "loop/g", "status": "done", "step": "release", "pr": "https://example.test/pull/1",
             "pr_base": base, "pr_head": head, "report": {}}
    state.update(more)
    json.dump(state, open(record, "w"), indent=2)


def read():
    return json.load(open(record))


def merge_g():
    """(exit, output) of merge.py g inside the throwaway repo."""
    out, err, old = io.StringIO(), io.StringIO(), os.getcwd()
    os.chdir(repo)
    sys.argv = ["merge.py", "g"]
    subprocess.run = fake_run
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = merge.main()
            except SystemExit as stop:
                code = stop.code
                print(code)
    finally:
        subprocess.run = real_run
        os.chdir(old)
        lock = os.path.join(repo, ".git", "loop", "merge.lock")
        os.path.exists(lock) and os.unlink(lock)  # the pod lock is dropped when a merge.py process exits; these runs share one process
    return code, out.getvalue() + err.getvalue()


write()
import dlf  # noqa: E402
runs = os.path.dirname(record)
ids = [dlf.file_line(repo, runs, "g", "v1", "break", "other", "b%d" % n, "a break", "settle words", "accept")[0] for n in (1, 2, 3)]
ids.append(dlf.file_line(repo, runs, "g", "v1", "plan", "other", "plan1", "the plan is past its review cap", "settle words", "accept")[0])
ids.append(dlf.cap_line(repo, runs, "g", "v1", 480, 240, 240, 480)[0])
posted = json.load(open(os.path.join(tmp, "fake", "state.json")))["comments"]["1"]
check("DLF-1.1: the goal has five open lines on the release's one issue", len(posted) == 5 and all(ids), str(ids))
gh_merge_rc[0] = 0
code, said = merge_g()
state = read()
check("DLF-1.1: with five open lines the goal still merges on green", code in (0, None) and "MERGED https://example.test/pull/1" in said, said[-300:])
check("and ends done and released: no line held it", state["status"] == "done" and state.get("release") in ("merged", "cut"), str(state))
write(status="failed")  # negative control: a goal that failed for another reason is still refused
code, said = merge_g()
check("a goal that failed with no release error is still refused (negative control)", code not in (0, None) and "has no finished pull request" in said, said[-200:])
sys.exit(1 if fails else 0)
