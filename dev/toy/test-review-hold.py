#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-release/scripts/merge.py skills/workflow-release/scripts/review.py skills/workflow-monitoring/scripts/board_lines.py
"""review-hold (DEL-13, issue 3803): with "review_hold": true merge.py refuses REVIEW_HOLD and merges nothing until the
operation session records a review of the pull request's head (review.py record); a worker cannot record; a push after
the record voids it; the board's Issues says "merge waiting on review"; with the setting off merging is unchanged.

Builds a throwaway repo with a bare origin; gh is stood in for inside this process (no network). usage: test-review-hold.py [hold|merge|worker]  (one leg: only its checks decide the exit)"""
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(root, "skills", "workflow-release", "scripts"))
sys.path.insert(0, os.path.join(root, "skills", "workflow-monitoring", "scripts"))
fails = 0


LEG = sys.argv[1] if len(sys.argv) > 1 else ""


def check(name, ok, extra="", leg="hold"):
    global fails
    print(("PASS: " if ok else "FAIL: ") + name + ("" if ok else "  " + extra))
    fails += 0 if ok or (LEG and LEG != leg) else 1


def git(*args, cwd=None):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "core.autocrlf=false"] + list(args),
                          cwd=cwd or repo, capture_output=True, text=True)


tmp = tempfile.mkdtemp(prefix="review-hold-")
origin, repo = os.path.join(tmp, "origin.git"), os.path.join(tmp, "repo")
git("init", "-q", "--bare", "-b", "main", origin, cwd=tmp)
git("clone", "-q", origin, repo, cwd=tmp)
os.makedirs(os.path.join(repo, ".loop"))
config = os.path.join(repo, ".loop", "config.json")
open(config, "w").write('{"auto_merge": true, "base": "main", "review_hold": true}\n')
open(os.path.join(repo, "a.txt"), "w").write("a\n")
git("add", "-A"); git("commit", "-q", "-m", "base"); git("push", "-q", "origin", "main")
base = git("rev-parse", "HEAD").stdout.strip()
git("switch", "-q", "-c", "loop/g"); open(os.path.join(repo, "a.txt"), "a").write("a2\n")
git("commit", "-q", "-am", "goal work"); git("push", "-q", "origin", "loop/g")
head = git("rev-parse", "HEAD").stdout.strip()
common = os.path.abspath(os.path.join(repo, git("rev-parse", "--git-common-dir").stdout.strip()))
record = os.path.join(common, "loop", "runs", "g.json")
os.makedirs(os.path.dirname(record), exist_ok=True)

import board_lines  # noqa: E402
import merge  # noqa: E402
import review  # noqa: E402

merge.pods = None  # one process, many merges: no cross-pod lock
real_run, merged, tip = subprocess.run, [], [head]


def fake_run(args, *a, **k):
    if args and args[0] == "gh":
        if args[1:3] == ["pr", "view"]:
            return subprocess.CompletedProcess(args, 0, json.dumps({"state": "OPEN", "headRefOid": tip[0]}), "")
        if args[1:3] == ["pr", "merge"]:
            merged.append(args)
            return subprocess.CompletedProcess(args, 0, "", "")
        if args[1:3] == ["release", "view"]:
            return subprocess.CompletedProcess(args, 1, "", "release not found")
        return subprocess.CompletedProcess(args, 0, "https://example.test/release/1\n", "")
    return real_run(args, *a, **k)


def write(**more):
    git("fetch", "-q", "origin")
    now = git("rev-parse", "origin/main").stdout.strip()
    state = {"slug": "g", "branch": "loop/g", "status": "done", "step": "release", "pr": "https://example.test/pull/1",
             "pr_base": now, "pr_head": head, "report": {}}
    state.update(more)
    json.dump(state, open(record, "w"), indent=2)


def read():
    return json.load(open(record))


def call(fn, *argv, role="", hold=True):
    """(exit, output) of fn() inside the throwaway repo with LOOP_ROLE=role and gh stood in."""
    open(config, "w").write(json.dumps({"auto_merge": True, "base": "main", "review_hold": hold}) + "\n")
    out, old, saved = io.StringIO(), os.getcwd(), os.environ.get("LOOP_ROLE")
    os.chdir(repo)
    os.environ["LOOP_ROLE"] = role
    sys.argv = ["x"] + list(argv)
    subprocess.run = fake_run
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            try:
                code = fn()
            except SystemExit as stop:
                code = stop.code
                print(code)
    finally:
        subprocess.run = real_run
        os.chdir(old)
        os.environ["LOOP_ROLE"] = saved or ""
    return code, out.getvalue()


write()
code, said = call(merge.main, "g")
state = read()
check("hold on with no review: merge.py refuses REVIEW_HOLD and merges nothing", code == 5 and "(REVIEW_HOLD)" in said and not merged, said)
check("the goal stays done with review_wait set, not failed", state["status"] == "done" and state.get("review_wait") is True, str(state))
check("the board's Issues says merge waiting on review", any("merge waiting on review" in line for line in board_lines.issues(repo, [state])), "", "board")
code, said = call(review.main, "record", "g", role="worker")
check("a worker cannot record a review: refused, nothing written", code not in (0, None) and "REVIEW_ROLE" in said and "review" not in read(), said, "worker")
code, said = call(review.main, "record", "g")
state = read()
check("the operation role records the review of the current head", code == 0 and state["review"]["head"] == head and not state.get("review_wait"), said, "merge")
code, said = call(merge.main, "g")
check("with the review recorded merge.py merges", code in (0, None) and "MERGED https://example.test/pull/1" in said and merged, said[-300:], "merge")
tip[0], merged[:] = "b" * 40, []
write(review={"head": head}, pr_head="b" * 40)
code, said = call(merge.main, "g")
check("a push after the record voids it: the hold applies again", code == 5 and "(REVIEW_HOLD)" in said and not merged, said[-300:])
tip[0] = head
write()
code, said = call(merge.main, "g", hold=False)
check("with the setting off merging is unchanged", code in (0, None) and merged and "REVIEW_HOLD" not in said, said[-300:], "merge")
sys.exit(1 if fails else 0)
