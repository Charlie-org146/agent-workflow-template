#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-monitoring/scripts/layers.py skills/workflow-monitoring/scripts/operate.py skills/workflow-monitoring/scripts/reply_hook.py skills/workflow-monitoring/scripts/sessions.py
"""MON-1, MON-2, MON-5, MON-11, MON-16 (three layers): top builds one board from every machine's STATUS and is the only
publisher, a machine prints one line, the relay rule, the budget and agent_command checks, and the reply hook's machine mode."""
import json
import os
import subprocess
import sys
import tempfile
import time

here = os.path.dirname(os.path.abspath(__file__))
scripts = os.path.join(here, "..", "..", "skills", "workflow-monitoring", "scripts")
sys.path.insert(0, scripts)
import layers  # noqa: E402

fails = 0


def check(ok, text):
    global fails
    print(("PASS: " if ok else "FAIL: ") + text)
    fails += 0 if ok else 1


now = 1_800_000_000.0
mac = {"machine": "mac", "at": now - 60, "main": {"tpl": "abc1234"}, "merges": [{"slug": "old", "pr": 7}], "idle": [{"session": "s1", "reason": "free in the pool, no ready goal"}],
       "workers": [{"slug": "a", "step": "build", "status": "running", "pr": 0}, {"slug": "b", "step": "pr", "status": "done", "pr": 41}],
       "parked": [{"slug": "c", "reason": "held at pr"}], "needs_owner": [{"slug": "a", "words": "raise the cap?", "recommend": "no"}]}
pc = {"machine": "pc", "at": now - 45 * 60, "main": {"tpl": "abc1234"}, "merges": [], "idle": [], "parked": [], "needs_owner": [],
      "workers": [{"slug": "d", "step": "qa", "status": "running", "pr": 0}]}
text = layers.board([mac, pc], now)
check("mac/a build running" in text and "pc/d qa running" in text, "the board lists both machines' running goals in one board")
check("mac/b #41" in text and "mac/old #7" in text and "mac tpl abc1234" in text and "pc tpl abc1234" in text, "it shows PR numbers, merges and main per repo for each machine")
check(text.index("Needs you") < text.index("Running") < text.index("PRs") < text.index("Merges") < text.index("Parked and idle") < text.index("Main"), "the sections are in top's board order")
check("raise the cap? -> recommended: no" in text and "mac/c parked: held at pr" in text and "mac/s1 idle: free in the pool" in text, "needs-owner carries words and a recommendation; parked and idle carry reasons")
check("STALE: pc STATUS is 45 minutes old (over 30)" in text and "STALE: mac" not in text, "a STATUS over 30 minutes old is called out, a fresh one is not")

with tempfile.TemporaryDirectory() as tmp:
    common = os.path.join(tmp, ".git")
    os.makedirs(os.path.join(common, "loop", "runs"))
    json.dump({"slug": "g", "status": "running", "step": "qa", "pr": "https://x/pull/12", "goal": "g"}, open(os.path.join(common, "loop", "runs", "g.json"), "w"))
    status, said = layers.send(common, {}, now=now)
    check(said == "sent" and status["workers"] == [{"slug": "g", "step": "qa", "status": "running", "pr": 12}], "a machine sends STATUS with the goal's PR number")
    check(layers.send(common, {}, now=now + 60)[1] == "no change" and layers.send(common, {}, now=now + 31 * 60)[1] == "sent", "STATUS goes on change and every 30 minutes, not between")
    line = layers.one_line(status, "no change", now)
    check("\n" not in line and "STATUS no change" in line and "\n" not in layers.one_line(status, "sent", now), "a machine prints one line, not the board")
    check(not os.path.exists(os.path.join(common, "loop", "top-board.txt")), "a machine publishes no board")
    check([m["machine"] for m in layers.collect(common)] == [status["machine"]], "top reads each machine's latest STATUS")
    layers.publish_board(common, {}, now)
    check(os.path.exists(os.path.join(common, "loop", "top-board.txt")), "top publishes the one board")
    rows = dict(layers.defaults(common, {"agent_command": ["claude", "-p", "--allowedTools", "Bash,Read"], "time_budget_minutes": 240, "token_budget": 100}))
    check(rows["agent_command is one --allowedTools=<list> token"].startswith("FIX: ") and layers.check_allowed({"agent_command": ["claude", "--allowedTools=Bash,Read"]}) == "ok", "the two-token --allowedTools form is reported, one token is ok")
    json.dump({"slug": "h", "budget": {"minutes": 999, "tokens": 5}}, open(os.path.join(common, "loop", "runs", "h.json"), "w"))
    check(layers.check_budgets(common, {"time_budget_minutes": 240, "token_budget": 100}).startswith("FIX: h "), "a budget above the owner's cap is reported; caps stay the owner's")
    check(all(v == "ok" for k, v in dict(layers.defaults(common, {})).items() if "budgets" not in k and "allowed" not in k), "the other defaults hold")

check(layers.relay("top", "approve the plan")[0], "OWNER-WORDS relayed from top count as owner words")
check(not layers.relay("top", "delete the old branches")[0] and not layers.relay("top", "force push main")[0], "relayed words in a safety class are refused")
check(not layers.relay("peer", "approve the plan")[0] and layers.relay("owner", "delete it")[0], "words from a peer are refused; the owner's own typed words count")
check(layers.role("top") == "top" and layers.role("bogus") == "" and layers.role("") in ("", "top", "machine"), "the role is top, machine or today's loop")

import argparse  # noqa: E402
import contextlib  # noqa: E402
import io  # noqa: E402
import operate  # noqa: E402


def one_pass(role):
    """operate.one_pass in a bare folder with every script call recorded: (what it printed, the scripts it ran)."""
    ran, out = [], io.StringIO()
    with tempfile.TemporaryDirectory() as tmp:
        common = os.path.join(tmp, ".git")
        os.makedirs(os.path.join(common, "loop"))
        keep = (operate.script, operate.refresh, operate.behind_ask)
        operate.script = lambda name, *a, cwd=None: (ran.append(name), (0, "board text" if name == "checkin.py" else ""))[1]
        operate.refresh = operate.behind_ask = lambda *a: ""
        try:
            with contextlib.redirect_stdout(out):
                operate.one_pass(tmp, common, argparse.Namespace(role=role, max=0, skill_dir="", board=False))
        finally:
            operate.script, operate.refresh, operate.behind_ask = keep
    return out.getvalue().strip(), ran


said, ran = one_pass("machine")
check(len(said.splitlines()) == 1 and "STATUS" in said and "board text" not in said and "board_page.py" not in ran, "a machine pass prints one line, never the check-in or board, and publishes no Loop Board")
check("watch.py" in ran and "checkin.py" in ran, "a machine pass runs today's loop")
said, ran = one_pass("top")
check("board_page.py" in ran and "watch.py" not in ran and "checkin.py" not in ran, "top only builds the board and publishes it: it starts no goal")
said, ran = one_pass("")
check("board text" in said and "board_page.py" in ran, "no role runs today's loop and prints the check-in")

hook = os.path.join(scripts, "reply_hook.py")
with tempfile.TemporaryDirectory() as tmp:
    reply = os.path.join(tmp, "reply.txt")
    open(reply, "w").write("14:05 mac: STATUS sent, 2 workers\n")
    env = dict(os.environ, LOOP_OP_ROLE="")
    full = subprocess.run([sys.executable, hook, "check", reply], capture_output=True, text=True, env=env, cwd=tmp)
    check(full.returncode != 0, "top keeps the full-layout check: a one-line reply is refused")
    common = os.path.join(tmp, ".git")
    os.makedirs(os.path.join(common, "loop", "status"))
    subprocess.run(["git", "init", "-q", tmp], check=True)
    sent = os.path.join(common, "loop", "status", layers.machines.me() + ".json")
    check(layers.machine_reply("14:05 mac: STATUS sent", common) != [], "a machine one-liner is refused before STATUS went to top")
    open(sent, "w").write("{}")
    check(layers.machine_reply("14:05 mac: STATUS sent", common) == [] and layers.machine_reply("14:35 mac: no change", common) == [], "after STATUS went to top, 'STATUS sent' and 'no change' one-liners pass")
    check(layers.machine_reply("STATUS sent", common) != [] and layers.machine_reply("14:05 all fine\nmore", common) != [], "a line with no time, or two lines, is refused")
    machine = subprocess.run([sys.executable, hook, "check", reply], capture_output=True, text=True, env=dict(os.environ, LOOP_OP_ROLE="machine"), cwd=tmp)
    check(machine.returncode == 0, "the hook's check in machine mode accepts the one-line check-in")

print("ALL PASS" if not fails else "%d FAILED" % fails)
sys.exit(1 if fails else 0)
