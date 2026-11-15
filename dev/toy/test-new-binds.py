#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-delivery/scripts/goal.py skills/workflow-delivery/scripts/fit.py skills/workflow-monitoring/scripts/sessions.py
"""new-binds (#4257): goal.py new, run inside a Claude app worker session (CLAUDE_CODE_HOST_SESSION_ID set), binds the new goal
to that session like `sessions.py bind SLUG self` and says BOUND; outside an app session it changes nothing.
usage: test-new-binds.py [in|out]"""
import json
import os
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
goal = os.path.join(root, "skills", "workflow-delivery", "scripts", "goal.py")
only = sys.argv[1] if len(sys.argv) > 1 else ""
fails = 0


def check(name, ok):
    global fails
    print(("PASS: " if ok else "FAIL: ") + name)
    fails += 0 if ok else 1


def fresh():
    repo = tempfile.mkdtemp(prefix="new-binds-")
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run(git + ["init", "-q", "-b", "main", repo], check=True)
    os.makedirs(os.path.join(repo, ".loop"))
    with open(os.path.join(repo, ".loop", "config.json"), "w") as handle:
        json.dump({"base": "main", "workers": "app"}, handle)
    with open(os.path.join(repo, "flow.json"), "w") as handle:
        json.dump({"steps": dict.fromkeys(("idea", "plan", "build", "review", "qa", "ship"), "built-in")}, handle)
    subprocess.run(git + ["add", "-A"], cwd=repo, check=True)
    subprocess.run(git + ["commit", "-q", "-m", "base"], cwd=repo, check=True)
    return repo


def freeze(repo, session):
    env = {k: v for k, v in os.environ.items() if k != "CLAUDE_CODE_HOST_SESSION_ID"}
    env.update(LOOP_FLOW=os.path.join(repo, "flow.json"), LOOP_ROLE="worker", GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    if session:
        env["CLAUDE_CODE_HOST_SESSION_ID"] = session
    done = subprocess.run([sys.executable, goal, "new", "g", "--here", "--goal", "x", "--done", "one"], cwd=repo, capture_output=True, text=True, env=env)
    path = os.path.join(repo, ".git", "loop", "runs", "g.json")
    state = json.load(open(path)) if os.path.exists(path) else {}
    return done.stdout + done.stderr, state


if only in ("", "in"):
    said, state = freeze(fresh(), "local_toy-session")
    print(said)
    check("inside an app session the new goal is bound to it and says BOUND", (state.get("session") or {}).get("id") == "local_toy-session" and state.get("worker") == "session" and "BOUND g" in said)
if only in ("", "out"):
    said, state = freeze(fresh(), "")
    check("outside an app session nothing is bound and nothing is said about it", state.get("slug") == "g" and not state.get("session") and "BOUND" not in said)
print("PASS: goal.py new binds an app session's goal" if not fails else "FAILED %d" % fails)
sys.exit(1 if fails else 0)
