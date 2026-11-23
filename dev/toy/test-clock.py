#!/usr/bin/env python3
"""DEL-17 (v1.1.0): every step has a time limit set in settings, lead time shows per step and goal, a step over its limit
shows as missed with its cause, an ETA names its history, and no release goes out while main is known broken.

usage: test-clock.py [17.1|17.2|17.3|17.4|17.5]   (no argument runs all five; each prints its own `ALL PASS 17.n` line)

Hermetic: a fake HOME, a temporary repo with a local origin name, a stub steps module (the real one belongs to the steps
goal) and a fake gh that answers from a JSON file. Nothing touches the network or the owner's machine."""
import datetime
import hashlib
import importlib.util
import json
import argparse
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SK = os.path.join(ROOT, "skills")
MON, REL, SET = (os.path.join(SK, s, "scripts") for s in ("workflow-monitoring", "workflow-release", "workflow-setup"))
TMP = tempfile.mkdtemp(prefix="test-clock-")
HOME = os.path.join(TMP, "home")
STUB = os.path.join(TMP, "stub")
BIN = os.path.join(TMP, "bin")
for d in (HOME, STUB, BIN):
    os.makedirs(d)
ENV = dict(os.environ, HOME=HOME, LOOP_MACHINE_NAME="mac", LOOP_BOARD_HEALTH="ok", PATH=BIN + os.pathsep + os.environ["PATH"],
           PYTHONPATH=STUB, GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", FAKE_GH=os.path.join(TMP, "gh.json"))
for key in [k for k in ENV if k.startswith(("CLAUDE", "ANTHROPIC", "LOOP_")) and k not in ("LOOP_MACHINE_NAME", "LOOP_BOARD_HEALTH")]:
    del ENV[key]
os.environ.update(ENV)
sys.path[:0] = [STUB, MON, REL]
WANT = sys.argv[1] if len(sys.argv) > 1 else ""
FAILS = {}
COUNT = {}
GROUP = ["17.1"]


def check(ok, message):
    COUNT[GROUP[0]] = COUNT.get(GROUP[0], 0) + 1
    if not ok:
        FAILS[GROUP[0]] = FAILS.get(GROUP[0], 0) + 1
    print("%s: DEL-%s: %s" % ("PASS" if ok else "FAIL", GROUP[0], message))


def want(group):
    GROUP[0] = group
    return not WANT or WANT == group


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(text)
    return path


# The stub of the one step list (the steps goal ships the real steps.py): entries read the run record's own "entries".
write(os.path.join(STUB, "steps.py"), textwrap.dedent('''\
    STEPS = ("freeze", "plan", "build", "quick checks", "tests", "merge", "after the merge", "release")
    def name_of(label):
        return label
    def entries(state):
        return [dict(e) for e in state.get("entries", [])]
    '''))
write(os.path.join(BIN, "gh"), textwrap.dedent('''\
    #!/usr/bin/env python3
    import json, os, sys, time
    state = json.load(open(os.environ["FAKE_GH"]))
    mode, args = state.get("mode", "ok"), sys.argv[1:]
    open(os.environ["FAKE_GH"] + ".log", "a").write(" ".join(args) + "\\n")
    if mode == "hang":
        time.sleep(30)
    if mode == "fail":
        sys.stderr.write("HTTP 401: bad credentials ghp_FAKE_TOKEN_FOR_TOY (login)\\n")
        sys.exit(1)
    jq = args[args.index("--jq") + 1] if "--jq" in args else ""
    if args[:2] == ["issue", "list"]:
        data = state.get("issues", [])
        if "--jq" in args:
            print("\\n".join(str(i["number"]) for i in data))
        else:
            print(json.dumps(data))
    elif args[:2] == ["pr", "list"]:
        if state.get("prs_fail"):
            sys.stderr.write("HTTP 502\\n")
            sys.exit(1)
        data = state.get("prs", [])
        if "--jq" in args:
            print("\\n".join(str(r["number"]) for p in data for r in p.get("closingIssuesReferences", [])))
        else:
            print(json.dumps(data))
    elif args[:2] == ["pr", "checks"]:
        print(json.dumps(state.get("checks", [])))
    '''))
os.chmod(os.path.join(BIN, "gh"), 0o755)


def fake(**state):
    json.dump(state, open(ENV["FAKE_GH"], "w"))


def sh(args, cwd=None, **kw):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, env=dict(ENV, **kw.pop("env", {})), **kw)


REPO = os.path.join(TMP, "repo")
os.makedirs(REPO)
sh(["git", "init", "-q", "-b", "main"], REPO)
sh(["git", "config", "user.email", "t@example.com"], REPO)
sh(["git", "config", "user.name", "t"], REPO)
sh(["git", "remote", "add", "origin", "https://github.com/acme/widget.git"], REPO)
write(os.path.join(REPO, ".loop", "config.json"), json.dumps({"base": "main", "step_report_limits": ""}))
write(os.path.join(REPO, "README.md"), "x\n")
sh(["git", "add", "-A"], REPO)
sh(["git", "commit", "-qm", "first"], REPO)
sh(["git", "tag", "v0.0.1"], REPO)
RUNS = os.path.join(REPO, ".git", "loop", "runs")
os.makedirs(RUNS)


def stamp(minutes):
    return (datetime.datetime(2026, 11, 20, 9, 0, tzinfo=datetime.timezone.utc) + datetime.timedelta(minutes=minutes)).strftime("%Y-%m-%dT%H:%M:%SZ")


def goal(slug, steps, status="done", extra=None, log_extra=()):
    """A run record whose log runs through steps [(name, minutes)] and whose entries are the same list."""
    log, entries, at = ["%s frozen 3 done lines" % stamp(0)], [], 0
    for name, mins in steps:
        log.append("%s start %s" % (stamp(at), name))
        at += mins
        entries.append({"step": name, "attempt": 1, "minutes": mins, "causes": [], "result": "done"})
    log += list(log_extra) + ["%s done" % stamp(at)]
    run = {"slug": slug, "status": status, "log": log, "entries": entries, "touches": ["docs"], "updated": stamp(at)}
    run.update(extra or {})
    write(os.path.join(RUNS, slug + ".json"), json.dumps(run))
    return run


import clock  # noqa: E402  (after PYTHONPATH and the stub are in place)

LEAD = [("freeze", 12), ("plan", 41), ("build", 65), ("tests", 4)]
SHA = lambda text: hashlib.sha256(text.encode()).hexdigest()

# ---------------------------------------------------------------------------------------------------------------- 17.1
if want("17.1"):
    named = {"quick checks": (1, "named"), "tests": (5, "named"), "merge": (5, "named")}
    check(all(clock.limit({}, k, s) == v for k, v in named.items() for s in ("doc", "code")),
          "the owner's named defaults (o755): quick checks 1, tests 5, merge 5 for both sizes")
    check(clock.limit({}, "PR checks", "doc") == (5, "named") and clock.limit({}, "PR checks", "code") == (30, "named"),
          "PR checks is 5 for a doc-only change and 30 for a code change")
    check(clock.limit({}, "push to main", "doc") == (3, "named") and clock.limit({}, "push to main", "code") == (35, "named"),
          "push to main is 3 for a doc-only change and 35 for a code change")
    check(all(clock.limit({}, "queue to main", z) == (10, "named") for z in ("doc", "code")), "queue to main is 10 minutes for both sizes (DEL-27.4, o742)")
    check(all(clock.limit({}, "pr to queue", z) == (1, "named") for z in ("doc", "code")), "pr to queue is 1 minute for both sizes (DEL-27.2, o742)")
    check(clock.limit({"step_report_limits": "queue_to_main=12,PR to queue=off"}, "queue to main", "code") == (12, "setting") and clock.limit({"step_report_limits": "PR to queue=off"}, "pr to queue", "doc")[0] is None, "a setting changes or switches off the queue limits with no code change")
    check(clock.limit({}, "plan", "code") == (None, "awaiting history") and clock.limit({}, "plan", "code", {"plan": 40}) == (40, "usual"),
          "a name with no named value starts at its measured usual, and shows 'awaiting history' without one")
    check(clock.limit({"step_report_limits": "tests=9"}, "tests", "code") == (9, "setting"),
          "changing a step's limit in settings applies with no code change")
    both = {"step_report_limits": "tests=9,doc:tests=7"}
    check(clock.limit(both, "tests", "doc")[0] == 7 and clock.limit(both, "tests", "code")[0] == 9 and clock.limit(both, "merge", "doc")[0] == 5,
          "a size entry wins over a bare entry, a bare entry applies to both sizes, a partial value keeps every other default")
    check(clock.parse("quick_checks=20,Docs-Check=4,PR CHECKS=off") == {(None, "quick checks"): 20, (None, "docs check"): 4, (None, "PR checks"): None},
          "names match ignoring case and space, hyphen or underscore; off switches one limit off")
    check(clock.parse("build=05") == {(None, "build"): 5}, "05 reads as 5")
    refused = []
    for bad in ("nope=5", "build=0x", "build=+5", "build=5.0", "build=1441", "build=5,Build=6", "quick checks=1,quick_checks=2", ",build=5", "build=5,", "build\u00a0x=5", "huge:tests=5"):
        try:
            clock.parse(bad)
        except ValueError:
            refused.append(bad)
    check(len(refused) == 11, "bad entries are refused: unknown name, 0x, +5, 5.0, over 1440, duplicates after normalizing, empty entries, NBSP, unknown size (%d of 11)" % len(refused))
    gone, off = clock.unset({"step_report_limits": "plan=off,freeze=50"}, {})
    check("freeze" not in gone and "plan" not in gone and off >= 2 and "build" in gone,
          "unset lists steps with no limit as awaiting history, and counts the ones switched off by choice (%d)" % off)
    cfgfile = write(os.path.join(TMP, "cfg", "config.json"), json.dumps({"step_report_limits": "tests=banana"}))
    done = sh([sys.executable, os.path.join(SET, "settings.py"), "fill-repo", "--repo", os.path.join(TMP, "cfg", "..", "cfg")], env={"PYTHONPATH": STUB})
    bad_run = subprocess.run([sys.executable, os.path.join(MON, "clock.py"), "check", cfgfile], capture_output=True, text=True, env=ENV)
    check(bad_run.returncode != 0 and "STEP_LIMITS_BAD" in bad_run.stderr and "banana" in bad_run.stderr and "Nothing was changed" in bad_run.stderr,
          "the check refuses a bad value with the STEP_LIMITS_BAD text on stderr and a non-zero exit")
    write(cfgfile, json.dumps({"step_report_limits": "build=45,code:tests=30"}))
    check(subprocess.run([sys.executable, os.path.join(MON, "clock.py"), "check", cfgfile], env=ENV).returncode == 0, "the check accepts a good value")
    check(subprocess.run([sys.executable, os.path.join(MON, "clock.py"), "check", os.path.join(TMP, "none", "config.json")], env=ENV).returncode == 0, "a first fill-repo with no config file yet passes the check")
    bad_cfg = {"step_report_limits": "tests=banana"}
    lines = clock.begin(REPO, datetime.datetime.now(datetime.timezone.utc))
    write(os.path.join(REPO, ".loop", "config.json"), json.dumps(bad_cfg))
    shown = clock.begin(REPO)
    check(len(shown) == 1 and "step_report_limits unreadable (STEP_LIMITS_BAD)" in shown[0] and not lines,
          "a hand-edited bad value shows ONE unreadable line and the template defaults apply")
    write(os.path.join(REPO, ".loop", "config.json"), json.dumps({"base": "main", "step_report_limits": ""}))
    quick = clock.check_missed("health", 12 * 60, {"step_report_limits": "health=10"})
    check(quick and "missed (was 12m, limit 10m)" in quick and clock.check_missed("health", 60, {"step_report_limits": "health=10"}) is None,
          "check_missed reports a check that took too long and nothing for one within its limit")
    check(clock.size({"touches": ["docs", "dev/toy", ".loop/regression.tsv"]}) == "doc" and clock.size({"touches": ["skills/workflow-delivery", "docs"]}) == "code"
          and clock.size({}) == "code", "change size comes from the recorded touches: docs and toy files are doc, any skills/ touch is code, none is code")
    mine = re.search(r'DOC = re\.compile\((r"[^\n]*")\)', open(os.path.join(MON, "clock.py")).read())
    theirs = re.search(r'docs = re\.compile\((r"[^\n]*")\)', open(os.path.join(REL, "release.py")).read())
    check(bool(mine and theirs) and mine.group(1) == theirs.group(1), "the doc-only pattern equals release.auto_need's pattern in release.py")
    show = textwrap.dedent(open(os.path.join(MON, "clock.py")).read())
    check(len(open(os.path.join(MON, "clock.py"), "rb").read()) < 19000 and "limit_" not in show,
          "clock.py is under 19,000 bytes and carries no per-step limit_ keys")

# ---------------------------------------------------------------------------------------------------------------- 17.2
if want("17.2"):
    run = goal("toy-goal", LEAD, extra={"release": "merged"})
    card = clock.lead_line(run)
    check(card and card[0].startswith("[lead] toy-goal 2h02m in all"), "the lead card's header carries the goal's total (%s)" % (card[0] if card else None))
    check(any("freeze 12m" in x and "build 1h05m" in x for x in card), "the card shows minutes per step")
    check(card[-1].startswith("  read from toy-goal.json log, ") and re.search(r"\d\d:\d\d$", card[-1]), "the last line says what it was read from, with the clock time")
    check(all(len(x) <= 60 for x in card) and all(x.startswith(("[", "  ")) for x in card), "every card line is at most 60 columns and is part of a card")
    long = goal("many", [(s, 7) for s in ("freeze", "plan", "build", "quick checks", "tests", "merge", "after the merge", "release")])
    wide = clock.lead_line(long)
    check(wide[0].endswith("56m in all") and all(len(x) <= 60 for x in wide) and len(wide) >= 3, "a long step list wraps and the total stays in the header")
    twice = goal("twice", [("tests", 4), ("tests", 3)])
    check("tests 7m" in " ".join(clock.lead_line(twice)), "a step done twice sums its attempts")
    check(clock.lead_line({"slug": "x", "log": []}) == [] and clock.lead_line({"slug": "x"}) == [], "a goal with no log gets no card")
    import board_lines  # noqa: E402
    item = {"slug": "toy-goal", "bars": [(1, 3, 0)], "left": 600}
    got = board_lines.bars(item, datetime.datetime.now(datetime.timezone.utc))
    os.chdir(REPO)
    clock.CTX.clear()
    got = board_lines.bars(item, datetime.datetime.now(datetime.timezone.utc))
    check(any(x.startswith("[lead] toy-goal") for x in got), "the check-in's goal lines (board_lines.bars) carry the lead card")
    import live_board  # noqa: E402
    goal("shipped-one", [("freeze", 5), ("tests", 5)], extra={"release": "merged"})
    goal("live-one", [("freeze", 5)], status="running")
    clock.CTX.clear()
    out = live_board.render(REPO)
    text = "\n".join(out)
    check("[lead] live-one" in text, "the live board shows the lead card of a live goal")
    check("Shipped" in text and "[shipped] shipped-one" in text and "freeze 5m" in text.split("Shipped", 1)[1], "a goal that merged shows its minutes per step on the live board under Shipped")
    shipped = text.split("\nShipped\n", 1)[1].split("\nFinish\n", 1)[0].strip().split("\n")
    check(shipped[-1].startswith("  read from") and text.rstrip().split("\n")[-3] == "Finish", "the Shipped section ends in a card line that says what it was read from, and Finish still closes the board")
    goal("broke", [("freeze", 5), ("tests", 9)], status="failed")
    clock.CTX.clear()
    check("[lead] broke" in "\n".join(live_board.render(REPO)), "a failed goal shows its lead card too")
    write(os.path.join(RUNS, "junk.json"), "[1, 2]")
    clock.CTX.clear()
    check("[lead] live-one" in "\n".join(live_board.render(REPO)) and any(x.startswith("[lead] toy-goal") for x in board_lines.bars(item, datetime.datetime.now(datetime.timezone.utc))),
          "a run file that is JSON but not an object leaves the live board and the check-in rendering their lead cards")
    os.remove(os.path.join(RUNS, "junk.json"))
    real, clock.minutes_of = clock.minutes_of, lambda entries: 1 // 0
    clock.CTX.clear()
    broken = clock.lead_line(json.load(open(os.path.join(RUNS, "live-one.json"))))
    board = live_board.render(REPO)
    clock.minutes_of = real
    check(broken == ["clock unavailable (CLOCK_ERROR: ZeroDivisionError); LOOP_DEBUG=1 prints the trace"] and "clock unavailable (CLOCK_ERROR: ZeroDivisionError" in "\n".join(board) and "Running goals" in board,
          "a failure inside clock is one CLOCK_ERROR line and the board still renders")
    keep = open(os.path.join(REPO, ".loop", "config.json")).read()
    write(os.path.join(REPO, ".loop", "config.json"), json.dumps({"base": "main", "step_report_limits": "tests=banana"}))
    clock.CTX.clear()
    shown = [x for x in live_board.render(REPO) if "step_report_limits unreadable (STEP_LIMITS_BAD)" in x]
    write(os.path.join(REPO, ".loop", "config.json"), keep)
    check(len(shown) == 1, "the live board prints the unreadable-setting line once per render")
    copy = os.path.join(TMP, "pathcopy", "skills")
    shutil.copytree(SK, copy)
    shutil.copy(os.path.join(STUB, "steps.py"), os.path.join(copy, "workflow-delivery", "scripts", "steps.py"))
    code = "import sys;sys.path.insert(0,sys.argv[1]);import clock;print(len(clock.steps()))"
    got = subprocess.run([sys.executable, "-c", code, os.path.join(copy, "workflow-monitoring", "scripts")], capture_output=True, text=True, cwd=TMP, env=dict(ENV, PYTHONPATH=""))
    check(got.stdout.strip() not in ("", "0"), "clock loads steps.py from workflow-delivery's scripts folder with no PYTHONPATH %s" % got.stderr[-100:])
    check(all(live_board.parse_at(t) == __import__("graph").parse_at(t) for t in ("2026-11-21T10:00:00Z", "2026-11-21T10:00:00", "bad", None)), "live_board.parse_at reads times as graph.parse_at does")
    html = subprocess.run([sys.executable, os.path.join(MON, "live_board.py"), "--html"], cwd=REPO, capture_output=True, text=True, env=ENV).stdout
    check("&lt;" not in "[lead]" and html.count("<section>") == 1 and "[shipped]" in html, "the HTML board carries the same section through live_board --html")
    for name in os.listdir(RUNS):
        if name.endswith(".json"):
            os.remove(os.path.join(RUNS, name))
    clock.CTX.clear()
    empty = live_board.render(REPO)
    check("Shipped" not in "\n".join(empty) and "[shipped]" not in "\n".join(empty), "with nothing merged there is no Shipped section at all")
    markup = goal("markup", [("tests", 3)], extra={"release": "merged", "log_extra": []})
    markup["slug"] = "<b>x</b>"
    write(os.path.join(RUNS, "markup.json"), json.dumps(dict(markup, log=markup["log"] + ["x"])))
    html2 = subprocess.run([sys.executable, os.path.join(MON, "live_board.py"), "--html"], cwd=REPO, capture_output=True, text=True, env=ENV).stdout
    check("<b>x</b>" not in html2, "markup in a goal name stays inert in the HTML board")

# ---------------------------------------------------------------------------------------------------------------- 17.3
if want("17.3"):
    entry = {"step": "tests", "attempt": 1, "minutes": 41, "causes": ["refused twice: DOC-18"], "waiting": None, "budget_hits": []}
    line = clock.missed(entry, {}, "code", {})
    check(line == "missed (was 41m, limit 5m): refused twice: DOC-18", "a step past its limit gives exactly 'missed (was <N>m, limit <L>m): <cause>' (%s)" % line)
    check(clock.missed(dict(entry, minutes=5), {}, "code", {}) is None and clock.missed(dict(entry, minutes=4), {}, "code", {}) is None, "a step within its limit gives nothing")
    check("waiting: review" in clock.missed(dict(entry, causes=[], waiting="waiting: review"), {}, "code", {}), "with no recorded cause the record's waiting reason is the cause")
    check(clock.missed(dict(entry, causes=[], waiting=None, budget_hits=[{"kind": "step"}]), {}, "code", {}).endswith("a budget hit: {'kind': 'step'}") or "budget" in clock.missed(dict(entry, causes=[], waiting=None, budget_hits=[{"kind": "step"}]), {}, "code", {}),
          "a budget hit is the cause when nothing else is")
    check(clock.missed(dict(entry, causes=[], waiting=None), {}, "code", {}).endswith("no cause recorded"), "with nothing recorded the cause says so")
    check("\x1b" not in clock.missed(dict(entry, causes=["bad\x1b[31m text"]), {}, "code", {}), "control characters never reach the line")
    check(clock.missed(dict(entry, minutes=500), {"step_report_limits": "tests=off"}, "code", {}) is None, "a limit switched off never misses")
    run = goal("slow", [("freeze", 3), ("tests", 41)])
    run["entries"][1]["causes"] = ["refused twice: DOC-18"]
    card = clock.lead_line(run)
    derived = [x for x in card if "missed (was" in x]
    check(len(derived) == 1 and derived[0].strip().startswith("tests: (derived) missed (was 41m, limit 5m)"), "a goal with no logged line shows the miss once, marked (derived)")
    logged_line = "missed (was 41m, limit 5m): refused twice: DOC-18"
    run2 = dict(run, log=run["log"][:-1] + ["%s tests %s" % (stamp(44), logged_line)] + run["log"][-1:])
    card2 = clock.lead_line(run2)
    shown = [x.strip() for x in card2 if "missed (was" in x]
    check(shown == ["tests: " + logged_line], "a logged line is shown as logged, once, under its step name, with no (derived) prefix")
    joined = " ".join(x.strip() for x in card[card.index(derived[0]):-1])
    check(joined[len("tests: (derived) "):] == shown[0][len("tests: "):], "the logged line and the derived one are byte-identical apart from the step name and the prefix")
    retry = goal("retry", [("tests", 3), ("tests", 3)])
    retry_card = clock.lead_line(retry)
    mixed = {"slug": "mix", "status": "running", "touches": ["docs"], "updated": stamp(0), "entries": [{"step": "merge", "attempt": 1, "minutes": 9, "causes": ["queue slow"], "start": "x"}, {"step": "after the merge", "attempt": 1, "minutes": 7, "causes": ["notes slow"], "start": "x"}],
             "log": ["2026-11-22T10:00:00Z after the merge missed (was 7m, limit 5m): notes slow"]}
    shown = clock.lead_line(mixed)
    check(sum("notes slow" in x for x in shown) == 1 and any("queue slow" in x and "missed (was 9m, limit 5m)" in x for x in shown),
          "a logged miss of after the merge is not read as merge's miss, and merge's own miss still shows")
    check(clock.merged_lines([dict(mixed, status="done")], {"mix"})[0].startswith("[shipped] mix 16m in all"), "a Shipped card keeps the goal's time in all in its header")
    clock.CTX["gh_end"] = time.monotonic() - 1
    spawned, real_run = [], subprocess.run
    subprocess.run = lambda *a, **k: spawned.append(a[0]) or real_run(*a, **k)
    got = clock.pr_checks({"pr": "7"})
    subprocess.run = real_run
    check(got is None and not spawned, "once a render's 10 second allowance for PR checks is spent, later goals make no gh call")
    clock.CTX["gh_end"] = time.monotonic() + 10
    check(any("missed (was 6m, limit 5m)" in x for x in retry_card), "a retry that stays under the limit per attempt but misses in total is a miss (attempts sum)")
    nostart = {"slug": "n", "log": ["%s frozen" % stamp(0)], "entries": [], "touches": ["docs"]}
    check(clock.lead_line(nostart)[0].startswith("[lead] n 0m in all") and not any("missed" in x for x in clock.lead_line(nostart)), "a goal with no steps shows no miss and does not fail")
    check(clock.missed(entry, {}, "code", {}) == clock.missed(dict(entry, attempt=2), {}, "code", {}), "the line does not carry the attempt: a retry never logs a different line")
    writer = open(os.path.join(MON, "clock.py")).read()
    check("open(" not in writer.split("def pr_checks")[0].split("def missed")[1].split("def context")[0], "missed writes nothing")

    # B3, B4, B5: PR checks compared with its limit, a usual for the checks, and the marker that says a limit is a measured usual
    os.chdir(REPO)
    for name in os.listdir(RUNS):
        if name.endswith(".json"):
            os.remove(os.path.join(RUNS, name))
    for i in range(3):
        goal("usual%d" % i, [("plan", 40), ("tests", 4)], extra={"check_seconds": {"health": 600, "docs check": 180}})
    clock.CTX.clear()
    got = clock.usual([json.load(open(os.path.join(RUNS, n))) for n in sorted(os.listdir(RUNS)) if n.endswith(".json")])
    check(got.get("plan") == 40 and got.get("health") == 10 and got.get("docs check") == 3 and "board" not in got,
          "health and docs check get a measured usual from their recorded seconds, and a check with no history gets none")
    check(clock.limit({}, "health", "code", got) == (10, "usual") and "health" not in clock.unset({}, got)[0] and "board" in clock.unset({}, got)[0],
          "a check with a usual has a limit and leaves the unset list; one without stays listed")
    def checks(minutes):
        fake(checks=[{"startedAt": "2026-11-22T10:00:00Z", "completedAt": "2026-11-22T10:%02d:00Z" % minutes, "state": "SUCCESS"}])
    live = goal("slowpr", [("plan", 55), ("tests", 4)], status="running", extra={"pr": "7", "touches": ["skills/x"]})
    checks(41)
    text = "\n".join(clock.lead_line(live, {}))
    check("PR checks 41m" in text and "missed (was 41m, limit 30m): the required checks took 41m" in text, "PR checks over its 30 minute code limit shows a missed line with its cause")
    check("plan limit 40m (measured usual on mac)" in text and "missed (was 55m, limit 40m)" in text,
          "a step whose limit is a measured usual says so on the card, and a step past it shows as missed")
    checks(20)
    check("missed (was 20m" not in "\n".join(clock.lead_line(live, {})), "PR checks under its limit shows no missed line")
    docs = dict(live, touches=["docs"])
    checks(7)
    check("missed (was 7m, limit 5m)" in "\n".join(clock.lead_line(docs, {})), "PR checks over the 5 minute doc limit shows a missed line")
    check("missed (was 7m" not in "\n".join(clock.lead_line(docs, {"step_report_limits": "PR checks=off"})), "a switched-off PR checks limit never misses")


# ---------------------------------------------------------------------------------------------------------------- 17.4
if want("17.4"):
    import auto  # noqa: E402
    import board_status as bs  # noqa: E402
    for i in range(3):
        goal("past%d" % i, [("plan", 10 + i), ("tests", 4)])
    root_cfg = {}
    new = auto.eta_new(REPO, "next", 3, ["docs"], 240, root_cfg)
    check("finished goals" in new["basis"] or "past goals" in new["basis"] or "no estimate yet" in new["basis"], "a new ETA's basis names its history or says there is none (%s)" % new["basis"])
    loop = os.path.join(REPO, ".git", "loop")
    now = time.time()
    bs.eta_say(loop, "goal", "next", "worker-x", new["basis"], int(now) + 3600, int(now))
    entry = list(bs.eta_fold(loop).values())[0]
    check(entry["who"] == "worker-x" and entry["said"] == int(now) and entry["basis"] == new["basis"] and entry["state"] == "open",
          "the ETA ledger entry records who, when and the basis with its history")
    bs.eta_say(loop, "goal", "next", "worker-x", "later", int(now) + 7200, int(now) + 10)
    states = sorted(e["state"] for e in bs.eta_fold(loop).values())
    check(states == ["missed", "open"], "restating an ETA marks the old one missed and keeps it visible")
    auto.eta_settle(loop, {}, now + 99999)
    check(all(e["state"] == "missed" for e in bs.eta_fold(loop).values()) and all(e.get("cause") for e in bs.eta_fold(loop).values() if "restated" not in e.get("cause", "x")),
          "a passed ETA shows as missed with its cause")
    check(clock.basis_suffix([], None, REPO).startswith(", too few finished goals (0 of 10)"), "with no finished goals the suffix says 'too few finished goals (0 of 10)'")
    old = bs.estimate_full
    bs.estimate_full = lambda *a, **k: (0, 0, 3600, False)
    reached = auto.eta_new(REPO, "next2", 3, ["docs"], 240, root_cfg)
    check(reached["estimate"] == 60 and reached["basis"].startswith("estimate 60m plus a 25% margin") and reached["basis"].endswith(clock.basis_suffix(
          [r for r in map(bs.read_json, glob.glob(os.path.join(REPO, ".git", "loop", "runs", "*.json"))) if isinstance(r, dict) and r.get("slug")], None, REPO)) and ", " in reached["basis"].split("margin", 1)[1],
          "with an estimate in hand, auto.eta_new's basis carries the history suffix (%s)" % reached["basis"])
    import board_model as bm  # noqa: E402
    oldm, oldb = bm.model, bm.backtest
    bm.model = lambda *a, **k: {}
    bm.backtest = lambda *a, **k: 1 / 0
    clock.BASIS.clear()
    broken = auto.eta_new(REPO, "next3", 3, ["docs"], 240, root_cfg)
    bm.model, bm.backtest, bs.estimate_full = oldm, oldb, old
    check(broken["basis"].endswith(", clock unavailable (CLOCK_ERROR: ZeroDivisionError)") and broken["estimate"] == 60,
          "a failing backtest never breaks the ETA: the basis says clock unavailable (CLOCK_ERROR)")
    builds = []
    realm = bm.model
    bm.model = lambda *a, **k: builds.append(1) or realm(*a, **k)
    clock.BASIS.clear()
    first = clock.basis_suffix([{"slug": "m1", "updated": "2026-01-01T00:00:00Z"}], None, REPO)
    after_first = len(builds)
    second = clock.basis_suffix([{"slug": "m1", "updated": "2026-01-01T00:00:00Z"}], None, REPO)
    bm.model = realm
    check(first == second and after_first > 0 and len(builds) == after_first, "the ETA history is built once for one run set, not once per goal (%d then %d model builds)" % (after_first, len(builds)))
    check(abs(auto.eta_margin({"eta_margin_percent": 40}) - 1.4) < 1e-9 and "%d%% margin" in open(os.path.join(MON, "auto.py")).read(), "the margin text of the basis is unchanged")

# ---------------------------------------------------------------------------------------------------------------- 17.5
if want("17.5"):
    import gate  # noqa: E402
    import release  # noqa: E402
    import autorelease  # noqa: E402
    import review  # noqa: E402
    os.chdir(REPO)
    check(release.hold is gate.hold and release.verify_steps is gate.verify_steps and review.left_text is gate.left_text and autorelease.release is release,
          "release.py and review.py re-export what moved to gate.py, and autorelease reaches the hold through release")
    sha = sh(["git", "rev-parse", "HEAD"], REPO).stdout.strip()
    sh(["git", "update-ref", "refs/remotes/origin/main", sha], REPO)
    rows = [("no issue", dict(issues=[]), "none"),
            ("one issue", dict(issues=[{"number": 12, "title": "regression row a is red"}]), "open 12"),
            ("two issues, the lowest named", dict(issues=[{"number": 30, "title": "b"}, {"number": 7, "title": "a"}]), "open 7"),
            ("the fourth row of the release.yml table", dict(issues=[{"number": 12, "title": "t"}], prs=[{"closingIssuesReferences": [{"number": 12, "url": "https://github.com/acme/widget/issues/12"}]}]), "none"),
            ("another issue stays", dict(issues=[{"number": 12, "title": "t"}, {"number": 13, "title": "u"}], prs=[{"closingIssuesReferences": [{"number": 12, "url": "https://github.com/acme/widget/issues/12"}]}]), "open 13"),
            ("no merged pull request for the tip", dict(issues=[{"number": 12, "title": "t"}], prs=[]), "open 12"),
            ("closing references unreadable", dict(issues=[{"number": 12, "title": "t"}], prs_fail=True), "unreadable"),
            ("gh fails with a token in its stderr", dict(mode="fail"), "unreadable"),
            ("200 issues is a truncated list", dict(issues=[{"number": n, "title": "t"} for n in range(1, 201)]), "unreadable")]
    release_yml = open(os.path.join(ROOT, ".github", "workflows", "release.yml")).read()
    hold = re.search(r"- id: hold\n\s+run: \|\n((?:\s{10}.*\n|\n)+?)\s+- if:", release_yml)
    check(bool(hold), "the release.yml hold step is found in the workflow (the row fails loudly if it moves)")
    script = textwrap.dedent(hold.group(1)) if hold else ""
    for label, state, expect in rows:
        fake(**state)
        got = gate.main_red(REPO)
        kind = got[0] if got[0] != "open" else "open " + got[1].split(":")[0]
        check(kind == expect, "the gate over '%s' says %s" % (label, expect))
        if expect in ("none", "open 12", "open 13", "open 7") and script and label != "two issues, the lowest named" and "200" not in label:
            out = subprocess.run(["bash", "-c", script], capture_output=True, text=True, env=dict(ENV, GITHUB_REPOSITORY="acme/widget", GITHUB_SHA=sha, GITHUB_OUTPUT=os.path.join(TMP, "gho")))
            held = "held: main red" in out.stdout
            check(held == (expect != "none"), "release.yml's own hold step agrees on '%s' (held=%s)" % (label, held))
    calls = [x for x in open(ENV["FAKE_GH"] + ".log").read().splitlines() if x.startswith("issue list") and "--json number,title" in x]
    check(bool(calls) and all("--label main-red" in x and "--state open" in x and "--limit 200" in x for x in calls), "every issue read asks gh for open issues labelled main-red, 200 at most")
    other = os.path.join(TMP, "norepo")
    sh(["git", "init", "-q", other])
    fake(issues=[{"number": 12, "title": "t"}])
    check(gate.main_red(other)[0] == "unreadable" and "MAIN_RED_UNREADABLE" in gate.hold(other, "toy-goal", 1), "a repo with no origin fails closed")
    sh(["git", "remote", "add", "origin", os.path.join(TMP, "norepo-origin")], other)
    check(gate.main_red(other)[0] == "unreadable" and "MAIN_RED_UNREADABLE" in gate.hold(other, "toy-goal", 1), "a local-path origin fails closed")
    sh(["git", "remote", "set-url", "origin", "https://git.example.test/a/b.git"], other)
    check(gate.main_red(other)[0] == "unreadable", "an origin on another host cannot be read, so the gate fails closed")
    sh(["git", "remote", "set-url", "origin", "https://notgithub.com/a/b.git"], other)
    check(gate.main_red(other)[0] == "unreadable", "an origin on a host that only ends in github.com fails closed")
    real, gate.read_red = gate.read_red, lambda top: 1 // 0
    got = gate.main_red(REPO)
    gate.read_red = real
    check(got[0] == "unreadable", "an unexpected failure while reading main-red issues is unreadable, never a pass")
    sh(["git", "remote", "set-url", "origin", "git@github.com:acme/widget.git"], other)
    check(gate.repo_of(other) == "acme/widget", "an ssh github.com origin names its repository")
    for reply in ({}, {"number": 12, "title": "t"}, [{"number": "12", "title": "t"}]):
        fake(issues=reply)
        check(gate.main_red(REPO)[0] == "unreadable", "an issue reply that is not a list of issues fails closed (%s)" % type(reply).__name__)
    mirror = os.path.join(TMP, "mirror")
    sh(["git", "init", "-q", mirror])
    sh(["git", "remote", "add", "origin", "https://github.com/acme/widget.git"], mirror)
    sh(["git", "config", "url.https://git.example.test/.insteadOf", "https://github.com/"], mirror)
    alias = os.path.join(TMP, "alias")
    sh(["git", "init", "-q", alias])
    sh(["git", "remote", "add", "origin", "gh:acme/widget"], alias)
    sh(["git", "config", "url.https://github.com/.insteadOf", "gh:"], alias)
    bare = os.path.join(TMP, "norepo2")
    sh(["git", "init", "-q", bare])
    sh(["git", "remote", "add", "origin", os.path.join(TMP, "norepo-origin")], bare)
    check(gate.repo_of(mirror) == "acme/widget", "a mirror's address (configured github.com, effective other host) still names the repository the origin names")
    check(gate.repo_of(alias) == "acme/widget", "an alias (configured shorthand, effective github.com) names the repository it stands for")
    fork = os.path.join(TMP, "fork")
    sh(["git", "init", "-q", fork])
    sh(["git", "remote", "add", "origin", "https://github.com/acme/widget.git"], fork)
    sh(["git", "config", "url.https://github.com/acme/other.insteadOf", "https://github.com/acme/widget"], fork)
    pushed = os.path.join(TMP, "pushed")
    sh(["git", "init", "-q", pushed])
    sh(["git", "remote", "add", "origin", "https://github.com/acme/widget.git"], pushed)
    sh(["git", "remote", "set-url", "--push", "origin", "https://github.com/acme/other.git"], pushed)
    check(gate.repo_of(fork) == "" and gate.repo_of(pushed) == "" and gate.main_red(fork)[0] == "unreadable" and gate.main_red(pushed)[0] == "unreadable",
          "an origin whose addresses name different github.com repositories is unreadable, so the hold never reads one repository while a release goes to another")
    check(gate.repo_of(bare) == "" and gate.main_red(bare)[0] == "unreadable", "an origin that neither its effective nor its configured address names as a github.com repository is unreadable")
    fake(issues=[{"number": 12, "title": "regression row a is red\x1b[31m"}])
    try:
        gate.hold(REPO, "toy-goal")
        cut = ""
    except SystemExit as stop:
        cut = str(stop)
    check(cut.startswith("REFUSED (MAIN_RED): issue 12") and "release.py cut toy-goal again" in cut and "hold=main-red:12" in cut and "\x1b" not in cut,
          "cut refuses, naming the issue and its own retry command")
    class Past(Exception):
        pass
    def stub(mod, **fns):
        old = {k: getattr(mod, k) for k in fns}
        for k, v in fns.items():
            setattr(mod, k, v)
        return lambda: [setattr(mod, k, v) for k, v in old.items()]
    back = stub(release, load=lambda slug: {"branch": "loop/toy-goal"}, finished=lambda state: None, toplevel=lambda state: REPO,
                git=lambda *a, **k: (_ for _ in ()).throw(Past("cut went past the hold")))
    try:
        release.cmd_cut(argparse.Namespace(slug="toy-goal", user=False))
        door = "no refusal"
    except SystemExit as stop:
        door = str(stop)
    except Past as stop:
        door = str(stop)
    back()
    check(door.startswith("REFUSED (MAIN_RED): issue 12") and "release.py cut toy-goal again" in door, "the real release.py cut refuses on an open main-red issue, naming it")
    back = stub(review, table=lambda top, name: [["rec", "", "", "", "v1.0.0"]], OK=lambda *a, **k: False,
                gate_refusals=lambda *a, **k: (_ for _ in ()).throw(Past("promote went past the hold")))
    try:
        review.promote(REPO, {}, 1, "rec", "ref")
        door = "no refusal"
    except SystemExit as stop:
        door = str(stop)
    except Past as stop:
        door = str(stop)
    back()
    check(door.startswith("REFUSED (MAIN_RED): issue 12"), "the real review.py promote refuses on an open main-red issue, naming it")
    auto_text = gate.hold(REPO, "toy-goal", 1)
    check(auto_text.startswith("(MAIN_RED) hold=main-red:12 the merge is done;") and "merge.py toy-goal again" in auto_text and len(auto_text) < 400, "the autorelease door returns its own recovery text, within release_error's size")
    state = {"slug": "toy-goal", "status": "done", "release": "merged"}
    fake(issues=[{"number": 12, "title": "t"}])
    try:
        autorelease.finish(REPO, {"base": "main"}, state)
        code = 0
    except SystemExit as stop:
        code = str(stop)
    check(isinstance(code, str) and code.startswith("REFUSED: (MAIN_RED)") and "REFUSED: REFUSED" not in code, "autorelease.finish refuses through fail() with one REFUSED prefix")
    check(state.get("release_error", "").startswith("(MAIN_RED)") and state.get("status") == "done", "the merge stays done and the refusal is recorded as release_error")
    fake(mode="fail")
    text = gate.hold(REPO, "toy-goal", 1)
    check("ghp_" not in text and "bad credentials" not in text and "MAIN_RED_UNREADABLE" in text and "gh exit code 1" in text, "an unreadable list names the class and exit code, never gh's text or a token")
    gate.TIMEOUT, gate.DEADLINE = 1, 2
    fake(mode="hang")
    began = time.time()
    got = gate.main_red(REPO)
    check(got[0] == "unreadable" and time.time() - began < 6, "a hanging gh ends in unreadable inside the deadline (%.1fs)" % (time.time() - began))
    gate.TIMEOUT, gate.DEADLINE = 30, 70
    check((gate.TIMEOUT, gate.DEADLINE) == (30, 70), "the shipped limits are 30 seconds a call and 70 seconds for the whole gate")
    fake(issues=[{"number": 12, "title": "t"}])
    check(subprocess.run([sys.executable, os.path.join(REL, "release.py"), "cut", "nope"], capture_output=True, text=True, env=ENV).returncode != 0, "release.py cut still refuses a goal that does not exist")
    fake(issues=[{"number": 12, "title": "t"}])
    held_a = {"slug": "held-a", "pr": "7", "release": "merged", "status": "done", "release_bullets": ["goal a work"], "release_steps": "steps of a"}
    why = autorelease.release.hold(REPO, "held-a", 1)
    try:
        autorelease.fail(held_a, why)
        refused = ""
    except SystemExit as stop:
        refused = str(stop)
    check(why != "" and "hold=main-red:12" in held_a.get("release_error", "") and refused.startswith("REFUSED: ") and held_a["status"] == "done" and autorelease.mergeable(held_a),
          "a held goal is merged, records its hold, keeps status done and can be run through merge.py again")
    check(held_a["release_bullets"] == ["goal a work"] and held_a["release_steps"] == "steps of a", "a held goal keeps its own release notes and its own verify steps")
    check(len(held_a["release_error"]) <= 400 and "merge.py held-a again" in held_a["release_error"], "the recorded hold keeps its retry instruction inside the 400 characters the record allows")
    fake(issues=[{"number": 12345, "title": "x" * 300}])
    worst = autorelease.release.hold(REPO, "a-long-goal-name-for-the-worst-case", 1)
    check(0 < len(worst) <= 400 and "again" in worst[-250:], "the worst-case hold text (long title, long name) stays within 400 characters and keeps its retry instruction")
    card_held = clock.lead_line(dict(goal("held-card", [("freeze", 3), ("tests", 4)], status="done"), release_error=held_a["release_error"]))
    check(any(x.strip().startswith("release held by main-red (12)") for x in card_held), "a held goal's lead card has one line saying its release is held")
    # the release toys' own gh shim (dev/toy/release-gh.py) answers the hold's questions: none open, or an open issue when TOY_MAIN_RED is set
    shim = os.path.join(TMP, "relshim"); os.makedirs(os.path.join(shim, "gh-state"))
    shutil.copy(os.path.join(HERE, "release-gh.py"), os.path.join(shim, "gh.py"))
    write(os.path.join(shim, "gh"), '#!/bin/bash\nexec python3 "%s/gh.py" "$@"\n' % shim); os.chmod(os.path.join(shim, "gh"), 0o755)
    saved_env = {k: os.environ.get(k) for k in ("PATH", "FAKE_GH_DIR", "TOY_FAKEGH", "TOY_MAIN_RED")}
    os.environ.update(PATH=shim + os.pathsep + os.environ["PATH"], FAKE_GH_DIR=os.path.join(shim, "gh-state"), TOY_FAKEGH=os.path.join(HERE, "fakegh", "gh"))
    os.environ.pop("TOY_MAIN_RED", None)
    quiet = gate.main_red(REPO)
    os.environ["TOY_MAIN_RED"] = "1"
    loud = gate.main_red(REPO)
    for k, v in saved_env.items():
        os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)
    check(quiet == ("none", "") and loud[0] == "open" and loud[1].startswith("77:"), "the release toys' gh shim says no main-red issue by default and an open one when TOY_MAIN_RED is set, so those toys still prove a refusal")
    import io, contextlib, argparse as _ap
    rel = autorelease.release
    kept = {k: getattr(rel, k) for k in ("load", "toplevel", "auto_on", "auto_need", "finished", "save", "read_config", "base_of", "docs_lines", "docs_trouble", "verify_steps", "cmd_cut")}
    saved = []
    batch = {"slug": "batch-a", "status": "done", "batch": True, "pr": "9"}
    rel.load, rel.toplevel, rel.auto_on, rel.auto_need, rel.finished = (lambda slug: batch), (lambda state: REPO), (lambda top: True), (lambda top, state: ("patch", "a test")), (lambda state: None)
    rel.save, rel.read_config, rel.base_of, rel.docs_lines, rel.docs_trouble, rel.verify_steps = (lambda state, note=None: saved.append(note)), (lambda top: {}), (lambda top, cfg: "main"), (lambda *a: []), (lambda *a, **k: []), (lambda *a: "")
    rel.cmd_cut = lambda args: gate.hold(REPO, args.slug)
    fake(issues=[{"number": 12, "title": "t"}])
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        got = rel.cmd_ask(_ap.Namespace(slug="batch-a"))
    for key, value in kept.items():
        setattr(rel, key, value)
    check("MAIN_RED" in out.getvalue() and "The owner decides." in out.getvalue() and batch["release"] == "ask" and batch.get("release_url") is None and got == 0,
          "a batch cut that the hold refuses prints the refusal, releases nothing and waits for the owner")
    fake(issues=[{"number": 12, "title": "t"}])
    try:
        gate.hold(REPO)
        promote = ""
    except SystemExit as stop:
        promote = str(stop)
    check("review.py promote again" in promote and "release.py cut" not in promote, "the promote door's refusal names its own recovery, not the cut's")
    fake(issues=[])
    check(autorelease.release.hold(REPO, "held-a", 1) == "" and autorelease.mergeable(held_a), "once the issue is resolved a rerun of the held goal is not held")
    other_b = {"slug": "other-b", "pr": "8", "release": "merged", "status": "done", "release_bullets": ["goal b work"], "release_steps": "steps of b"}
    check("goal b work" in autorelease.notes_text(other_b) and "goal a work" not in autorelease.notes_text(other_b),
          "another goal's release lists only its own notes, so each held goal is released by its own merge.py run")
    # review finding: a closing reference to ANOTHER repository's issue with the same number does not clear this repository's hold
    fake(issues=[{"number": 12, "title": "t"}], prs=[{"closingIssuesReferences": [{"number": 12, "url": "https://github.com/acme/other/issues/12"}]}])
    check(gate.main_red(REPO) == ("open", "12: t"), "a closing reference to another repository's issue with the same number does not clear the hold")
    fake(issues=[{"number": 12, "title": "t"}], prs=[{"closingIssuesReferences": [{"number": 12}]}])
    check(gate.main_red(REPO)[0] == "open", "a closing reference that names no repository clears nothing")
    fake(issues=[{"number": 12, "title": "t"}], prs=[{"closingIssuesReferences": [{"number": 12, "url": "https://github.com/ACME/Widget/issues/12"}]}])
    check(gate.main_red(REPO) == ("none", ""), "the repository of a closing reference is compared without regard to letter case")
    # review finding: the marker leads the hold text, so a long goal name cannot push it out of the 400 characters release_error keeps
    fake(issues=[{"number": 12345, "title": "x" * 300}])
    long_a = {"slug": "g" * 90, "pr": "9", "release": "merged", "status": "done", "release_bullets": [], "release_steps": ""}
    try:
        autorelease.fail(long_a, gate.hold(REPO, long_a["slug"], 1))
    except SystemExit:
        pass
    held_card = clock.lead_line(dict(goal("long-held", [("freeze", 3)], status="done"), release_error=long_a["release_error"]))
    check("hold=main-red:12345" in long_a["release_error"][:60] and any("release held by main-red (12345)" in x for x in held_card), "with a 90-character goal name the hold marker still survives release_error and the card shows the held line")
    # review finding: the door cells (cut, promote, autorelease) x (hold unreadable, no hold, rerun after the issue is resolved)
    class Past(Exception):
        pass
    def past(*a, **k):
        raise Past()
    rel = autorelease.release
    def refused(call):
        try:
            call()
        except SystemExit as stop:
            return str(stop)
        except Past:
            return "PAST"
        return "RETURNED"
    kept = {k: getattr(rel, k) for k in ("load", "toplevel", "finished", "git")}
    cut_state = {"slug": "cut-x", "status": "done", "pr": "5"}
    rel.load, rel.toplevel, rel.finished, rel.git = (lambda slug: cut_state), (lambda state: REPO), (lambda state: None), past
    cut = lambda: rel.cmd_cut(_ap.Namespace(slug="cut-x", bump="patch", user=False, auto=True))
    fake(mode="fail")
    check("MAIN_RED_UNREADABLE" in refused(cut), "cut: an unreadable issue list refuses through release.cmd_cut before any git call")
    fake(issues=[{"number": 12, "title": "t"}])
    check("MAIN_RED" in refused(cut), "cut: an open issue refuses through release.cmd_cut")
    fake(issues=[])
    check(refused(cut) == "PAST", "cut: once the issue is resolved the same state goes past the hold and on to the branch check")
    for k, v in kept.items():
        setattr(rel, k, v)
    import review as rv
    keep_rv = {k: getattr(rv, k) for k in ("table", "OK", "gate_refusals")}
    rv.table, rv.OK, rv.gate_refusals = (lambda top, name: [["rec", "", "", "", "v9.0.0"]]), (lambda refs, top: False), past
    promote = lambda: rv.promote(REPO, {"base": "main"}, 9, "rec", "ref")
    fake(mode="fail")
    check("MAIN_RED_UNREADABLE" in refused(promote), "promote: an unreadable issue list refuses through review.promote before the gate")
    fake(issues=[])
    check(refused(promote) == "PAST", "promote: once the issue is resolved the same call goes past the hold and on to the gate")
    for k, v in keep_rv.items():
        setattr(rv, k, v)
    keep_ar = autorelease.stage_notes
    autorelease.stage_notes = past
    fin_state = {"slug": "fin-x", "pr": "6", "release": "merged", "status": "done", "release_bullets": ["w"], "release_steps": "s"}
    fake(mode="fail")
    out = refused(lambda: autorelease.finish(REPO, {}, fin_state))
    check("MAIN_RED_UNREADABLE" in fin_state.get("release_error", "") and fin_state["status"] == "done" and out.startswith("REFUSED"), "autorelease: an unreadable issue list is recorded as release_error and the goal stays done and mergeable")
    fake(issues=[])
    check(refused(lambda: autorelease.finish(REPO, {}, fin_state)) == "PAST", "autorelease: once the issue is resolved the same held goal goes past the hold and on to stage its notes")
    autorelease.stage_notes = keep_ar
    # review finding: the measured usual takes the 20 most recent finished goals by completion time, not by file name
    old = [dict(goal("zz-old%d" % i, [("tests", 100)], status="done"), updated=stamp(-100000 + i)) for i in range(20)]
    new = [dict(goal("aa-new%d" % i, [("tests", 10)], status="done"), updated=stamp(-1000 + i)) for i in range(20)]
    check(clock.usual(new + old).get("tests") == 10, "the measured usual comes from the 20 most recent goals by completion time, not from file-name order")
    # review finding: small hardening
    cfg_list = os.path.join(TMP, "listcfg.json")
    write(cfg_list, "[1, 2]")
    got = sh([sys.executable, os.path.join(MON, "clock.py"), "check", cfg_list])
    check("Traceback" not in got.stderr, "a config that is not a JSON object does not make the settings check print a traceback")
    spawned2, real_run2 = [], subprocess.run
    subprocess.run = lambda *a, **k: spawned2.append((a[0], k.get("cwd"))) or real_run2(*a, **k)
    clock.CTX["gh_end"] = time.monotonic() + 10
    bad = [clock.pr_checks({"pr": "--repo=other/repo"}), clock.pr_checks({"pr": "https://example.test/pull/1"})]
    n_bad = len(spawned2)
    clock.CTX["root"] = REPO
    clock.pr_checks({"pr": "7"})
    subprocess.run = real_run2
    check(bad == [None, None] and n_bad == 0 and spawned2 and spawned2[-1][1] == REPO, "a pull request value that is not a number or a github.com pull request URL is never passed to gh, and a good one runs in the board's checkout")
    outside = goal("secret", [("freeze", 3), ("tests", 9)], status="done")
    os.remove(os.path.join(RUNS, "secret.json"))
    write(os.path.join(os.path.dirname(RUNS), "secret.json"), json.dumps(outside))
    clock.CTX.clear()
    clock.begin(REPO)
    check(clock.lead_for("../secret") == [] and clock.lead_for("secret") == [] , "a slug with a path separator reads no run record outside the runs folder (the record one folder up is not read)")
    # moved code is byte for byte what it was
    import ast
    def source(path, name):
        text = open(path).read()
        for node in ast.parse(text).body:
            if isinstance(node, ast.FunctionDef) and node.name == name:
                return "".join(text.splitlines(keepends=True)[node.lineno - 1:node.end_lineno])
    ORIGINAL = {"verify_steps": "87eb149ef4b892ea2fae04ccbb7ce863bef6c0efa6ac3f4a3b88e78017c81fa4", "left_text": "d3b4b312fddb09d8a4fca3443cc5e5a12300ca2f84d09b804b76d1dca7bc460c", "cache_path": "9201520f6d27c3f380fba8e0bc2bb18f319c30c32767bda5ee60071270e3420d"}
    for name, path in (("verify_steps", os.path.join(REL, "gate.py")), ("left_text", os.path.join(REL, "gate.py")), ("cache_path", os.path.join(MON, "clock.py"))):
        check(SHA(source(path, name)) == ORIGINAL[name], "%s moved byte for byte (sha256 matches its text before the move)" % name)
    # every changed caller loads by path from its own skill folder, and the skill subsets stand alone
    sub = []
    for skill, script in (("workflow-release", "release.py"), ("workflow-release", "review.py"), ("workflow-release", "autorelease.py"), ("workflow-setup", "settings.py"),
                          ("workflow-monitoring", "live_board.py"), ("workflow-monitoring", "board_lines.py"), ("workflow-monitoring", "auto.py"), ("workflow-monitoring", "clock.py"),
                          ("workflow-release", "gate.py")):
        code = ("import importlib.util as u,sys;s=u.spec_from_file_location('m',sys.argv[1]);m=u.module_from_spec(s);s.loader.exec_module(m)")
        sdir = os.path.join(SK, skill, "scripts")
        got = subprocess.run([sys.executable, "-c", code, os.path.join(sdir, script)], capture_output=True, text=True, cwd=TMP, env=dict(ENV, PYTHONPATH=sdir + os.pathsep + MON + os.pathsep + REL + os.pathsep + STUB))
        sub.append((script, got.returncode, got.stderr[-120:]))
    check(all(r[1] == 0 for r in sub), "each changed script loads by path from its own folder %s" % [r[0] for r in sub if r[1]])
    only = os.path.join(TMP, "release-only")
    shutil.copytree(os.path.join(SK, "workflow-release"), os.path.join(only, "workflow-release"))
    code = "import sys;sys.path.insert(0,sys.argv[1]);import release,review,autorelease;print(release.hold.__module__, review.left_text.__module__)"
    got = subprocess.run([sys.executable, "-c", code, os.path.join(only, "workflow-release", "scripts")], capture_output=True, text=True, cwd=TMP, env=dict(ENV, PYTHONPATH=""))
    check(got.returncode == 0 and "gate gate" in got.stdout, "the release skill alone (no monitoring skill) still loads and holds %s" % got.stderr[-100:])
    setup_only = os.path.join(TMP, "setup-only")
    shutil.copytree(os.path.join(SK, "workflow-setup"), os.path.join(setup_only, "workflow-setup"))
    cfg2 = write(os.path.join(TMP, "s2", ".loop", "config.json"), json.dumps({"step_report_limits": "tests=banana"}))
    got = subprocess.run([sys.executable, os.path.join(setup_only, "workflow-setup", "scripts", "settings.py"), "fill-repo", "--repo", os.path.join(TMP, "s2")], capture_output=True, text=True, cwd=TMP, env=ENV)
    check(got.returncode != 0 and "Traceback" not in got.stderr, "the setup skill alone refuses a step_report_limits value it cannot check")
    write(os.path.join(TMP, "s2", ".loop", "config.json"), json.dumps({}))
    got = subprocess.run([sys.executable, os.path.join(setup_only, "workflow-setup", "scripts", "settings.py"), "fill-repo", "--repo", os.path.join(TMP, "s2")], capture_output=True, text=True, cwd=TMP, env=ENV)
    check(got.returncode == 0, "the setup skill alone fills settings with no step_report_limits value %s" % got.stderr[-100:])

for group in sorted(COUNT):
    print("%s DEL-%s: %d checks" % ("ALL PASS" if not FAILS.get(group) else "FAILED", group, COUNT[group]))
    if not FAILS.get(group):
        print("ALL PASS %s" % group)
shutil.rmtree(TMP, ignore_errors=True)
sys.exit(1 if FAILS else 0)
