#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-release/scripts/merge.py skills/workflow-release/scripts/autorelease.py skills/workflow-delivery/scripts/guards.py
"""merge-refused (#4004): a merge.py that is refused (here gh refuses the merge) leaves the goal failed, never done, while
its pull request is open: the board shows it unfinished and goal.py resume can revive it (it takes only a failed or
stopped goal). merge.py run again takes a goal a refusal left failed, merges it and ends it done; a goal that failed for
another reason is still refused.

Builds a throwaway repo with a bare origin; gh is stood in for inside this process (no network). usage: test-merge-refused.py"""
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(root, "skills", "workflow-release", "scripts"))
os.environ["LOOP_ROLE"] = "worker"
fails = 0


def check(name, ok, extra=""):
    global fails
    print(("PASS: " if ok else "FAIL: ") + name + ("" if ok else "  " + extra))
    fails += 0 if ok else 1


def git(*args, cwd=None):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "core.autocrlf=false"] + list(args),
                          cwd=cwd or repo, capture_output=True, text=True)


tmp = tempfile.mkdtemp(prefix="merge-refused-")
origin, repo = os.path.join(tmp, "origin.git"), os.path.join(tmp, "repo")
git("init", "-q", "--bare", "-b", "main", origin, cwd=tmp)
git("clone", "-q", origin, repo, cwd=tmp)
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
    return code, out.getvalue() + err.getvalue()


write()
code, said = merge_g()
state = read()
check("merge.py refused by gh exits non-zero and records the release error", code not in (0, None) and "gh could not merge" in said and state.get("release_error"), said)
check("the refused goal is failed, not done, at the same step", state["status"] == "failed" and state["step"] == "release", str(state["status"]))
check("its pull request stays recorded and no merge is marked", state["pr"] and not state.get("release"))
gate = (state["status"] in ("failed", "stopped"))  # goal.py resume's own gate (guards.cmd_resume)
resume = real_run([sys.executable, os.path.join(root, "skills", "workflow-delivery", "scripts", "goal.py"), "resume", "g", "--why", "retry"],
                  cwd=repo, capture_output=True, text=True, env=dict(os.environ, LOOP_ROLE=""))
check("goal.py resume no longer refuses it as finished (RESUME_STATUS)", gate and "(RESUME_STATUS)" not in resume.stdout + resume.stderr,
      (resume.stdout + resume.stderr)[-200:])
gh_merge_rc[0] = 0
code, said = merge_g()
state = read()
check("merge.py run again merges the goal a refusal left failed", code in (0, None) and "MERGED https://example.test/pull/1" in said, said[-300:])
check("and the goal ends done and released, with the release error gone", state["status"] == "done" and state.get("release") in ("merged", "cut") and not state.get("release_error"), str(state))
write(status="failed")  # failed for another reason: no release error
code, said = merge_g()
check("a goal that failed with no release error is still refused", code not in (0, None) and "has no finished pull request" in said, said[-200:])
sys.exit(1 if fails else 0)
