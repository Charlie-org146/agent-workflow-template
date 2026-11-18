#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-delivery/scripts/routing.py skills/workflow-delivery/scripts/goal.py skills/workflow-delivery/scripts/guards.py
"""agent-routing (DEL-16): the config picks each step's agent. Build runs through the routed command (a fake Codex that
prints Codex's JSONL events), review stays on the heavy profile, the run record names both agents with token counts,
Codex missing from the machine falls back to Claude with one warning line, and a new profile needs no code change."""
import json
import os
import subprocess
import sys
import tempfile
import time

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SCRIPTS = os.path.join(root, "skills", "workflow-delivery", "scripts")
ROUTING = os.path.join(SCRIPTS, "routing.py")
failed = []
FAKE = r'''import json, sys
sys.stdin.read()
open("built.txt", "w").write("built by %s\n" % sys.argv[1])
print(json.dumps({"type": "item.completed", "item": {"type": "agent_message", "text": "done\nSTEP: done"}}))
print(json.dumps({"type": "turn.completed", "usage": {"input_tokens": 1000, "cached_input_tokens": 400, "cache_write_input_tokens": 0, "output_tokens": 50}}))
'''


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


with tempfile.TemporaryDirectory() as base:
    repo = os.path.join(base, "repo")
    os.makedirs(repo)
    git = lambda *a: subprocess.run(["git", "-c", "user.name=Toy", "-c", "user.email=t@example.test", "-c", "core.autocrlf=false"]
                                    + list(a), cwd=repo, capture_output=True, text=True)
    git("init", "-q", "-b", "main")
    with open(os.path.join(repo, "a.txt"), "w") as handle:
        handle.write("a\n")
    git("add", "-A")
    git("commit", "-qm", "init")
    fake = os.path.join(base, "fake-agent.py")
    with open(fake, "w", newline="\n") as handle:
        handle.write(FAKE)
    runs = os.path.join(repo, ".git", "loop", "runs")
    os.makedirs(runs)
    agents_file = os.path.join(base, "agents.json")
    env = dict(os.environ, LOOP_ROLE="worker", LOOP_AGENTS=agents_file, PYTHONUTF8="1")

    def conf(profiles, routes):
        with open(agents_file, "w") as handle:
            json.dump({"profiles": profiles, "routes": routes}, handle)

    def goal(slug, small):
        with open(os.path.join(runs, slug + ".json"), "w") as handle:
            json.dump({"slug": slug, "size": {"small": small}, "worker": "session"}, handle)

    def run(*args):
        return subprocess.run([sys.executable, "-B", ROUTING] + list(args), cwd=repo, capture_output=True, text=True, env=env)

    def record(slug):
        with open(os.path.join(runs, slug + ".json")) as handle:
            return json.load(handle)

    codex = {"agent": "codex", "command": [sys.executable, fake, "codex"], "login": None}

    # Done line: build routed to Codex, review on Claude, both named with tokens.
    conf({"cheap": codex}, {"steps": {"build": "cheap"}})
    goal("g1", True)
    done = run("build", "g1")
    state = record("g1")
    built = os.path.exists(os.path.join(repo, "built.txt")) and "built by codex" in open(os.path.join(repo, "built.txt")).read()
    check(done.returncode == 0 and built, "a build routed to cheap runs through the Codex command: " + done.stdout[-200:] + done.stderr[-200:])
    check(git("log", "-1", "--format=%s").stdout.strip() == "Build via codex: g1", "the Codex build is committed by delivery")
    check(state["agents"]["build"]["agent"] == "codex" and state["agents"]["build"]["tokens"] == 650,
          "the run record names codex for build with its tokens (input minus cached, plus output)")
    check(state["tokens"]["build"] == 650, "the step's tokens also land in the budget's tokens")
    sys.path.insert(0, SCRIPTS)
    import routing  # noqa: E402
    os.environ["LOOP_AGENTS"] = agents_file
    routing.add_tokens(state, "review", "4000")
    check(state["agents"]["review"]["agent"] == "claude" and state["agents"]["review"]["tokens"] == 4000,
          "the record names claude for review with its tokens")
    check({state["agents"]["build"]["agent"], state["agents"]["review"]["agent"]} == {"codex", "claude"}, "one record names both agents")

    # Review stays heavy unless the config routes it by name.
    conf({"cheap": codex}, {"sizes": {"small": "cheap", "large": "cheap"}})
    check(run("resolve", "review", "--size", "small").stdout.startswith("ROUTE review: heavy"), "a size route never moves review off heavy")
    check(run("resolve", "build", "--size", "small").stdout.startswith("ROUTE build: cheap"), "a size route moves a small goal's build to cheap")
    conf({"cheap": codex}, {"steps": {"review": "cheap"}})
    check(run("resolve", "review").stdout.startswith("ROUTE review: cheap"), "review moves only when the config routes it by name")

    # Size routes: a small goal builds on cheap, a large one on heavy.
    conf({"cheap": codex}, {"sizes": {"small": "cheap"}})
    check(run("resolve", "build", "--size", "large").stdout.startswith("ROUTE build: heavy"), "a large goal's build stays on heavy")

    # Codex removed from the machine: build falls back to Claude with one warning line.
    conf({"cheap": dict(codex, command=["no-such-agent-on-this-machine", "exec"])}, {"steps": {"build": "cheap"}})
    goal("g2", True)
    done = run("build", "g2")
    warns = [line for line in done.stdout.splitlines() if line.startswith("AGENT_FALLBACK")]
    state = record("g2")
    check(done.returncode == 0 and len(warns) == 1 and "using claude" in warns[0], "a missing agent warns once and uses claude: " + done.stdout[-200:] + done.stderr[-200:])
    check("BUILD g2: build it yourself" in done.stdout, "the fallback build is left to the worker session")
    check(state["agents"]["build"]["agent"] == "claude" and "isn't installed" in state["agents"]["build"]["fallback"],
          "the record names claude for the fallback build and the reason")

    # A new agent is one profile entry: no code change.
    conf({"local": {"agent": "open-model", "model": "m1", "command": [sys.executable, fake, "open-model"], "output": "codex-jsonl",
                    "prompt": "stdin"}}, {"steps": {"build": "local"}})
    goal("g3", False)
    done = run("build", "g3")
    state = record("g3")
    check(done.returncode == 0 and state["agents"]["build"]["agent"] == "open-model" and state["agents"]["build"]["model"] == "m1",
          "a profile added to the file routes a step with no code change: " + done.stdout[-200:] + done.stderr[-200:])

    # An agent that changes no file (a sandbox that blocks writes) is a failed build, recorded, and the worker builds it itself.
    conf({"local": {"agent": "open-model", "command": [sys.executable, "-c", "import sys; sys.stdin.read()"], "output": "codex-jsonl",
                    "prompt": "stdin"}}, {"steps": {"build": "local"}})
    goal("g4", False)
    done = run("build", "g4")
    check(done.returncode == 1 and "changed no file" in done.stdout, "a routed build that changes no file fails and says so: " + done.stdout[-200:])

    # A sandbox that can't write: Codex edits files under its sandbox and delivery commits; with no write sandbox the build
    # falls back to Claude with one line, never to full access.
    wall = r"import sys; sys.stdin.read(); sys.stderr.write('ERROR patch rejected: writing is blocked by read-only sandbox')"
    conf({"local": {"agent": "open-model", "command": [sys.executable, "-c", wall], "output": "codex-jsonl", "prompt": "stdin"}},
         {"steps": {"build": "local"}})
    goal("g5", False)
    done = run("build", "g5")
    warns = [line for line in done.stdout.splitlines() if line.startswith("AGENT_FALLBACK")]
    check(done.returncode == 0 and len(warns) == 1 and "sandbox is read-only" in warns[0] and "using claude" in warns[0],
          "a write-blocked agent falls back to claude with one line: " + done.stdout[-250:])
    check("sandbox is read-only" in record("g5")["agents"]["build"]["fallback"], "the record carries the write-blocked reason")

    # Detect reports each agent and --write keeps the file private and valid.
    conf({}, {})
    os.remove(agents_file)
    done = run("detect", "--write")
    written = json.load(open(agents_file)) if os.path.exists(agents_file) else {}
    check(done.stdout.count("AGENT ") == 2 and "profiles" in written and "routes" in written, "detect names each agent and writes the profiles: " + done.stdout[-300:])

# A routed agent that passes its timeout loses its whole tree: the agent and the child it started are both gone (net row routing-timeout-tree).
TREE = r'''import os, subprocess, sys, time
kid = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
open(sys.argv[1], "w").write("%d %d" % (os.getpid(), kid.pid))
time.sleep(30)
'''
sys.path.insert(0, SCRIPTS)
import proctree  # noqa: E402
import routing  # noqa: E402


def gone(pid, wait=10):
    end = time.time() + wait
    while time.time() < end:
        if not proctree.alive_since(pid):  # a zombie counts as gone
            return True
        time.sleep(0.2)
    return False


def pids(path):
    end = time.time() + 10
    while time.time() < end and not (os.path.exists(path) and open(path).read().count(" ")):
        time.sleep(0.1)
    return [int(n) for n in open(path).read().split()]


with tempfile.TemporaryDirectory() as base:
    agent = os.path.join(base, "tree-agent.py")
    with open(agent, "w", newline="\n") as handle:
        handle.write(TREE)
    prof = {"command": [sys.executable, agent, os.path.join(base, "tree.pids")], "prompt": "arg", "limit": 3}
    began = time.time()
    _, code, err = routing.ask(prof, "go")
    took = time.time() - began
    held = pids(os.path.join(base, "tree.pids"))
    check(code == 1 and "timed out" in err and len(held) == 2 and took < 15,  # a stop that waits on the child's pipe takes the child's 30 s
          "a routed agent past its timeout fails at once: %s %s %.0fs" % (code, err[-60:], took))
    check(all(gone(pid) for pid in held), "the timed-out agent and the child it started are both gone: %s" % held)
    # Negative control: the old subprocess.run(timeout) kills only the agent, so its child keeps running (here with no pipe to wait on, which Windows drains).
    try:
        subprocess.run(prof["command"] + ["go"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3)
    except subprocess.TimeoutExpired:
        pass
    old = pids(os.path.join(base, "tree.pids"))
    left = not gone(old[1], 2)
    check(left, "negative control: subprocess.run(timeout) leaves the agent's child running: %s" % old)
    for pid in old:
        os.kill(pid, 9) if os.name != "nt" else proctree.kill(pid)

print("FAILED: %d" % len(failed) if failed else "PASS: agent-routing")
sys.exit(1 if failed else 0)
