#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-delivery/scripts/decisions.py skills/workflow-delivery/scripts/goal.py skills/workflow-monitoring/scripts/graph.py
"""One review (DLF-1.3), decisions after the start: the ledger is a file of its own that is only added to, writers of the
run record cannot lose an entry, a missing or torn ledger refuses, and a permanent stop holds at every change into
queued or running. Throwaway folders with their own home; no network."""
import json
import os
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
delivery = os.path.join(root, "skills", "workflow-delivery", "scripts")
monitoring = os.path.join(root, "skills", "workflow-monitoring", "scripts")
sys.path[:0] = [delivery, monitoring]
home = tempfile.mkdtemp()
os.environ.update(HOME=home, USERPROFILE=home, GIT_CONFIG_NOSYSTEM="1")
tmp = os.path.join(home, "repo")
runs = os.path.join(tmp, ".git", "loop", "runs")
subprocess.run(["git", "init", "-q", tmp], check=True)
subprocess.run(["git", "-C", tmp, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "base"], check=True)
os.makedirs(runs)
os.makedirs(os.path.join(tmp, ".loop", "goals"))

failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


try:
    import decisions
except ImportError as error:
    print("FAIL: decisions.py is missing: %s" % error)
    sys.exit(1)


def record(slug, **more):
    state = dict({"slug": slug, "goal": slug, "status": "running", "step": "build", "tries": 0, "flow": {}, "branch": "loop/" + slug,
                  "worktree": tmp, "touches": [], "log": []}, **more)
    json.dump(state, open(os.path.join(runs, slug + ".json"), "w"))
    return state


def refused(call):
    try:
        call()
    except SystemExit as stop:
        return str(stop.code)
    return ""


# the ledger: its own file, numbered, only added to
record("a", one_review={"at": "t"})
decisions.create(runs, "a", by="test")
first = decisions.add(runs, "a", "decision", question="q1", taken="x")
second = decisions.add(runs, "a", "decision", question="q2", taken="y")
check([first, second] == [2, 3] and [e["n"] for e in decisions.entries(runs, "a")] == [1, 2, 3], "entries are numbered in order")
check(refused(lambda: decisions.create(runs, "a", by="test")) != "", "a ledger is made once and never made again over another")

# many writers at once lose nothing and share no number
child = ("import sys; sys.path.insert(0, %r); import decisions\n"
         "for i in range(20): decisions.add(%r, 'a', 'decision', question='%%s-%%d' %% (sys.argv[1], i), taken='x')" % (delivery, runs))
procs = [subprocess.Popen([sys.executable, "-c", child, str(k)]) for k in range(4)]
codes = [p.wait() for p in procs]
got = [e["n"] for e in decisions.entries(runs, "a")]
check(codes == [0] * 4 and got == list(range(1, 84)), "80 concurrent entries are all kept with unique numbers (%d entries)" % len(got))

# a writer of the whole run record cannot lose an entry
import goal  # noqa: E402
os.chdir(tmp)
stale = goal.load("a")
decisions.add(runs, "a", "decision", question="added while another writer holds the record", taken="x")
goal.save(stale, "a stale writer saves")
check(len(decisions.entries(runs, "a")) == 84, "a stale whole-record save keeps every entry")

# a missing or torn ledger refuses
record("gone", one_review={"at": "t"})
said = refused(lambda: decisions.require(runs, {"slug": "gone", "one_review": {"at": "t"}}))
check("decisions" in said, "a marked goal with no ledger is refused: %s" % said[:80])
decisions.create(runs, "torn", by="test")
open(decisions.ledger(runs, "torn"), "a").write('{"n": 2, "kind"')
check(refused(lambda: decisions.entries(runs, "torn")) != "", "a torn ledger is refused, not read as shorter")
check(refused(lambda: decisions.require(runs, {"slug": "plain"})) == "", "an unmarked goal needs no ledger")

# a permanent stop holds at every change into queued or running
record("s", one_review={"at": "t"}, status="stopped")
decisions.create(runs, "s", by="test")
decisions.stop(runs, "s", "a done line needs the part", by="operation")
for status in ("queued", "running", "waiting"):
    state = goal.load("s")
    state["status"] = status
    said = refused(lambda: goal.save(state, "set " + status))
    check("stopped for good" in said and json.load(open(os.path.join(runs, "s.json")))["status"] == "stopped",
          "goal.py cannot set a stopped goal %s: %s" % (status, said[:70]))
import sessions  # noqa: E402
import watch  # noqa: E402
import worker  # noqa: E402
import mend  # noqa: E402
sys.path.append(os.path.join(root, "skills", "workflow-release", "scripts"))
import release  # noqa: E402
for module in (sessions, watch, worker, mend, release):
    state = dict(json.load(open(os.path.join(runs, "s.json"))), status="queued" if module is watch else "running")
    said = refused(lambda m=module, s=state: m.save(s, "revive"))
    check("stopped for good" in said and json.load(open(os.path.join(runs, "s.json")))["status"] == "stopped",
          "%s.py cannot revive it: %s" % (module.__name__, said[:60]))
state = goal.load("s")
state["status"] = "retired"
check(refused(lambda: goal.save(state, "retired")) == "", "it can still be retired")

# the stop also holds when a writer has lost the mark from the record
lost = {k: v for k, v in json.load(open(os.path.join(runs, "s.json"))).items() if k != "one_review"}
lost["status"] = "running"
check("stopped for good" in refused(lambda: goal.save(lost, "revive")), "a record without the mark is still held by its ledger")

# a handover carries the ledger and the pre-flight and review files
os.makedirs(os.path.join(tmp, ".git", "loop", "redteam"), exist_ok=True)
open(os.path.join(runs, "a.extra.json"), "w").write('{"touches": ["x"]}')
open(os.path.join(tmp, ".git", "loop", "redteam", "plan-a.json"), "w").write('{"breaks": []}')
bundle = decisions.pack(runs, json.load(open(os.path.join(runs, "a.json"))))
there = os.path.join(home, "other", "loop", "runs")
decisions.unpack(there, {"slug": "a", "one_review": {"at": "t"}}, bundle)
check(len(decisions.entries(there, "a")) == 84 and os.path.exists(os.path.join(there, "a.extra.json"))
      and os.path.exists(os.path.join(there, "..", "redteam", "plan-a.json")), "a handover carries the decisions, pre-flight and review files")
said = refused(lambda: decisions.unpack(os.path.join(home, "third", "loop", "runs"), {"slug": "a", "one_review": {"at": "t"}}, {}))
check("carries no decisions" in said, "a marked goal handed over without its ledger is refused: %s" % said[:80])
open(os.path.join(there, "a.decisions.jsonl"), "a").write('{"n": 85, "kind": "decision"}\n')
check("don't continue" in refused(lambda: decisions.unpack(there, {"slug": "a", "one_review": {"at": "t"}}, bundle)),
      "an older copy never replaces a longer ledger")

# an unmarked goal saves as today
record("u", status="stopped")
state = goal.load("u")
state["status"] = "running"
check(refused(lambda: goal.save(state, "resumed")) == "", "an unmarked goal is not held")

print("ALL PASS" if not failed else "%d FAILED" % len(failed))
sys.exit(1 if failed else 0)
