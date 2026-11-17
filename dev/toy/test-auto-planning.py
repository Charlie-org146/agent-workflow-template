#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-monitoring/scripts/monitor.py skills/workflow-monitoring/scripts/notify.py skills/workflow-delivery/scripts/routing.py
"""auto-planning (MON-10, #4779): `monitor.py plan` gives every release-less goal a release, estimate, hard ETA, token budget,
machine and agent with a reason and starts nothing; `plan approve` writes it into the queue only with the owner's words; goals
already started are left out; `plan --check` has a second agent's notes, with a Claude fallback."""
import json
import os
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
MONITOR = os.path.join(root, "skills", "workflow-monitoring", "scripts", "monitor.py")
failed = []
WANT = sys.argv[1] if len(sys.argv) > 1 else ""  # one done line (1 to 5) or all
want = lambda *n: not WANT or WANT in n
QUEUE = """# Queue
- slug: win-fix | touches: skills/workflow-delivery/scripts | goal: Make lanes work on native Windows | done: it runs
- slug: mac-judge | touches: docs/wiki | goal: Run the judge on the Mac | done: it runs
- slug: tiny | touches: README.md | goal: Fix the title | done: the title reads right
- slug: big | depends-on: tiny | touches: skills/workflow-delivery/scripts,skills/workflow-monitoring/scripts,docs/wiki | goal: A large change | done: a | done: b | done: c | done: d
- slug: claim | touches: README.md | goal: Shares a prefix with a claimed goal | done: x
- slug: begun | touches: README.md | goal: Already has a run | done: x
- slug: claimed | touches: README.md | goal: Already on a machine | done: x | machine: mac
- slug: peered | touches: README.md | goal: In the peer's plan | done: x
- slug: dated | release: v3.0 | touches: README.md | goal: Has a release | done: x
"""


NOW = "1"


def check(ok, text):
    if WANT and WANT != NOW:
        return
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


with tempfile.TemporaryDirectory() as base:
    repo = os.path.join(base, "repo")
    os.makedirs(os.path.join(repo, ".loop"))
    git = lambda *a: subprocess.run(["git", "-c", "user.name=Toy", "-c", "user.email=t@example.test", "-c", "core.autocrlf=false"] + list(a),
                                    cwd=repo, capture_output=True, text=True)
    files = {"VERSION": "1.0.52\n", "README.md": "t\n", ".loop/queue.md": QUEUE,
             ".loop/config.json": json.dumps({"base": "main", "token_budget": 3000000, "time_budget_minutes": 240})}
    for name, text in files.items():
        with open(os.path.join(repo, name), "w", newline="\n") as handle:
            handle.write(text)
    git("init", "-q", "-b", "main")
    git("add", "-A")
    git("commit", "-qm", "init")
    loop = os.path.join(repo, ".git", "loop")
    os.makedirs(os.path.join(loop, "runs"))
    with open(os.path.join(loop, "runs", "begun.json"), "w") as handle:
        json.dump({"slug": "begun", "status": "running"}, handle)
    peer = os.path.join(base, "peer.json")
    with open(peer, "w") as handle:
        json.dump({"goals": {"peered": {"machine": "mac"}}}, handle)
    agent = os.path.join(base, "agent.py")
    with open(agent, "w", newline="\n") as handle:
        handle.write("import sys\nprint({'walled': 'read-only sandbox'}.get(sys.argv[1], 'notes from ' + sys.argv[1]))\n")
    agents = os.path.join(base, "agents.json")

    def routes(second, steps):
        profiles = {"heavy": {"agent": "claude", "command": [sys.executable, agent, "heavy"], "prompt": "arg"},
                    "cheap": {"agent": "cheapagent", "command": [sys.executable, agent, "cheap"], "login": [], "prompt": "arg"},
                    "second": {"agent": "second", "command": second, "login": [], "prompt": "arg"}}
        with open(agents, "w") as handle:
            json.dump({"profiles": profiles, "routes": {"steps": steps, "sizes": {"small": "cheap"}, "fallback": "heavy"}}, handle)

    env = dict(os.environ, LOOP_AGENTS=agents, PYTHONUTF8="1")

    def run(*args):
        done = subprocess.run([sys.executable, MONITOR] + list(args), cwd=repo, capture_output=True, text=True, env=env, encoding="utf-8", errors="replace")
        return done.returncode, done.stdout + done.stderr

    def queue():
        with open(os.path.join(repo, ".loop", "queue.md"), newline="") as handle:
            return handle.read()

    def line(out, slug):
        return next((x for x in out.splitlines() if " %s |" % slug in x), "")

    routes([sys.executable, agent, "second"], {})
    code, out = run("plan", "--machines", "pc=6,mac=7", "--peer-plan", peer, "--first-release", "v2.0") if want("1", "2", "3", "4") else (0, "")
    if want("1", "3", "4"):
        rows = {slug: line(out, slug).split(" | ") for slug in ("win-fix", "mac-judge", "tiny", "big")}
        NOW = '1'
        check(code == 0 and all(len(r) == 7 for r in rows.values()), "plan prints a row per release-less goal")
        check(all(x.startswith("v2.") and "est " in r[1] and "ETA " in r[2] and r[3].endswith("k tokens") and r[6] for r in rows.values() for x in [r[0]]),
              "each row has a release, an estimate, a hard ETA, a token budget and a reason")
        check(not [n for n in os.listdir(os.path.join(loop, "runs")) if n != "begun.json"] and queue() == QUEUE,
              "plan starts nothing: no run record and no queue line changed")
        NOW = '3'
        check(rows["win-fix"][4] == "pc" and rows["mac-judge"][4] == "mac", "the Windows-only goal lands on the PC and the Mac-lane goal on the Mac")
        check(rows["tiny"][4] == "mac" and rows["big"][4] == "pc", "the rest go to the machine with the most memory left after the goals already given to it")
        check(rows["tiny"][5] == "cheap" and rows["big"][5] == "heavy", "a small goal takes the cheap profile and a large one the heavy profile")
        NOW = '4'
        check(
              all("LEFT OUT %s: already started" % slug in out for slug in ("begun", "claimed", "peered")) and " claim |" in out and "LEFT OUT claim:" not in out and "dated" not in out.split("LEFT OUT")[0],
              "goals with a run, a machine field or a place in the peer's plan are left out as already started")
        check(out.strip().splitlines()[-1].startswith("SEND to the other operation session:") and "ETA choices" in out,
              "the plan ends with the message for the other machine's operation session and leaves ETA choices to the owner")

    NOW = '2'
    if want('2'):
        code, out = run("plan", "approve", "--owner-record", "o1")
        pending = lambda: json.load(open(os.path.join(loop, "plan-round.json")))["status"]
        check(code != 0 and "REFUSED" in out and queue() == QUEUE and pending() == "pending", "approve with no owner-words record refuses and changes nothing")
        with open(os.path.join(loop, "owner-words.tsv"), "w", newline="\n") as handle:
            handle.write('o1\t2026-11-17T00:00:00Z\toperation\t"approve"\tplan\n')
        code, out = run("plan", "approve", "--owner-record", "o1", "nosuch", "machine=pc")
        check(code != 0 and "REFUSED" in out and queue() == QUEUE and pending() == "pending", "approve with an unknown slug refuses and changes nothing")
        code, out = run("plan", "approve", "--owner-record", "o1", "big", "machine=mac", "agent=cheap", "release=v2.9")
        text = queue()
        got = next(x for x in text.splitlines() if x.startswith("- slug: big "))
        check(code == 0 and got.endswith("| release: v2.9 | machine: mac | agent: cheap") and "slug: win-fix " in text and "| machine: pc | agent: cheap" in text
              and "| release: v2.0 |" in text and "slug: dated | release: v3.0 |" in text and "begun" in text and pending() == "approved",
              "approve writes release, machine and agent into the queue lines, line edits over the plan")
        code, out = run("plan", "approve", "--owner-record", "o1")
        check(code != 0 and "no pending plan" in out, "approve with no pending plan refuses")
        code, out = run("plan", "--machines", "pc=6")
        check("PLAN" in out and "win-fix" not in out.split("LEFT OUT")[0], "a second round leaves the approved goals alone")

    NOW = '5'
    if want('5'):
        git("checkout", "-q", ".loop/queue.md")
        code, out = run("plan", "--check", "--machines", "pc=6,mac=7")
        check(code == 0 and "Cross-check:" in out and "NOTE: no second agent" in out and "AGENT_FALLBACK" not in out, "plan --check with no second agent routed says so and the plan still prints")
        routes([sys.executable, agent, "second"], {"plan": "second"})
        code, out = run("plan", "--check", "--machines", "pc=6,mac=7")
        check("Notes from second:" in out and "notes from second" in out and "AGENT_FALLBACK" not in out, "a plan route sends the cross-check to the second agent")
        routes([sys.executable, agent, "walled"], {"plan": "second"})
        code, out = run("plan", "--check", "--machines", "pc=6,mac=7")
        check(code == 0 and out.count("AGENT_FALLBACK") == 1 and "Notes from claude:" in out and "notes from heavy" in out and "PLAN round" in out,
              "a second agent that can't write falls back to Claude with one AGENT_FALLBACK line and the plan still prints")
        routes(["no-such-agent-xyz"], {"plan": "second"})
        code, out = run("plan", "--check", "--machines", "pc=6,mac=7")
        check(code == 0 and out.count("AGENT_FALLBACK") == 1 and "isn't installed" in out and "notes from heavy" in out,
              "a second agent that is not installed falls back to Claude with one AGENT_FALLBACK line")

print("PASS: auto-planning" if not failed else "FAIL: auto-planning (%d)" % len(failed))
sys.exit(1 if failed else 0)
