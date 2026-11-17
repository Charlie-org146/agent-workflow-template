#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-delivery/scripts/tokens.py skills/workflow-delivery/scripts/fit.py skills/workflow-delivery/scripts/proctree.py skills/workflow-monitoring/scripts/optokens.py skills/workflow-monitoring/scripts/reply_hook.py skills/workflow-monitoring/scripts/checkin.py
"""token-diet (#4788): per-step tokens from a transcript, the operation session's token rows, the budget unit, a quiet check-in,
the reply layout only for check-ins, and the 2,000-character output cap. Every check prints one PASS or FAIL line."""
import io
import json
import os
import subprocess
import sys
import tempfile
import types
from contextlib import redirect_stdout

root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DELIVERY = os.path.join(root, "skills", "workflow-delivery", "scripts")
MONITORING = os.path.join(root, "skills", "workflow-monitoring", "scripts")
sys.path[:0] = [DELIVERY, MONITORING]
import fit  # noqa: E402
import optokens  # noqa: E402
import reply_hook  # noqa: E402
import tokens  # noqa: E402

fails = 0


def check(name, ok):
    global fails
    print(("PASS: " if ok else "FAIL: ") + name)
    fails += 0 if ok else 1


work = tempfile.mkdtemp(prefix="token-diet-")
projects = os.path.join(work, "projects", "p")
os.makedirs(projects)
os.environ["LOOP_TRANSCRIPT_DIR"] = os.path.join(work, "projects")
SID = "11111111-2222-3333-4444-555555555555"
OPS = "99999999-8888-7777-6666-555555555555"


def call(mid, at, inp, read, write, out, model="claude-sonnet-5-5"):
    return {"type": "assistant", "timestamp": at, "message": {"id": mid, "model": model, "content": [], "usage": {
        "input_tokens": inp, "cache_read_input_tokens": read, "cache_creation_input_tokens": write, "output_tokens": out}}}


def user(text, at):
    return {"type": "user", "timestamp": at, "message": {"role": "user", "content": text}}


def put(session, entries, mode="w"):
    with open(os.path.join(projects, session + ".jsonl"), mode, encoding="utf-8") as handle:
        for entry in entries:
            handle.write(json.dumps(entry) + "\n")


# 1. a step's tokens come from the transcript, a call counted once
put(SID, [user("go", "2026-11-17T00:00:01Z"),
          call("m1", "2026-11-17T00:00:10Z", 5, 1000, 200, 10), call("m1", "2026-11-17T00:00:11Z", 5, 1000, 200, 40),
          call("m2", "2026-11-17T00:00:20Z", 3, 3000, 100, 20, "claude-opus-5-5"),
          call("m3", "2026-11-17T00:01:30Z", 7, 5000, 50, 30)])
os.environ["CLAUDE_CODE_SESSION_ID"] = SID
state = {"slug": "g", "log": ["2026-11-17T00:00:00Z g: frozen"]}
tokens.add(state, "idea", "unknown", True, now="2026-11-17T00:01:00Z")
got = state["tokens"]["idea"]
check("step tokens: a step holds input, cache reads, cache writes, output, calls, model and peak context from the transcript",
      got == {"input": 8, "cache_read": 4000, "cache_write": 300, "output": 60, "calls": 2, "model": "claude-sonnet-5-5", "peak": 3103} or
      got == {"input": 8, "cache_read": 4000, "cache_write": 300, "output": 60, "calls": 2, "model": "claude-opus-5-5", "peak": 3103})
tokens.add(state, "plan", "unknown", True, now="2026-11-17T00:02:00Z")
check("step tokens: the next step counts only the calls after the last mark",
      state["tokens"]["plan"]["calls"] == 1 and state["tokens"]["plan"]["input"] == 7 and state["tokens"]["idea"]["calls"] == 2)
shown = types.SimpleNamespace(load=lambda slug: dict(state), guards=types.SimpleNamespace(moved_since_plan=lambda g, s: None), config=lambda: {})
fit.resume_at, fit.active_minutes = (lambda *a: ""), (lambda *a: 0)
fit.monitor = lambda *a, **k: types.SimpleNamespace(wall_minutes=lambda s: 0)
out = io.StringIO()
with redirect_stdout(out):
    fit.cmd_show(shown, types.SimpleNamespace(slug="g"))
lines = [l for l in out.getvalue().splitlines() if l.startswith("TOKENS ")]
check("step tokens: goal.py show lists each step's fields", len(lines) == 2 and lines[0].startswith("TOKENS idea: input 8, cache_read 4,000, cache_write 300, output 60, 2 calls"))
older = {"slug": "g", "tokens": {"build": 1500}}
tokens.add(older, "build", "250")
check("step tokens: an int an older step reported still adds up", older["tokens"]["build"] == 1750)

# 2. the operation session's rows, by trigger
repo = os.path.join(work, "repo")
os.makedirs(os.path.join(repo, ".loop"))
subprocess.run(["git", "init", "-q", repo], check=True)
with open(os.path.join(repo, ".loop", "config.json"), "w") as handle:
    handle.write("{}")
common = os.path.realpath(os.path.join(repo, ".git"))
os.makedirs(os.path.join(common, "loop"))
with open(os.path.join(common, "loop", "operation.id"), "w") as handle:
    handle.write("op2\n" + OPS + "\n")
turns = [user("Operation-pc check-in, every 30 minutes. Governance only.", "2026-11-17T01:00:00Z"), call("a1", "2026-11-17T01:00:05Z", 1, 100, 10, 4),
         user("<system-reminder>\nThe session \"worker\" finished a turn. It reported", "2026-11-17T01:01:00Z"), call("a2", "2026-11-17T01:01:05Z", 1, 200, 10, 4),
         user("make it faster", "2026-11-17T01:02:00Z"), call("a3", "2026-11-17T01:02:05Z", 1, 300, 10, 4),
         user("Stop hook feedback:\nREPLY FORMAT (MON-5): missing", "2026-11-17T01:03:00Z"), call("a4", "2026-11-17T01:03:05Z", 1, 400, 10, 4)]
put(OPS, turns)
first = optokens.append(repo, now="2026-11-17T01:04:00Z").split("\t")
check("op tokens: a row holds time, session, context and the tokens under scheduled, peer, human and hook-retry",
      first[:2] == ["2026-11-17T01:04:00Z", OPS] and first[2:] == ["411", "115", "215", "315", "415", "1060"])
put(OPS, [user("Operation-pc check-in, every 30 minutes.", "2026-11-17T01:10:00Z"), call("a5", "2026-11-17T01:10:05Z", 1, 500, 10, 4)], "a")
second = optokens.append(repo, now="2026-11-17T01:11:00Z").split("\t")
with open(os.path.join(common, "loop", "op-tokens.tsv")) as handle:
    table = handle.read().splitlines()
check("op tokens: the next row holds only what was spent since the last one, under the file's header",
      second[3:] == ["515", "0", "0", "0", "515"] and len(table) == 3 and table[0].startswith("# time\tsession\tcontext\tscheduled"))

# 3. the token budget reads measured tokens
cfg = {"token_budget": 3000000}


def stops(run):
    try:
        fit.budget_stop("g", run, "/none", cfg)
    except SystemExit as stopped:
        return "BUDGET_TOKENS" in str(stopped)
    return False


check("budget: a goal seeded with 3,000,000 measured tokens is refused at its next step",
      stops({"slug": "g", "tokens": {"build": {"input": 1000000, "cache_write": 1500000, "output": 500000, "calls": 90}}}))
check("budget: cache reads alone never stop a goal",
      not stops({"slug": "g", "tokens": {"build": {"input": 100, "cache_read": 90000000, "cache_write": 5000, "output": 900, "calls": 400}}}))
put(SID, [call("m9", "2026-11-17T00:05:00Z", 2000000, 0, 0, 1000001)], "a")
live = {"slug": "g", "token_at": "2026-11-17T00:04:00Z", "tokens": {"build": {"input": 10, "output": 10}}}
check("budget: the open window since the last mark counts too", stops(live))

# 4. a scheduled check-in with nothing new skips the model turn
prompt = "Operation-pc check-in, every 30 minutes (owner o108). Governance only: assign, watch, report."
payload = {"session_id": OPS, "cwd": repo, "prompt": prompt}
seen = "Machine: 4 GB free\n2 running, 0 waiting on you; pool 3 idle\nAll sessions\n| a | repo | for | running | build 4/8 | 12m, ETA 10:04 | latest |"
optokens.remember(common, seen, now=1000000)
same = seen.replace("4 GB", "9 GB").replace("12m", "9m").replace("10:04", "11:30")
block = optokens.decide(payload, text=same, now=1000000 + 600)
check("quiet: an unchanged check-in is blocked with one line and no model turn", bool(block) and block["decision"] == "block" and "\n" not in block["reason"])
check("quiet: a check-in whose words changed goes through", optokens.decide(payload, text=same.replace("running", "waiting"), now=1000000 + 600) is None)
check("quiet: an unchanged check-in more than two hours after the last full one goes through", optokens.decide(payload, text=same, now=1000000 + 7300) is None)
check("quiet: a prompt that is not the scheduled check-in goes through", optokens.decide(dict(payload, prompt="where do things stand"), text=same, now=1000000 + 600) is None)
check("quiet: a session that is not the operation session goes through",
      optokens.decide(dict(payload, session_id="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"), text=same, now=1000000 + 600) is None)

# 5. the layout is asked of check-ins only
peer = [user('<system-reminder>\nThe session "worker - x" finished a turn. It reported', "t")]
check("layout: a peer message turn needs no layout", optokens.needs_layout(peer) is False)
check("layout: a scheduled check-in needs it", optokens.needs_layout([user(prompt, "t")]) is True)
check("layout: a hook retry after a check-in still needs it", optokens.needs_layout([user(prompt, "t"), user("Stop hook feedback:\nx", "t")]) is True)
check("layout: the owner asking where things stand needs it, other talk does not",
      optokens.needs_layout([user("where do things stand", "t")]) is True and optokens.needs_layout([user("yes, merge it", "t")]) is False)
check("layout: a turn that can't be read needs it", optokens.needs_layout([]) is True)
path = os.path.join(projects, OPS + ".jsonl")


def reply(entries, text):
    put(OPS, entries)
    for name in os.listdir(os.path.join(common, "loop", "reply-hook")) if os.path.isdir(os.path.join(common, "loop", "reply-hook")) else []:
        os.remove(os.path.join(common, "loop", "reply-hook", name))
    return reply_hook.hook({"session_id": OPS, "cwd": repo, "transcript_path": path, "last_assistant_message": text})


short = "Noted. worker-x merged.\nNothing else to do."
check("layout: a 2-line reply to a peer message passes the reply hook", reply(peer, short) is None)
blocked = reply([user(prompt, "t")], "All quiet.")
check("layout: a one-line reply to a scheduled check-in is still blocked", isinstance(blocked, dict) and blocked.get("decision") == "block")

# 6. output over 2,000 characters is cut in the middle, the whole kept in a file
script = ("import sys; sys.path.insert(0, %r); import proctree; proctree.outcap('t.py'); n = int(sys.argv[1]); "
          "print('A' * (n // 2)); print('B' * (n - n // 2 - 2)); print('END')" % DELIVERY)


def run(n, cap=None):
    env = dict(os.environ, PYTHONUTF8="1")
    env.pop("LOOP_OUTPUT_CAP", None)
    cap is not None and env.update(LOOP_OUTPUT_CAP=cap)
    return subprocess.run([sys.executable, "-c", script, str(n)], cwd=repo, env=env, capture_output=True, text=True).stdout


big = run(5000)
saved = big.split("the full output is in ")[1].split(" ...]")[0] if "the full output is in " in big else ""
check("output cap: 5,000 characters print as at most about 2,300 with a line saying where the full text is",
      len(big) < 2300 and "characters cut" in big and big.rstrip().endswith("END") and big.startswith("A"))
check("output cap: the full text is readable at the named file", bool(saved) and os.path.exists(saved) and len(open(saved).read()) >= 5000)
check("output cap: output under 2,000 characters is untouched", run(1500).count("A") + run(1500).count("B") >= 1490 and "cut" not in run(1500))
check("output cap: LOOP_OUTPUT_CAP=0 turns it off", len(run(5000, "0")) >= 5000)

sys.exit(1 if fails else 0)
