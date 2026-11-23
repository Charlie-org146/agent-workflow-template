#!/usr/bin/env python3
# reads: skills/steps.py skills/workflow-docs/scripts/steps_page.py skills/workflow-delivery/scripts/lanekit.py
# reads: skills/workflow-monitoring/scripts/layers.py skills/workflow-monitoring/scripts/board_page.py skills/workflow-monitoring/scripts/board_log.py
# windows: skip (fcntl)
"""DEL-19 (v110-fast-steps-2), part 2 of 2 (part 1 is test-steps.py): cause keys and fixes, the board's numbers, a goal left unreleased,
the writers scans, open steps, stale copies, layers, budget hits, the end lines. `CASE <name> PASS|FAIL` per case.
usage: test-steps-more.py"""
import ast
import datetime
import importlib
import json
import os
import re
import subprocess
import sys
sys.dont_write_bytecode = True  # the shared file lives under skills/, where a cache folder would fail the package check
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
SKILLS = os.path.join(ROOT, "skills")
sys.path[:0] = [SKILLS, os.path.join(SKILLS, "workflow-delivery", "scripts"), os.path.join(SKILLS, "workflow-monitoring", "scripts"),
                os.path.join(SKILLS, "workflow-docs", "scripts")]
steps, board_log, lanekit, sp = (importlib.import_module(n) for n in ("steps", "board_log", "lanekit", "steps_page"))
import atexit
import shutil

_made = []


def mk():
    """A temp folder this toy makes; it is removed when the toy exits (absolute path, under the system temp root only)."""
    path = tempfile.mkdtemp()
    _made.append(path)
    return path


@atexit.register
def _clean():
    for path in _made:
        if os.path.isabs(path) and path.startswith(os.path.realpath(tempfile.gettempdir())) or path.startswith(tempfile.gettempdir()):
            shutil.rmtree(path, ignore_errors=True)


failed = []


def case(name, ok, why=""):
    print("CASE %s %s%s" % (name, "PASS" if ok else "FAIL", "" if ok else ": " + why))
    ok or failed.append(name)


def text(rel):
    return open(os.path.join(ROOT, rel)).read()


def run_state(step, status, log=None, **more):
    return dict({"slug": "t", "step": step, "status": status, "log": list(log or [])}, **more)


case("cause-key-shape", steps.KEY.match("merge:HEAD_MOVED") and not steps.KEY.match("../x:failed") and not steps.KEY.match("merge:lower"))
case("cause-off-list-step-is-freeze", steps.add_cause(c1 := {}, "zzz", "boom (SOME_CODE)") and c1["causes"][0]["key"] == "freeze:SOME_CODE" and steps.add_cause(c2 := {}, "-", "") and c2["causes"][0]["key"] == "freeze:failed" and steps.add_cause({}, "pr", "boom (SOME_CODE)"))
st = {"slug": "c", "step": "build", "status": "running", "log": []}
tmpc = os.path.join(mk(), "runs", "c.json")
steps.commit(tmpc, st, "2026-11-22T10:00:00Z")
stale = json.load(open(tmpc))
later = json.load(open(tmpc))
later.update(status="done")
steps.commit(tmpc, later, "2026-11-22T10:05:00Z")
stale["status"] = "running"
steps.commit(tmpc, stale, "2026-11-22T10:06:00Z")
case("commit-stale-copy-keeps-disk-clock", sum(1 for l in json.load(open(tmpc))["log"] if " end build:" in l) == 1, str(json.load(open(tmpc))["log"]))

base_log = ["2026-11-22T10:00:00Z start idea", "2026-11-22T10:10:00Z idea done", "2026-11-22T10:20:00Z start plan", "2026-11-22T10:30:00Z plan done",
            "2026-11-22T10:40:00Z session report: worker · x: held at build", "2026-11-22T11:10:00Z resumed", "2026-11-22T11:20:00Z start build"]
extra_log = []
for line in base_log:
    extra_log.append(line)
    if line.endswith("idea done"):
        extra_log.append("2026-11-22T10:10:00Z end idea: 10m active, tokens not reported, done")
    if line.endswith("held at build"):
        extra_log.append("2026-11-22T10:40:00Z began plan")
at = datetime.datetime(2026, 11, 22, 12, 0, tzinfo=datetime.timezone.utc)
board_before = board_log.flow_seconds({"log": base_log, "status": "running", "step": "build"}, at)
board_after = board_log.flow_seconds({"log": extra_log, "status": "running", "step": "build"}, at)
case("board-numbers-unchanged", board_before == board_after and bool(board_before), "%s != %s" % (board_before, board_after))

left = run_state("release", "done", release="leave", step_clock={"step": "pr", "since": "2026-11-22T10:00:00Z", "active_s": 0})
steps.transition({"step": "release", "status": "done", "release": "leave"}, left, "2026-11-22T10:20:00Z")
waiting = run_state("release", "done", step_clock={"step": "pr", "since": "2026-11-22T10:00:00Z", "active_s": 0})
steps.transition({"step": "release", "status": "done"}, waiting, "2026-11-22T10:20:00Z")
case("merge-ends-for-a-left-goal", any(" end pr:" in l for l in left["log"]) and not any(" end pr:" in l for l in waiting["log"]), str((left["log"], waiting["log"])))

case("filer-writes-nothing", "subprocess.run([\"gh\"" not in text("skills/workflow-docs/scripts/steps_page.py") and "issue" not in text("skills/workflow-docs/scripts/steps_page.py").replace("issues", ""))
case("fix-per-cause", sp.fix_for("merge:failed") != sp.fix_for("merge:HEAD_MOVED") and sp.fix_for("freeze:failed") != sp.fix_for("plan:failed")
     and "(SOME_CODE)" in sp.fix_for("tests:SOME_CODE"), "two causes share a fix")

WRITES = ['audit.py', 'board_lines.py', 'board_model.py', 'controls.py', 'docs.py', 'flow.py', 'govern_hook.py', 'graph.py', 'guards.py', 'lane.py', 'lanekit.py', 'lanes.py', 'layers.py', 'machines.py', 'mailbox.py', 'mend.py', 'monitor.py', 'notify.py', 'replan.py', 'review.py', 'routing.py', 'sessions.py', 'settings.py', 'steps.py', 'sync.py', 'unattended.py', 'update.py', 'workflows.py']
found_writers = sorted({n for dp, _d, fs in os.walk(SKILLS) for n in fs if n.endswith(".py") and "json.dump(" in open(os.path.join(dp, n)).read()})
case("writers-are-all-known", found_writers == WRITES, "new or gone JSON writers: %s" % sorted(set(found_writers) ^ set(WRITES)))

FORMS = re.compile(r"\bwrite\([^\n]*json\.dumps\(|handle\.write\(json\.dumps\(")
KNOWN_FORMS = ['agents.py', 'auto.py', 'board.py', 'board_page.py', 'board_status.py', 'controls.py', 'defects.py', 'goal.py', 'govern_hook.py', 'lane.py', 'narrow.py', 'operate.py', 'reply_hook.py', 'setup.py', 'slots.py', 'unattended.py']
found_forms = sorted({n for dp, _d, fs in os.walk(SKILLS) for n in fs if n.endswith(".py") and FORMS.search(open(os.path.join(dp, n)).read())})
case("writers-by-dumps-are-known", found_forms == KNOWN_FORMS, "new or gone write(json.dumps) users: %s" % sorted(set(found_forms) ^ set(KNOWN_FORMS)))

seq = run_state("after the merge", "done", log=["2026-11-22T10:00:00Z began after the merge"], release="cut")
seq["step_clock"] = {"step": "after the merge", "since": "2026-11-22T10:00:00Z", "active_s": 0}
prev = dict(seq, step_clock=dict(seq["step_clock"]))
for at in ("2026-11-22T10:05:00Z", "2026-11-22T10:10:00Z"):
    cur = dict(prev, step_clock=dict(prev["step_clock"]))
    steps.transition(dict(prev), cur, at)
    prev = cur
cur = dict(prev, step="release", step_clock=dict(prev["step_clock"]))
steps.transition(dict(prev), cur, "2026-11-22T10:16:00Z")
fin = dict(cur, steps_done=True, step_clock=dict(cur["step_clock"]))
steps.transition(dict(cur), fin, "2026-11-22T10:20:00Z")
rows_seq = {r["step"]: r for r in steps.entries(fin)}
case("a-step-stays-open-across-saves", rows_seq["after the merge"]["minutes"] == 16 and rows_seq["after the merge"]["attempts"] == 1 and rows_seq["release"]["minutes"] == 4,
     str({k: (v["minutes"], v["attempts"]) for k, v in rows_seq.items() if v["state"] != "not run"}))

tmps = os.path.join(mk(), "runs", "st.json")
steps.commit(tmps, run_state("build", "running", log=[]), "2026-11-22T10:00:00Z")
stale_copy, fresh = json.load(open(tmps)), json.load(open(tmps))
fresh.update(step="tests")
steps.commit(tmps, fresh, "2026-11-22T10:10:00Z")
stale_copy["note"] = "late"
steps.commit(tmps, stale_copy, "2026-11-22T10:11:00Z")
after = json.load(open(tmps))
case("a-stale-copy-cannot-move-the-step-back", after["step"] == "tests" and after.get("note") == "late", str((after["step"], after.get("note"))))

layers = importlib.import_module("layers")
with tempfile.TemporaryDirectory() as tmp:
    repo = os.path.join(tmp, "r")
    subprocess.run(["git", "init", "-q", "-b", "main", repo], check=True)
    os.makedirs(os.path.join(repo, ".git", "loop", "runs"))
    for slug, step, num in (("late-goal", "after the merge", 3), ("pr-goal", "release", 4)):
        json.dump({"slug": slug, "status": "done", "step": step, "pr": "https://example.test/pull/%d" % num}, open(os.path.join(repo, ".git", "loop", "runs", slug + ".json"), "w"))
    built = layers.build(os.path.join(repo, ".git"), {})
case("layers-list-after-the-merge-as-a-pending-merge", sorted(m["slug"] for m in built["merges"]) == ["late-goal", "pr-goal"] and not built["workers"], str(built["merges"]))

lanekit = importlib.import_module("lanekit")
hit_path = os.path.join(mk(), "hk.json")
steps.commit(hit_path, run_state("build", "running", log=["2026-11-22T10:00:00Z first"], slug="hk"), "2026-11-22T10:00:00Z")
lanekit.hit(os.path.dirname(hit_path), "hk", "build", "step", 10, "2m")
hit_rec = json.load(open(hit_path))
case("budget-hit-saves-through-the-hook", hit_rec.get("budget_hits") and any("first" in l for l in hit_rec["log"]) and hit_rec["step_clock"]["since"] > "2026", str(hit_rec.get("step_clock")))

later = fin
for at in ("2026-11-22T11:00:00Z", "2026-11-22T12:00:00Z", "2026-11-22T13:00:00Z", "2026-11-22T14:00:00Z"):
    nxt = dict(later, step_clock=dict(later["step_clock"]), note="saved " + at)
    steps.transition(dict(later), nxt, at)
    later = nxt
again = {r["step"]: r for r in steps.entries(later)}["release"]
case("saves-after-the-steps-are-done-add-nothing", again["minutes"] == 4 and again["attempts"] == 1 and sum(1 for l in later["log"] if " end release:" in l) == 1,
     str((again["minutes"], again["attempts"])))

gp = os.path.join(mk(), "runs", "g.json")
steps.commit(gp, run_state("build", "running"), "2026-11-22T10:00:00Z")
mine, theirs = json.load(open(gp)), json.load(open(gp))
theirs["note"] = "someone else saved a note"
steps.commit(gp, theirs, "2026-11-22T10:01:00Z")
mine.update(step="tests")
steps.commit(gp, mine, "2026-11-22T10:02:00Z")
case("a-legitimate-move-after-another-save-is-kept", json.load(open(gp))["step"] == "tests" and steps.entries(json.load(open(gp)))[2]["state"] != "not run", str(json.load(open(gp))["step"]))
loaded = json.load(open(gp))
stopper = json.load(open(gp))
stopper.update(status="stopped", finding="boom (SOME_CODE)")
steps.commit(gp, stopper, "2026-11-22T10:03:00Z")
loaded["note"] = "late note"
steps.commit(gp, loaded, "2026-11-22T10:04:00Z")
case("a-status-move-back-on-the-same-step-is-refused", json.load(open(gp))["status"] == "stopped" and sum(1 for l in json.load(open(gp))["log"] if " began tests" in l) == 1,
     str((json.load(open(gp))["status"], [l for l in json.load(open(gp))["log"] if "began" in l])))

def commits(src, fn):
    node = next(n for n in ast.walk(ast.parse(src)) if isinstance(n, ast.FunctionDef) and n.name == fn)
    calls = [c for c in ast.walk(node) if isinstance(c, ast.Call)]
    saves = any(isinstance(c.func, ast.Attribute) and c.func.attr == "commit" for c in calls)
    writes = any((isinstance(c.func, ast.Name) and c.func.id in ("write", "open")) or (isinstance(c.func, ast.Attribute) and c.func.attr in ("write", "dump", "replace")) for c in calls)
    return saves and not writes


board_src = text("skills/workflow-monitoring/scripts/board_page.py")
rev1 = board_src.replace('moved_mon.steps().commit(path, run, run["updated"])\n    print("NOTED', 'write(path, json.dumps(run, indent=2))\n    print("NOTED', 1)
rev2 = board_src.replace('moved_mon.steps().commit(path, run, run["updated"])\n    print("NOTED', 'open(path, "w").write(json.dumps(run))\n    print("NOTED', 1)
rev3 = board_src.replace('moved_mon.steps().commit(path, run, run["updated"])\n    print("RETIRED', 'write(path, json.dumps(run, indent=2))\n    print("RETIRED', 1)
case("note-and-retire-save-through-the-hook", commits(board_src, "cmd_note") and commits(board_src, "cmd_retire"))
case("note-reverted-to-write-is-caught", rev1 != board_src and not commits(rev1, "cmd_note"))
case("note-reverted-to-open-write-is-caught", rev2 != board_src and not commits(rev2, "cmd_note"))
case("retire-reverted-to-write-is-caught", rev3 != board_src and not commits(rev3, "cmd_retire"))

live_board = importlib.import_module("live_board")
same = live_board.depth_of({"depth": {"idea": "full", "plan": "full", "review": "full", "qa": "full", "ship": "full"}}, "full")
diff = live_board.depth_of({"depth": {"idea": "full", "plan": "condensed", "review": "full", "qa": "condensed", "ship": "full"}}, "full")
case("depth-line-same-values-show-once", same == "freeze full, plan full, tests full (setting full)", same)
case("depth-line-differing-values-are-joined", diff == "freeze full, plan condensed, tests full/condensed (setting full)", diff)
case("depth-line-has-no-older-names", not re.search(r"\b(idea|review|qa|ship)\b", same + diff), same + " | " + diff)

off = {"slug": "off", "status": "running", "step": "zzz", "worker": "session", "pid": os.getpid(), "updated": "2026-11-22T10:00:00Z",
       "reports": [{"at": "2026-11-22T09:30:00Z", "step": "build", "status": "running", "text": ""}],
       "log": ["2026-11-22T09:00:00Z start idea", "2026-11-22T09:10:00Z idea done", "2026-11-22T09:20:00Z start build"]}
live_board = importlib.import_module("live_board")
moved_mon = importlib.import_module("moved_mon")
off_flow = "\n".join(live_board.flow_lines(off))
case("off-list-label-keeps-the-last-known-step", moved_mon.shown(off, "build")[:2] == ("build", 3) and "[build]" in off_flow and live_board.place(off) == live_board.place(dict(off, step="build")),
     str((moved_mon.shown(off, "build"), off_flow)))
case("off-list-label-break-fixture-is-a-real-label", moved_mon.shown(dict(off, step="checks"), "build")[:2] == ("quick checks", 4))

case("the-bar-counts-the-one-list", live_board.place(dict(off, step="checks")) == 3 and live_board.place(dict(off, step="review")) == 4 and live_board.place(dict(off, step="release")) == 7,
     str([live_board.place(dict(off, step=x)) for x in ("checks", "review", "release")]))

said = live_board.next_line(dict(off, step="build", reports=[], report={"at": "2026-11-22T09:50:00Z", "text": "worker off: step ship, running"}))
case("the-next-line-says-the-list-name", "step tests" in said and "step ship" not in said, said)

tasks_src, board_src2 = text("skills/workflow-monitoring/scripts/board_tasks.py"), text("skills/workflow-monitoring/scripts/board.py")
case("task-lines-draw-only-the-list-name", "moved_mon.shown(r, FLOW[current(r)])[0]" in tasks_src and ".label(" not in tasks_src)
case("the-handoff-draws-only-the-list-name", 'r["shown"]' in board_src2 and ".label(" not in board_src2)

sp2 = os.path.join(mk(), "runs", "sm.json")
steps.commit(sp2, run_state("tests", "running", slug="sm"), "2026-11-22T10:00:00Z")
a_copy, b_copy = json.load(open(sp2)), json.load(open(sp2))
b_copy["status"] = "waiting"
steps.commit(sp2, b_copy, "2026-11-22T10:01:00Z")
a_copy["step"] = "pr"
steps.commit(sp2, a_copy, "2026-11-22T10:02:00Z")
sm = json.load(open(sp2))
case("a-step-move-after-a-status-only-save-sticks", sm["step"] == "pr" and sm["status"] == "waiting", str((sm["step"], sm["status"])))

extra = board_src.replace('moved_mon.steps().commit(path, run, run["updated"])\n    print("NOTED', 'moved_mon.steps().commit(path, run, run["updated"])\n    open(path, "w").write("x")\n    print("NOTED', 1)
case("a-direct-write-beside-the-commit-is-caught", extra != board_src and not commits(extra, "cmd_note"))

case("say-leaves-other-text-alone", [steps.say(t) for t in ("plan-review step", "next step review the diff", "pre-step ship, x", "step pr-check failed", "a review step of the draft", "can't merge: required checks failed: build", "review: 3 findings", "pr: #12 merged", "the review lane is busy", "the review reply came late", None, 3)]
     == ["plan-review step", "next step review the diff", "pre-step ship, x", "step pr-check failed", "a review step of the draft", "can't merge: required checks failed: build", "review: 3 findings", "pr: #12 merged", "the review lane is busy", "the review reply came late", None, 3], "")
case("say-reads-the-written-asks", [steps.say(t) for t in ("review left this for you: x", "auto-approved at qa: y", "10 refused records in a row: idea refused: no DEPTH line", "qa: 2 refusals", "review: full_markers for review in the flow file is not a list", "a full_markers string for qa is missing", "10 records: review wasn't run by flow.py", "the qa lane has not passed", "the ship reply has no STEP line", "HEAD moved since the qa lane passed", "the review step ran condensed", "review failed: boom", "idea gave no STEP line")]
     == ["tests left this for you: x", "auto-approved at tests: y", "10 refused records in a row: freeze refused: no DEPTH line", "tests: 2 refusals", "tests: full_markers for tests in the flow file is not a list", "a full_markers string for tests is missing", "10 records: tests wasn't run by flow.py", "the tests lane has not passed", "the tests reply has no STEP line", "HEAD moved since the tests lane passed", "the tests step ran condensed", "tests failed: boom", "freeze gave no STEP line"], "")

rec = {"log": ["2026-11-22T10:00:00Z start freeze", "2026-11-22T10:05:00Z end freeze: 5m active, tokens 1, done", "2026-11-22T10:05:00Z start plan",
               "2026-11-22T10:35:00Z end plan: 30m active, tokens 2, done"], "step": "plan", "status": "running"}
lines = steps.summary(rec).splitlines()
case("summary-lists-the-worst-step-first", lines[0] == "### Steps" and lines[2].startswith("- plan: 30m") and lines[3].startswith("- freeze: 5m"), str(lines))
cs = {}
case("a-cause-is-recorded-once", steps.add_cause(cs, "qa", "x (REFUSED_X)") and not steps.add_cause(cs, "ship", "y (REFUSED_X)") and len(cs["causes"]) == 1, str(cs))

two = {"log": ["T1 began build", "T2 end build: 5m active, tokens 10, moved on", "T3 began build", "T4 end build: 7m active, tokens not reported, done"]}
b2 = [r for r in steps.entries(two) if r["step"] == "build"][0]
case("entries-add-attempts-keep-first-start-and-last-tokens", (b2["minutes"], b2["tokens"], b2["start"], b2["attempts"]) == (12, "10", "T1", 2), str(b2))
again = {"step": "build", "status": "running", "steps_done": True, "log": []}
steps.transition({"step": "build", "status": "done"}, again, "2026-11-22T10:00:00Z")
case("a-goal-that-runs-again-has-steps-again", "steps_done" not in again, str(again))
rel = {"step": "release", "status": "done"}
case("an-unpushed-release-is-the-merge", steps.eff(dict(rel, release_pushed=True)) == "release" and steps.eff(dict(rel, release="leave")) is None and steps.eff(rel) == "pr" and steps.eff(dict(rel, release="cut")) == "release", "")

def move(status, used, end):
    run = {"step": "build", "status": "running", "tokens": {"a": 100}, "log": []}
    steps.transition({}, run, "2026-11-22T10:00:00Z")
    old = json.loads(json.dumps(run))
    run.update(step="tests", status=status, tokens={"a": 100 + used})
    steps.transition(old, run, end)
    return run
ended = {st: next(l for l in move(st, 300, "2026-11-22T11:00:01Z")["log"] if " end build:" in l) for st in ("running", "done", "stopped", "failed")}
case("transition-writes-the-result-word", [ended[k].rsplit(", ", 1)[1] for k in ("running", "done", "stopped", "failed")] == ["moved on", "done", "stopped", "failed"], str(ended))
case("transition-writes-whole-minutes-and-the-tokens-used", "60m active, tokens 300," in ended["done"] and "tokens not reported" in next(l for l in move("running", 0, "2026-11-22T10:05:00Z")["log"] if " end build:" in l), str(ended))
two = move("running", 300, "2026-11-22T11:00:01Z")
nxt = json.loads(json.dumps(two))
two["step"] = "merge"
steps.transition(nxt, two, "2026-11-22T11:04:00Z")
case("a-new-step-starts-its-clock-again", any(" end tests: 3m active" in l for l in two["log"]), str(two["log"]))
pth = os.path.join(tempfile.mkdtemp(), "r.json")
steps.commit(pth, {"step": "build", "status": "running", "log": []}, "2026-11-22T10:00:00Z")
case("update-ends-the-step-it-leaves", steps.update(pth, lambda r: r.update(step="tests"), "2026-11-22T10:10:00Z") and any(" end build:" in l for l in json.load(open(pth))["log"]) and json.load(open(pth))["step_clock"]["mark"] == 2 and steps.update(pth + "x", lambda r: None) is False, "")

print("ALL PASS" if not failed else "FAILED: %s" % ", ".join(failed))
sys.exit(1 if failed else 0)
