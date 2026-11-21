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


PROFILE = ["codex", "exec", "--sandbox", "workspace-write", "-c", "sandbox_workspace_write.network_access=true", "-c", "sandbox_workspace_write.writable_roots=GITROOTS", "-C", "WORKTREE"]
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
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "base"], check=True)
    tree = os.path.join(tmp, "tree")  # a linked worktree, as every goal's is
    subprocess.run(["git", "worktree", "add", "-q", "--detach", tree], check=True)
    GIT = os.path.realpath(os.path.join(repo, ".git"))
    ROOTS = json.dumps([GIT + "/objects", GIT + "/refs", GIT + "/logs", GIT + "/worktrees/tree"])
    fresh = lambda: {"slug": "g1", "worktree": tree, "branch": "loop/g1", "log": [], "status": "queued"}
    WANT = [sys.executable, os.path.join(MON, "worker.py"), "loop", "g1", "--"] + [tree if a == "WORKTREE" else a.replace("GITROOTS", ROOTS) for a in PROFILE] + ["the prompt"]

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
    check(len(made) == 1 and made[0][0][-11:-1] == [tree if a == "WORKTREE" else a.replace("GITROOTS", ROOTS) for a in PROFILE], "a usage limit in the log: the goal restarts on Codex with the profile's arguments")
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
    # 5. TD537 (owner o676): the writable roots are exactly objects/, refs/, logs/ and this worktree's own git folder, never hooks, config or info
    state = fresh()
    made, said = run(watch.launch, state, "the prompt", {"codex_profile": PROFILE})
    args = made[0][0] if made else []
    asked = [a for a in args if a.startswith("sandbox_workspace_write.writable_roots=")]
    roots = json.loads(asked[0].split("=", 1)[1]) if len(asked) == 1 else []
    check(roots == json.loads(ROOTS) and len(roots) == 4, "the Codex args carry exactly the four writable roots of this worktree (%s)" % roots)
    check(not any(os.path.basename(r) in ("hooks", "config", "info") or r == GIT for r in roots) and "GITROOTS" not in " ".join(args), "and none is hooks, config, info or the whole git folder")
    for name, bad, folder in (("hooks", [x.replace("GITROOTS", '["%s/hooks"]' % GIT) for x in PROFILE], tree), ("config", [x.replace("GITROOTS", '["%s/config"]' % GIT) for x in PROFILE], tree),
                              ("info", [x.replace("GITROOTS", '["%s/info"]' % GIT) for x in PROFILE], tree), ("its own roots", [x.replace("GITROOTS", '["/etc"]') for x in PROFILE], tree),
                              ("the bypass flag", PROFILE + ["--dangerously-bypass-approvals-and-sandbox"], tree), ("danger-full-access", ["codex", "exec", "--sandbox", "danger-full-access"], tree),
                              ("a worktree that is not linked", PROFILE, repo)):
        state = dict(fresh(), worktree=folder)
        made, said = run(watch.launch, state, "the prompt", {"codex_profile": bad})
        check(made == [] and said and said.startswith("REFUSED"), "negative control: a profile with %s is refused and nothing starts" % name)
    check(batch.codex_next({"codex_profile": PROFILE}, {}) is True and batch.codex_next({}, {}) is False, "the shipped shape passes the guard; no profile means no Codex")
    os.chdir(here)

# TD520: a Codex run that ends 0 outside the flow ends done, its steps recorded, when it committed, left a clean tree and passed the
# gates; any other end still fails. The real worker.py loop and routing.py finish run against a throwaway repo with an origin.
def loop_run(command, slug, names="", agent="codex"):
    with tempfile.TemporaryDirectory() as tmp:
        bare, work = os.path.join(tmp, "o.git"), os.path.join(tmp, "r")
        git = lambda *a, cwd=work: subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True)
        git("init", "-q", "--bare", "-b", "main", bare, cwd=tmp)
        git("clone", "-q", bare, work, cwd=tmp)
        for key, value in (("user.email", "t@t"), ("user.name", "t")):
            git("config", key, value)
        git("commit", "-q", "--allow-empty", "-m", "base")
        git("push", "-q", "origin", "HEAD:main")
        git("checkout", "-qb", "loop/" + slug)
        runs = os.path.join(work, ".git", "loop", "runs")
        os.makedirs(runs)
        os.makedirs(os.path.join(work, ".git", "loop", "logs"))
        json.dump({"slug": slug, "status": "running", "agent": agent, "worktree": work, "branch": "loop/" + slug, "log": [], "flow": {}}, open(os.path.join(runs, slug + ".json"), "w"))
        home = os.path.join(tmp, "home")
        os.makedirs(os.path.join(home, ".workflow-loop"))
        open(os.path.join(home, ".workflow-loop", "private-names"), "w").write(names)
        env = dict(os.environ, LOOP_ROLE="worker", HOME=home, USERPROFILE=home)
        env.pop("LOOP_PRIVATE_NAMES", None)
        subprocess.run([sys.executable, os.path.join(MON, "worker.py"), "loop", slug, "--", "sh", "-c", command], cwd=work, capture_output=True, text=True, env=env)
        return json.load(open(os.path.join(runs, slug + ".json")))


good = loop_run("echo work > f.txt; git add -A; git commit -qm work", "g2")
check(good.get("status") == "done" and sorted(good.get("flow") or {}) == ["idea", "plan", "qa", "review", "ship"] and not good.get("finding"), "a Codex run that commits, leaves a clean tree and passes the gates ends done with its flow steps recorded")
check((good.get("report") or {}).get("status") == "waiting", "and it reports its pull request waiting, never merged by itself")
claude = loop_run("echo work > f.txt; git add -A; git commit -qm work", "g4", agent="claude")
check(claude.get("status") == "failed" and not claude.get("flow"), "negative control: a Claude worker that ends 0 with a commit and a clean tree is not overridden: it still ends failed")
for name, command, names in (("no commit", "true", ""), ("a dirty tree", "echo w > f.txt; git add -A; git commit -qm w; echo more > g.txt", ""), ("an exit 1", "echo w > f.txt; git add -A; git commit -qm w; exit 1", ""),
                             ("a private name in the commit", "echo secretword > f.txt; git add -A; git commit -qm w", "secretword\n")):
    bad = loop_run(command, "g3", names)
    check(bad.get("status") == "failed" and not bad.get("flow"), "negative control: a run that ends with %s still ends failed, no steps recorded" % name)
if failed:
    sys.exit(1)
print("PASS: TD515: Codex is the last fallback, started with exactly the profile's arguments, and a sandbox-opening profile is refused")
