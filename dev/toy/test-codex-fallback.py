#!/usr/bin/env python3
# windows: skip
# reads: skills/workflow-monitoring/scripts/batch.py skills/workflow-monitoring/scripts/watch.py skills/workflow-monitoring/scripts/mend.py
# reads: skills/workflow-monitoring/scripts/live_board.py skills/workflow-monitoring/scripts/sessions.py
"""TD515 (MCH-1, SET-10): the worker fallback order is app session, then background Claude, then Codex.

With a stubbed codex (nothing real is run: Popen is replaced and records the command and env): a session start that cannot be
made falls back to Codex with exactly the profile's arguments and the board says background · codex; when Claude can start,
Codex is never used (negative control); with no profile Codex is never used; a usage limit in a failed goal's log hands the goal
to Codex; a profile with danger-full-access or the bypass flag is refused and nothing starts. The Codex worker is started the
same way as a Claude one (worker.py loop, LOOP_ROLE=worker), so the run record's gates apply: no merge by itself."""
import json
import os
import subprocess
import sys
import tempfile

here = os.path.dirname(os.path.abspath(__file__))
MON = os.path.normpath(os.path.join(here, "..", "..", "skills", "workflow-monitoring", "scripts"))
sys.path.insert(0, MON)
sys.argv[0] = os.path.join(MON, "watch.py")  # as when watch.py runs: worker.py is found beside it
import batch  # noqa: E402
import live_board  # noqa: E402
import mend  # noqa: E402
import sessions  # noqa: E402
import watch  # noqa: E402

failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


PROFILE = ["codex", "exec", "--sandbox", "workspace-write", "-c", "sandbox_workspace_write.network_access=true", "-C", "WORKTREE"]
calls = []


class Child:
    pid = 4242


REAL = subprocess.Popen


def popen(command, *a, **kw):
    if not kw.get("start_new_session"):  # git and gh calls are real; only the agent launch is stubbed
        return REAL(command, *a, **kw)
    calls.append((list(command), kw.get("env") or {}))
    return Child()


def run(fn, *a):
    """fn(*a) with Popen replaced; (calls made, exit message or None)."""
    calls.clear()
    real = subprocess.Popen
    subprocess.Popen = popen
    try:
        fn(*a)
        return list(calls), None
    except SystemExit as error:
        return list(calls), str(error)
    finally:
        subprocess.Popen = real


with tempfile.TemporaryDirectory() as tmp:
    repo = os.path.join(tmp, "repo")
    subprocess.run(["git", "init", "-q", "-b", "main", repo], check=True)
    os.chdir(repo)
    os.environ["PATH"] = os.path.join(here, "fakegh") + os.pathsep + os.environ["PATH"]
    tree = os.path.join(tmp, "tree")
    os.makedirs(tree)
    fresh = lambda: {"slug": "g1", "worktree": tree, "branch": "loop/g1", "log": [], "status": "queued"}
    WANT = [sys.executable, os.path.join(MON, "worker.py"), "loop", "g1", "--"] + [tree if a == "WORKTREE" else a for a in PROFILE] + ["the prompt"]

    # 1. a session start that cannot be made (no session tool, so no session can be reached): Codex, exactly the profile
    cfg = {"codex_profile": PROFILE}
    refused = sessions.assign(fresh(), "the prompt", cfg)
    state = fresh()
    made, said = run(watch.launch, state, "the prompt", cfg)
    check(refused is False, "no session can be reached: assign says so")
    check(len(made) == 1 and made[0][0] == WANT, "then Codex starts with exactly codex exec --sandbox workspace-write -c sandbox_workspace_write.network_access=true -C WORKTREE, the prompt last")
    check(made and made[0][1].get("LOOP_ROLE") == "worker" and made[0][0][2:4] == ["loop", "g1"], "the Codex worker is started as worker.py loop with LOOP_ROLE=worker, so its run record, private-name scan and merge gates are the Claude worker's")
    check(state.get("agent") == "codex" and state.get("worker") == "background", "the run record names the agent: codex, a background worker")
    check("background · codex" in live_board.worker_of(state), "the board shows background · codex")

    # 2. negative control: Claude can start, so Codex is never used, and the board does not say codex
    state = fresh()
    made, said = run(watch.launch, state, "the prompt", {"agent_command": [sys.executable, "-c", "pass"], "codex_profile": PROFILE})
    check(len(made) == 1 and "codex" not in made[0][0] and state.get("agent") == "claude", "negative control: when background Claude can start, Codex is never used")
    check("codex" not in live_board.worker_of(state), "negative control: the board does not say codex")
    state = fresh()
    made, said = run(watch.launch, state, "the prompt", {})
    check(made == [] and said and "no agent_command" in said, "negative control: with no Codex profile and no Claude command nothing starts (as before)")

    # 3. a usage limit in the log of a failed goal hands it to Codex without waiting for the reset
    os.makedirs(os.path.join(repo, ".loop"))
    with open(os.path.join(repo, ".loop", "config.json"), "w") as handle:
        handle.write("{}")
    loop = os.path.join(repo, ".git", "loop")
    os.makedirs(os.path.join(loop, "runs"), exist_ok=True)
    os.makedirs(os.path.join(loop, "logs"), exist_ok=True)
    limited = dict(fresh(), status="failed", pid=999999, updated="2026-01-01T00:00:00Z", agent="claude", worker="background")
    with open(os.path.join(loop, "runs", "g1.json"), "w") as handle:
        json.dump(limited, handle)
    with open(os.path.join(loop, "logs", "g1.log"), "w") as handle:
        handle.write("working\nClaude usage limit reached; try again later\n")
    mend.free_to_restart = lambda s: True
    mend.where = lambda d: ""
    calls.clear()
    made, said = run(mend.one_pass, {"resume_on_limit": True, "agent_command": [sys.executable, "-c", "pass"], "codex_profile": PROFILE}, None)
    check(len(made) == 1 and made[0][0][-9:-1] == [a if a != "WORKTREE" else tree for a in PROFILE], "a usage limit in the log: the goal restarts on Codex with the profile's arguments")
    check(json.load(open(os.path.join(loop, "runs", "g1.json"))).get("agent") == "codex", "and the run record says agent: codex")
    with open(os.path.join(loop, "runs", "g1.json"), "w") as handle:
        json.dump(limited, handle)
    made, said = run(mend.one_pass, {"resume_on_limit": True, "agent_command": [sys.executable, "-c", "pass"]}, None)
    check(made == [], "negative control: with no Codex profile a usage limit still waits for the reset, nothing starts now")

    # 4. the guard: a profile that opens the sandbox is refused and nothing starts
    for bad in (["codex", "exec", "--sandbox", "danger-full-access", "-C", "WORKTREE"], PROFILE + ["--dangerously-bypass-approvals-and-sandbox"], ["codex", "exec", "--sandbox=danger-full-access"]):
        state = fresh()
        made, said = run(watch.launch, state, "the prompt", {"codex_profile": bad, "agent_command": [sys.executable, "-c", "pass"]})
        check(made == [] and said and said.startswith("REFUSED") and "sandbox" in said, "the guard refuses %s and starts nothing" % " ".join(bad[2:5]))
    check(batch.codex_next({"codex_profile": PROFILE}, {}) is True and batch.codex_next({}, {}) is False, "the shipped shape passes the guard; no profile means no Codex")
    os.chdir(here)
if failed:
    sys.exit(1)
print("PASS: TD515: Codex is the last fallback, started with exactly the profile's arguments, and a sandbox-opening profile is refused")
