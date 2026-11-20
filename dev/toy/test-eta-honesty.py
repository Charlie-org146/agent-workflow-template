#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-monitoring/scripts/board_status.py skills/workflow-monitoring/scripts/auto.py skills/workflow-monitoring/scripts/layers.py skills/workflow-health/scripts/rules.py skills/workflow-health/scripts/controls.py skills/workflow-health/scripts/report.py
"""eta-honesty (principle 8, DEL-17, HLT-4): every ETA a goal, the board or a STATUS states is recorded with who, when, basis and the time it
names; when that time passes without the event it is marked missed with a cause and the board shows it; health prints each layer's hit rate and
fails on an ETA over 15 minutes past that is neither met nor marked; a missed ETA or a statement marked wrong becomes a finding row.
A throwaway git repo and stand-in ledger lines: no network. usage: test-eta-honesty.py [ledger|health]  (no argument: both)"""
import datetime
import json
import os
import subprocess
import sys
import tempfile
import time

here = os.path.dirname(os.path.abspath(__file__))
top = os.path.join(here, "..", "..")
MON = os.path.join(top, "skills", "workflow-monitoring", "scripts")
HEALTH = os.path.join(top, "skills", "workflow-health", "scripts")
sys.path[:0] = [HEALTH, MON]
os.environ["LOOP_ROLE"] = "worker"
only = sys.argv[1] if len(sys.argv) > 1 else ""
if not only:  # each part in its own process: they import the same module names from two skills
    code = 0
    for part in ("ledger", "health"):
        done = subprocess.run([sys.executable, os.path.abspath(__file__), part], capture_output=True, text=True)
        print("".join(line + chr(10) for line in done.stdout.splitlines() if line.startswith(("PASS", "FAIL"))), end="")
        code = code or done.returncode
    sys.exit(code)
failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


tmp = tempfile.mkdtemp(prefix="eta-honesty-")
repo = os.path.join(tmp, "repo")
os.makedirs(repo)
subprocess.run(["git", "init", "-q", "-b", "main", repo], check=True)
os.makedirs(os.path.join(repo, ".git", "loop", "runs"))
os.chdir(repo)
loop = os.path.join(repo, ".git", "loop")
NOW = time.time()


def hours(n):
    return NOW + n * 3600


if only == "ledger":
    import auto
    import board_status as bs
    import layers

    # Value: protects=a stated ETA keeps who, when, basis and the time it names (done line 1); fails_when=eta_say drops a field or does not record
    bs.eta_say(loop, "goal", "g1", "worker one", "estimate 60m plus 25%", hours(1), NOW)
    mine = [e for e in bs.eta_fold(loop).values() if e["key"] == "g1"]
    check(len(mine) == 1 and all(mine[0].get(k) for k in ("who", "said", "basis", "names", "layer")), "a stated ETA is recorded with who, when, basis and the time it names")
    bs.eta_say(loop, "goal", "g1", "worker one", "estimate 60m plus 25%", hours(1) + 300, NOW)
    check(len(bs.eta_fold(loop)) == 1, "the same ETA stated again within 15 minutes adds nothing")
    check(auto.eta_settle(loop, {}, NOW + 60) == [], "an ETA whose time has not come stays open")
    # Value: protects=a passed ETA with no event is marked missed with a cause, and a met ETA is not (the negative control); fails_when=settle marks a met ETA missed or leaves a missed one open
    bs.eta_say(loop, "goal", "late", "worker two", "guess", NOW - 7200, NOW - 10000)
    bs.eta_say(loop, "goal", "ok", "worker three", "guess", NOW - 7200, NOW - 10000)
    done = {e["key"]: e for e in auto.eta_settle(loop, {("goal", "ok"): NOW - 7300}, NOW)}
    check(done["late"]["state"] == "missed" and "no event by" in done["late"]["cause"], "a passed ETA with no event is marked missed with a cause (%s)" % done["late"].get("cause"))
    check(done["ok"]["state"] == "met" and not done["ok"].get("cause"), "negative control: an ETA whose event came in time is marked met, with no cause")
    bs.eta_say(loop, "goal", "slow", "worker four", "guess", NOW - 7200, NOW - 10000)
    slow = auto.eta_settle(loop, {("goal", "slow"): NOW - 3600}, NOW)
    check(slow and slow[0]["state"] == "missed" and "after" in slow[0]["cause"], "an event that came after the time named is missed, not met")
    bs.eta_say(loop, "goal", "g1", "worker one", "moved", hours(3), NOW)
    old = [e for e in bs.eta_fold(loop).values() if e["key"] == "g1" and e["names"] == hours(1)]
    check(old and old[0]["state"] == "missed" and "restated" in old[0]["cause"], "a restated ETA marks the earlier one missed")
    # the board shows a missed ETA, not hides it
    bs.eta_say(loop, "board", "v9", "check-in", "latest finish", NOW - 7200, NOW - 10000, ["a"])
    auto.eta_settle(loop, {}, NOW)
    head = bs.release_header("v9", [{"slug": "a", "left": 3600, "mark": "running"}], datetime.datetime.now(datetime.timezone.utc))
    check("MISSED" in head and "earlier ETA" in head, "the board's release header shows the missed ETA (%s)" % head)
    clean = bs.release_header("v8", [{"slug": "a", "left": 3600, "mark": "running"}], datetime.datetime.now(datetime.timezone.utc))
    check("MISSED" not in clean and any(e["key"] == "v8" and e["layer"] == "board" for e in bs.eta_fold(loop).values()), "negative control: a release with no missed ETA shows none, and its ETA is recorded")
    # the sweep: a goal that finished by its ETA is met
    bs.eta_say(loop, "goal", "fin", "worker five", "guess", hours(1), NOW)
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(NOW + 600))
    with open(os.path.join(loop, "runs", "fin.json"), "w") as handle:
        json.dump({"slug": "fin", "status": "done", "step": "release", "updated": stamp}, handle)
    swept = layers.eta_sweep(os.path.join(repo, ".git"), NOW + 900)
    check(any(e["key"] == "fin" and e["state"] == "met" for e in swept), "the sweep marks a goal that finished before its ETA met")

if only == "health":
    import rules

    def ledger(*entries):
        base = {"id": "", "layer": "goal", "key": "x", "who": "w", "said": 1, "basis": "b", "names": 1, "state": "open", "goals": []}
        with open(os.path.join(loop, "etas.jsonl"), "w") as handle:
            for i, entry in enumerate(entries):
                handle.write(json.dumps(dict(base, id="e%d" % i, **entry)) + "\n")

    def rows(rule):
        return rules.GUARD_FUNCTIONS[rule](repo)

    # Value: protects=an ETA over 15 minutes past that is neither met nor marked fails health (done line 2); fails_when=eta-unmarked stays quiet or fires on a marked ETA
    ledger({"names": NOW - 1200})
    found = rows("eta-unmarked")
    check(len(found) == 1 and found[0]["state"] == "FAIL", "an ETA 20 minutes past, neither met nor marked, fails health")
    ledger({"names": NOW - 1200, "state": "met", "settled": NOW}, {"names": NOW - 1200, "state": "missed", "settled": NOW, "cause": "no event"}, {"names": NOW - 300})
    check(rows("eta-unmarked") == [], "negative control: every past ETA met or marked (and one only 5 minutes past) passes")
    ledger(*[{"layer": "goal", "state": "met" if i < 3 else "missed", "settled": i} for i in range(6)], {"layer": "board", "state": "met", "settled": 9})
    rate = rows("eta-rate")
    text = " | ".join(r["detail"] for r in rate)
    check("goal ETAs: 3 of the last 6 met" in text and "board ETAs: 1 of the last 1 met" in text and "status ETAs: 0 of the last 0 met" in text, "health prints each layer's hit rate (%s)" % text)
    ledger(*[{"layer": "goal", "state": "met", "settled": i} for i in range(6)])
    check(all(r["state"] == "INFO" for r in rows("eta-rate")), "negative control: every ETA met prints the rate and warns about nothing")
    ledger(*[{"layer": "goal", "state": "missed", "settled": i} for i in range(6)])
    check(any(r["state"] == "WARN" for r in rows("eta-rate")), "a layer that met under half its last 20 ETAs warns")
    # Value: protects=a missed ETA and a statement marked wrong become finding rows with the goal and the cause (done line 3); fails_when=either is not reported
    ledger({"key": "goal-a", "state": "missed", "settled": NOW, "names": NOW - 100, "cause": "no event by 10:00 (the goal is at qa, running)"})
    found = rows("eta-missed")
    check(len(found) == 1 and found[0]["subject"] == "goal-a" and "no event by 10:00" in found[0]["detail"], "a missed ETA is a finding row naming the goal and the cause")
    ledger({"key": "goal-a", "state": "met", "settled": NOW})
    check(rows("eta-missed") == [], "negative control: a met ETA is no finding")
    with open(os.path.join(loop, "runs", "w.json"), "w") as handle:
        json.dump({"slug": "w", "status": "running", "wrong": [{"said": "merged by 5", "why": "it was still in review"}]}, handle)
    found = rows("statement-wrong")
    check(len(found) == 1 and found[0]["subject"] == "w" and "still in review" in found[0]["detail"], "a statement marked wrong in a run record is a finding row with its cause")
    os.remove(os.path.join(loop, "runs", "w.json"))
    check(rows("statement-wrong") == [], "negative control: a run record with no wrong statement is no finding")

sys.exit(1 if failed else 0)
