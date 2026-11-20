#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-delivery/scripts/goal.py skills/workflow-delivery/scripts/fit.py skills/workflow-monitoring/scripts/sessions.py
"""new-binds (#4257): goal.py new, run inside a Claude app worker session (CLAUDE_CODE_HOST_SESSION_ID set), binds the new goal
to that session like `sessions.py bind SLUG self` and says BOUND; outside an app session it changes nothing.
usage: test-new-binds.py [in|out]"""
import json
import os
import re
import shutil
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
    env.update(HOME=repo, USERPROFILE=repo, LOOP_FLOW=os.path.join(repo, "flow.json"), LOOP_ROLE="worker", GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
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
if only in ("", "operation"):  # #5616: the governing session is never a worker, whatever id it goes by, and the pool never counts it as free
    repo, scripts = fresh(), os.path.join(root, "skills", "workflow-monitoring", "scripts")
    loop = os.path.join(repo, ".git", "loop")
    os.makedirs(loop, exist_ok=True)
    json.dump({"local_app-toy": {"state": "free", "name": "operation"}, "w1": {"state": "free", "name": "w1"}}, open(os.path.join(loop, "session-pool.json"), "w"))
    env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "LOOP_POD", "LOOP_ROLE"))}
    env.update(HOME=repo, USERPROFILE=repo)

    def tool(*args, **more):
        done = subprocess.run([sys.executable] + list(args), cwd=repo, capture_output=True, text=True, env=dict(env, **more))
        return done.returncode, done.stdout + done.stderr

    check("negative control: before it claims, the pool counts both sessions free", "2 free" in tool(os.path.join(scripts, "pool.py"), "status", LOOP_ROLE="worker")[1])
    code, said = tool(os.path.join(scripts, "operate.py"), "claim", CLAUDE_CODE_SESSION_ID="cli-toy", CLAUDE_CODE_HOST_SESSION_ID="local_app-toy")
    ids = open(os.path.join(loop, "operation.id")).read().split()
    check("operate.py claim registers both ids of the operation session, its CLI id and its app id (they differ)", code == 0 and {"cli-toy", "local_app-toy"} <= set(ids))
    check("the app id is not counted as free", "1 free" in tool(os.path.join(scripts, "pool.py"), "status", LOOP_ROLE="worker")[1])
    code, said = tool(os.path.join(scripts, "sessions.py"), "bind", "g", "local_app-toy", LOOP_ROLE="worker")
    check("bind refuses the operation session's app id", code != 0 and "never a worker" in said and "local_app-toy" in said)
    code, said = tool(os.path.join(scripts, "sessions.py"), "bind", "g", "w1", LOOP_ROLE="worker")
    check("and still binds an ordinary session", code == 0 and "w1" in said)
if only in ("", "trust"):  # TD509: a folder with no trust entry in ~/.claude.json is refused, and the file is never written
    repo, scripts = fresh(), os.path.join(root, "skills", "workflow-monitoring", "scripts")
    loop, tree = os.path.join(repo, ".git", "loop"), os.path.join(repo, "tree")
    os.makedirs(os.path.join(loop, "runs"), exist_ok=True)
    os.makedirs(tree)
    json.dump({"slug": "g", "status": "queued", "worktree": tree}, open(os.path.join(loop, "runs", "g.json"), "w"))
    json.dump({"w1": {"state": "free", "name": "w1"}}, open(os.path.join(loop, "session-pool.json"), "w"))
    claude = os.path.join(repo, ".claude.json")
    env = dict(os.environ, LOOP_ROLE="worker", HOME=repo)

    def bind():
        done = subprocess.run([sys.executable, os.path.join(scripts, "sessions.py"), "bind", "g", "w1"], cwd=tree, capture_output=True, text=True, env=env)
        return done.returncode, done.stdout + done.stderr

    code, said = bind()
    check("negative control: with no ~/.claude.json nothing is known, so bind goes through", code == 0 and "w1" in said)
    json.dump({"projects": {os.path.join(repo, "elsewhere"): {"hasTrustDialogAccepted": True}}}, open(claude, "w"))
    before = open(claude).read()
    json.dump({"slug": "g", "status": "queued", "worktree": tree}, open(os.path.join(loop, "runs", "g.json"), "w"))
    json.dump({"w1": {"state": "free", "name": "w1"}}, open(os.path.join(loop, "session-pool.json"), "w"))
    code, said = bind()
    check("a worktree with no trust entry is refused: ask the owner to trust it", code != 0 and "ask the owner to trust" in said and tree in said)
    check("and ~/.claude.json is read only: it is byte for byte as it was", open(claude).read() == before)
    done = subprocess.run([sys.executable, os.path.join(scripts, "sessions.py"), "assign", "g", "--text", "go"], cwd=tree, capture_output=True, text=True, env=env)
    check("assign refuses the same untrusted worktree", done.returncode != 0 and "ask the owner to trust" in done.stdout + done.stderr)
    json.dump({"projects": {repo: {"hasTrustDialogAccepted": True}}}, open(claude, "w"))
    code, said = bind()
    check("a trusted parent folder lets it through", code == 0 and "w1" in said)
if only in ("", "restart"):  # TD509: selfcheck names untrusted worktrees of bound sessions and worktree entries whose folder is gone
    repo, scripts = fresh(), os.path.join(root, "skills", "workflow-monitoring", "scripts")
    loop, tree = os.path.join(repo, ".git", "loop"), os.path.join(repo, "tree")
    os.makedirs(os.path.join(loop, "runs"), exist_ok=True)
    os.makedirs(tree)
    json.dump({"slug": "g", "status": "running", "session": {"id": "w1"}, "worktree": tree}, open(os.path.join(loop, "runs", "g.json"), "w"))
    claude = os.path.join(repo, ".claude.json")
    env = dict(os.environ, LOOP_ROLE="worker", HOME=repo, USERPROFILE=repo)

    def selfcheck():
        done = subprocess.run([sys.executable, os.path.join(scripts, "unattended.py"), "selfcheck"], cwd=repo, capture_output=True, text=True, env=env)
        return done.stdout

    check("negative control: with no ~/.claude.json no folder is called untrusted", "folder trust" not in selfcheck())
    json.dump({"projects": {os.path.join(repo, "elsewhere"): {"hasTrustDialogAccepted": True}}}, open(claude, "w"))
    check("a bound session whose worktree has no trust entry is MISSING folder trust, with its slug", "MISSING folder trust: g" in selfcheck())
    json.dump({"projects": {repo: {"hasTrustDialogAccepted": True}}}, open(claude, "w"))
    check("a trusted parent clears it", "folder trust" not in selfcheck())
    check("negative control: with every folder present no worktree is called gone", "MISSING worktrees" not in selfcheck())
    gone = os.path.join(repo, "gone")
    subprocess.run(["git", "-C", repo, "worktree", "add", "-q", "--detach", gone], check=True)
    shutil.rmtree(gone)
    check("a worktree entry whose folder is gone is MISSING worktrees, with the fix", "MISSING worktrees: 1 entries whose folder is gone. Fix: git worktree prune" in selfcheck())
if only in ("", "scratch"):  # TD509: scratch lives under ~/.workflow-loop/scratch, and no loop script hard-codes /tmp
    home = tempfile.mkdtemp(prefix="scratch-home-")
    done = subprocess.run([sys.executable, os.path.join(root, "skills", "workflow-monitoring", "scripts", "operate.py"), "scratch", "../my goal"], capture_output=True, text=True,
                          env=dict(os.environ, HOME=home, USERPROFILE=home, LOOP_ROLE="worker"))
    path = done.stdout.strip()
    check("operate.py scratch GOAL makes and prints a folder under ~/.workflow-loop/scratch, whatever the goal text", os.path.isdir(path) and os.path.realpath(path).startswith(os.path.realpath(os.path.join(home, ".workflow-loop", "scratch")) + os.sep))
    hard = re.compile(r"""["'](?:/private)?/tmp[/"']""")
    found = [os.path.join(d, f) for d, _, fs in os.walk(os.path.join(root, "skills")) for f in fs if f.endswith((".py", ".sh")) and hard.search(open(os.path.join(d, f), errors="replace").read())]
    check("no loop script hard-codes /tmp (%s)" % ", ".join(found), not found)
    check("negative control: a script that does is found", bool(hard.search('open("/tmp/x.log")')))
print("PASS: goal.py new binds an app session's goal" if not fails else "FAILED %d" % fails)
sys.exit(1 if fails else 0)
