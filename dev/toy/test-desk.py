#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-setup/scripts/desk.py skills/workflow-setup/scripts/setup.py skills/workflow-monitoring/scripts/machines.py
"""phone-first (#4805): onboarding lists every desk-only step and runs each once; check says DESK OK only when nothing is left
at the desk and a phone-only start works; a goal no app session can take starts as a background worker through agent_command."""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", ".."))
SETUP = os.path.join(TOP, "skills", "workflow-setup", "scripts", "setup.py")
MON = os.path.join(TOP, "skills", "workflow-monitoring", "scripts")
FAILS = []


def check(ok, name):
    print(("PASS: " if ok else "FAIL: ") + name)
    if not ok:
        FAILS.append(name)


with tempfile.TemporaryDirectory() as tmp:
    tmp = os.path.realpath(tmp)
    repo, home = os.path.join(tmp, "repo"), os.path.join(tmp, "home")
    subprocess.run(["git", "init", "-q", "-b", "main", repo], check=True)
    os.makedirs(os.path.join(repo, ".loop"))
    os.makedirs(home)
    os.makedirs(os.path.join(tmp, ".codex"))
    open(os.path.join(tmp, ".codex", "auth.json"), "w").close()  # the Codex login (its file only; never read)

    def config(**fields):
        with open(os.path.join(repo, ".loop", "config.json"), "w") as f:
            json.dump(dict(base="main", **fields), f)

    def desk(*args):
        env = dict(os.environ, LOOP_DESK_HOME=home, HOME=tmp, USERPROFILE=tmp, PATH=os.environ["PATH"])
        done = subprocess.run([sys.executable, SETUP, "desk"] + list(args) + (["--repo", repo] if args[0] != "done" else []), env=env, capture_output=True, text=True)
        return done.returncode, done.stdout + done.stderr

    config(workers="app", agent_command=[sys.executable, "-c", "pass"])
    code, out = desk("list")
    ids = ("trust-folders", "permission-modes", "tool-preapprovals", "private-names", "mail-env", "codex-login")
    check(code == 0 and all("DESK %s [" % i in out for i in ids), "onboarding lists every desk-only step")
    code, out = desk("run")
    check(out.count("Do: ") == 5 and "5 step(s) open" in out, "run prints each open desk step once, with how to do it")
    code, out = desk("run")
    check("Do: " not in out and "still open" in out, "a step already listed is not printed again with its instructions")
    code, out = desk("check")
    check(code == 1 and "GAP trust-folders" in out and "GAP phone-start: workers is app" in out, "check reports each gap, and an app-only worker rule")
    config(agent_command=[sys.executable, "-c", "pass"])
    with open(os.path.join(home, "private-names"), "w"):
        pass
    with open(os.path.join(home, "mail.env"), "w"):
        pass
    code, out = desk("done", "trust-folders", "permission-modes", "tool-preapprovals")
    check(code == 0 and "RECORDED" in out, "the owner records the desk steps done")
    code, out = desk("done", "no-such-step")
    check(code == 2, "an unknown step records nothing")
    code, out = desk("check")
    check(code == 0 and "DESK OK: nothing left to do at the desk" in out, "check ends clean when nothing is left and a phone-only start works")
    config()
    code, out = desk("check")
    check(code == 1 and "agent_command is missing" in out, "no agent_command means a phone-only start fails the check")

    # a goal no app session can take starts as a background worker through agent_command
    sys.path.insert(0, MON)
    config(agent_command=[sys.executable, "-c", "pass"])
    os.environ.update(LOOP_MACHINE_NAME="mac")
    for name in ("LOOP_ROLE", "LOOP_SESSION_TOOL"):
        os.environ.pop(name, None)
    git = lambda *a: subprocess.run(["git"] + list(a), cwd=repo, capture_output=True, text=True)
    git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "i")
    os.makedirs(os.path.join(repo, ".git", "loop", "logs"), exist_ok=True)
    os.makedirs(os.path.join(repo, ".git", "loop", "runs"), exist_ok=True)
    os.chdir(repo)
    import machines
    state = {"slug": "g1", "worktree": repo, "log": []}
    how = machines.start_worker(state, "go", {"agent_command": [sys.executable, "-c", "pass"]})
    check(how == "background" and state.get("status") == "running" and state.get("pid"), "with no app session a background worker starts through agent_command")
    state = {"slug": "g2", "worktree": repo, "log": []}
    how = machines.start_worker(state, "go", {"workers": "app", "agent_command": [sys.executable, "-c", "pass"]})
    check(how == "app" and not state.get("pid"), "workers app keeps the owner's rule: no background process, the goal waits for a bind")

if FAILS:
    print("FAILED %d" % len(FAILS))
    sys.exit(1)
print("OK")
