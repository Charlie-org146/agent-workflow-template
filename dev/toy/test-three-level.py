#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-monitoring/scripts/layers.py skills/workflow-monitoring/scripts/operate.py skills/workflow-monitoring/scripts/reply_hook.py skills/workflow-monitoring/scripts/sessions.py skills/workflow-monitoring/scripts/notify.py skills/workflow-monitoring/scripts/govern_hook.py skills/workflow-monitoring/scripts/board_log.py skills/workflow-monitoring/scripts/board_model.py skills/workflow-delivery/scripts/guards.py skills/workflow-delivery/scripts/goal.py
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
    check("two tokens" in rows["agent_command is one --allowedTools=<list> token"] and layers.check_allowed({"agent_command": ["claude", "--allowedTools=Bash,Read"]}) == "ok", "the two-token --allowedTools form is reported, one token is ok")
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

# HLT-2 red-team pass: input, record and due read and record only; they never edit a repo file, merge, file or send.
import builtins  # noqa: E402
import hashlib  # noqa: E402

REPLY = "A: the Mac's STATUS is trusted but was never re-read\nI: a free PC slot could start a known-red goal\nnoise\nR: the 3.0 GB floor stalls every lane at once\n"
with tempfile.TemporaryDirectory() as tmp:
    common = os.path.join(tmp, ".git")
    for name, item in (("mac", mac), ("pc", pc)):
        layers.write(os.path.join(common, "loop", "status", name + ".json"), item)
    open(os.path.join(tmp, "README.md"), "w").write("repo file")
    redteam = os.path.join(common, "loop", "redteam")

    def snapshot():
        return {os.path.join(d, f): hashlib.sha1(open(os.path.join(d, f), "rb").read()).hexdigest()
                for d, _, files in os.walk(tmp) for f in files if not d.startswith(redteam)}

    before, writes, calls = snapshot(), [], []
    real_open, real_run = builtins.open, subprocess.run
    builtins.open = lambda f, mode="r", *a, **k: (writes.append(os.path.abspath(str(f))) if any(c in mode for c in "wax+") else None, real_open(f, mode, *a, **k))[1]
    subprocess.run = lambda cmd, *a, **k: (calls.append(cmd), real_run(cmd, *a, **k))[1]
    try:
        text = layers.reviewer_input(common, now)
        routes = layers.record(common, REPLY, now)
    finally:
        builtins.open, subprocess.run = real_open, real_run
    check("STATUS mac" in text and "STATUS pc" in text and "mac/a build running" in text and "exactly one `R:" in text, "red-team input holds the board and each machine's latest STATUS, and asks for the three lists")
    saved = layers.read(os.path.join(redteam, os.listdir(redteam)[0]))
    check(saved["time"] == layers.iso(now) and saved["assumptions"] == ["the Mac's STATUS is trusted but was never re-read"] and len(saved["idle"]) == 1 and saved["risk"].startswith("the 3.0 GB floor"), "red-team record stores the three lists with a timestamp")
    filing = 'ROUTE ops-findings: python3 skills/workflow-monitoring/scripts/mailbox.py finding "the Mac\'s STATUS is trusted but was never re-read" --feature <PAGE> --found redteam/'
    check(routes[0].startswith(filing) and routes[1:] == ["ROUTE TOP-DECISION (proposed): I: a free PC slot could start a known-red goal",
                                                          "ROUTE TOP-DECISION (proposed): R: the 3.0 GB floor stalls every lane at once"], "each item is routed: assumptions to the ops-findings filing command, idle work and the risk to top as a proposed TOP-DECISION")
    words = [w for c in calls for w in (c if isinstance(c, (list, tuple)) else str(c).split())]
    check(writes and all(w.startswith(redteam) for w in writes) and snapshot() == before, "the red-team pass writes only under the git folder's loop/redteam and changes no repo file")
    check(not {"merge", "push", "gh", "send", "commit", "add"} & set(map(str, words)), "the red-team pass runs no merge, push, gh, send or commit")
    try:
        layers.record(common, "R: one\nR: two\n", now + 1)
        refused = False
    except SystemExit as stop:
        refused = "exactly one biggest risk" in str(stop)
    check(refused and len(os.listdir(redteam)) == 1, "negative control: two R: lines are refused and nothing is recorded")
    check(layers.due(common, now + 59 * 60).startswith("RED-TEAM ok") and layers.due(common, now + 61 * 60).startswith("RED-TEAM DUE"), "a pass is due once the last is over an hour old, not before")
    eta = now + 30 * 60
    check(layers.due(common, now + 25 * 60, eta).startswith("RED-TEAM DUE: the release ETA") and layers.due(common, now + 10 * 60, eta).startswith("RED-TEAM ok"), "a pass is due within an hour of a release ETA unless one ran in the last 20 minutes")
    check("RED-TEAM DUE" in layers.publish_board(common, {}, now + 61 * 60) and "RED-TEAM" not in layers.publish_board(common, {}, now + 60), "the top board carries the due line only when a pass is due")
with tempfile.TemporaryDirectory() as tmp:
    check(layers.due(os.path.join(tmp, ".git"), now) == "RED-TEAM DUE: no pass recorded", "with no pass recorded a pass is due")

# HLT-2 red team on a plan: a fresh-context reviewer reads one goal's plan and records findings; a goal frozen after the rule's cut-over
# cannot build without a review of its current plan, and a recorded principle break blocks until a fresh clean review or an owner record.
import board_model  # noqa: E402
import govern_hook  # noqa: E402
import notify  # noqa: E402

guards_py = os.path.join(here, "..", "..", "skills", "workflow-delivery", "scripts", "goal.py")
LATE, EARLY = "2099-01-01T00:00:00Z frozen 1 done lines", "2020-01-01T00:00:00Z frozen 1 done lines"


def step_build(tmp, log=LATE):
    state = {"slug": "g", "status": "running", "step": "plan", "tries": 0, "flow": {}, "goal": "g", "branch": "loop/g", "log": [log]}
    with open(os.path.join(tmp, ".git", "loop", "runs", "g.json"), "w") as handle:
        json.dump(state, handle)
    got = subprocess.run([sys.executable, guards_py, "step", "g", "build"], capture_output=True, text=True, cwd=tmp, env=dict(os.environ, LOOP_ROLE="worker"))
    return got.returncode, got.stdout + got.stderr


with tempfile.TemporaryDirectory() as tmp:
    subprocess.run(["git", "init", "-q", tmp], check=True)
    for sub in (".loop/goals", ".git/loop/runs", "docs/wiki"):
        os.makedirs(os.path.join(tmp, sub))
    plan = os.path.join(tmp, ".loop", "goals", "g.plan.md")
    for name, body in ((".loop/config.json", "{}"), (".loop/goals/g.md", "# g\n"), (".loop/goals/g.design.md", "design text\n"), (".loop/goals/g.plan.md", "plan v1\n"),
                       ("docs/wiki/Principles.md", "## 1. Documentation-driven\nfirst\n## 2. The loop\nsecond\n## 3. The docs are true\nthird\n")):
        open(os.path.join(tmp, name), "w").write(body)
    red = os.path.join(tmp, ".git", "loop", "redteam")
    ls = lambda: sorted(n for n in os.listdir(red) if n == "plan-g.json") if os.path.isdir(red) else []
    repo_files = lambda: {os.path.join(d, f): hashlib.sha1(open(os.path.join(d, f), "rb").read()).hexdigest() for d, ds, fs in os.walk(tmp) if ".git" not in d.split(os.sep) for f in fs}
    before, writes, calls = repo_files(), [], []
    real_open, real_run = builtins.open, subprocess.run
    builtins.open = lambda f, mode="r", *a, **k: (writes.append(os.path.abspath(str(f))) if any(c in mode for c in "wax+") else None, real_open(f, mode, *a, **k))[1]
    subprocess.run = lambda cmd, *a, **k: (calls.append(cmd), real_run(cmd, *a, **k))[1]
    try:
        asked = notify.plan_input(tmp, "g")
        lines = govern_hook.plan_record(tmp, "g", "A: the plan trusts main\nR: lane waits\nB3: the plan contradicts a page\nC: reuse the old toy\n", now)
    finally:
        builtins.open, subprocess.run = real_open, real_run
    os.rename(os.path.join(tmp, ".loop", "goals", "g.design.md"), os.path.join(tmp, ".loop", "goals", "g.design.bak"))
    check("plan v1" in notify.plan_input(tmp, "g") and "design text" not in notify.plan_input(tmp, "g"), "a goal with no design file still gets its plan reviewed")
    os.rename(os.path.join(tmp, ".loop", "goals", "g.design.bak"), os.path.join(tmp, ".loop", "goals", "g.design.md"))
    check("plan v1" in asked and "design text" in asked and "3. The docs are true" in asked and "B<n>" in asked, "the plan review input holds the goal's design and plan, the principles and the request")
    saved = layers.read(os.path.join(red, ls()[0]))
    check(saved["time"] == layers.iso(now) and saved["assumptions"] == ["the plan trusts main"] and saved["risks"] == ["lane waits"] and saved["cheaper"] == ["reuse the old toy"]
          and [(b["principle"], b["text"]) for b in saved["breaks"]] == [(3, "the plan contradicts a page")] and saved["sha"] and lines == ["BREAK principle 3: the plan contradicts a page"],
          "the findings are recorded with a timestamp, each break naming its principle")
    words = [w for c in calls for w in (c if isinstance(c, (list, tuple)) else str(c).split())]
    check(writes and all(w.startswith(red) for w in writes) and repo_files() == before and not {"merge", "push", "gh", "send", "commit", "add"} & set(map(str, words)),
          "the plan reviewer reads only: it writes under loop/redteam alone, changes no repo file and runs no merge, push, gh, send or commit")
    piped = subprocess.run([sys.executable, os.path.join(scripts, "notify.py"), "plan-record", "g", "-"], input="B3: the plan contradicts a page\n", capture_output=True, text=True, cwd=tmp)
    check(piped.stdout.strip() == "BREAK principle 3: the plan contradicts a page", "the plan findings can be piped in on stdin (plan-record SLUG -)")
    for bad in ("B: no number\n", "B9: no such principle\n"):
        try:
            govern_hook.plan_record(tmp, "g", bad, now + 5)
            refused = False
        except SystemExit as stop:
            refused = "must name its principle" in str(stop)
        check(refused and len(ls()) == 1, "negative control: a break %r that names no known principle is refused and nothing is recorded" % bad.strip())
    check(layers.due(os.path.join(tmp, ".git"), now + 60) == "RED-TEAM DUE: no pass recorded", "the hourly pass ignores plan findings")
    code, said = step_build(tmp)
    check(code == 2 and "break of principle 3" in said and "PLAN_BREAK" in said, "a recorded principle break blocks the goal's build step")
    open(os.path.join(tmp, ".git", "loop", "owner-words.tsv"), "w").write("o1\t2026-11-19T00:00:00Z\ts\t{}\n")
    refused = []
    for args in ((3, "o99"), (2, "o1")):
        try:
            board_model.plan_accept(tmp, "g", *args)
        except SystemExit:
            refused.append(args)
    check(len(refused) == 2 and step_build(tmp)[0] == 2, "negative control: an owner record that does not exist, or a principle with no break, accepts nothing and the build stays blocked")
    board_model.plan_accept(tmp, "g", 3, "o1")
    code, said = step_build(tmp)
    check(code == 0 and "STEP g build" in said, "an owner record that accepts the break lets the build start")
    open(plan, "w").write("plan v2\n")
    code, said = step_build(tmp)
    check(code == 2 and "the plan changed since its last review" in said, "a plan changed since its last review blocks the build until a fresh review is recorded")
    check(step_build(tmp, EARLY)[0] == 0, "negative control: a goal frozen before the rule's cut-over is exempt from the review requirement")
    os.rename(os.path.join(tmp, "docs", "wiki", "Principles.md"), os.path.join(tmp, "docs", "wiki", "P.bak"))
    check(step_build(tmp)[0] == 0, "negative control: a repo with no principles page has nothing to red-team against, so a late goal builds (the toy repos)")
    os.rename(os.path.join(tmp, "docs", "wiki", "P.bak"), os.path.join(tmp, "docs", "wiki", "Principles.md"))
    govern_hook.plan_record(tmp, "g", "A: only an assumption\n", now + 120)
    check(step_build(tmp)[0] == 0, "a fresh clean review of the changed plan unblocks the build")
    govern_hook.plan_record(tmp, "g", "B1: the plan breaks principle one\n", now + 240)
    check(step_build(tmp)[0] == 2 and step_build(tmp, EARLY)[0] == 2, "a fresh review that finds a break blocks again, for a goal frozen before the cut-over too")
    os.remove(os.path.join(red, "plan-g.json"))
    code, said = step_build(tmp)
    check(code == 2 and "no recorded review of the current plan" in said and step_build(tmp, EARLY)[0] == 0, "a goal frozen after the cut-over with no recorded review cannot build; one frozen before it can")

print("ALL PASS" if not fails else "%d FAILED" % fails)
sys.exit(1 if fails else 0)
