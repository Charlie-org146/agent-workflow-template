#!/usr/bin/env python3
# reads: skills/steps.py skills/workflow-docs/scripts/steps_page.py skills/workflow-delivery/scripts/lanekit.py
# reads: skills/workflow-monitoring/scripts/layers.py skills/workflow-monitoring/scripts/board_page.py skills/workflow-monitoring/scripts/board_log.py
# windows: skip (fcntl)
"""DEL-19 (v110-fast-steps-2), part 2 of 2 (part 1 is test-steps.py): cause keys and fixes, the board's numbers, a goal left unreleased,
the writers scans, a step open across saves, stale copies, layers and lanekit's budget hits. `CASE <name> PASS|FAIL` per case.
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


# 7. causes: only exact keys are read or recorded
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

# 8. the board's own numbers do not move because of the new log lines (N1)
import datetime
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

# 9. a goal left unreleased: its merge ends
left = run_state("release", "done", release="leave", step_clock={"step": "pr", "since": "2026-11-22T10:00:00Z", "active_s": 0})
steps.transition({"step": "release", "status": "done", "release": "leave"}, left, "2026-11-22T10:20:00Z")
waiting = run_state("release", "done", step_clock={"step": "pr", "since": "2026-11-22T10:00:00Z", "active_s": 0})
steps.transition({"step": "release", "status": "done"}, waiting, "2026-11-22T10:20:00Z")
case("merge-ends-for-a-left-goal", any(" end pr:" in l for l in left["log"]) and not any(" end pr:" in l for l in waiting["log"]), str((left["log"], waiting["log"])))

# 10. filing is off; one fix per cause; the one list names the steps in reports
case("filer-writes-nothing", "subprocess.run([\"gh\"" not in text("skills/workflow-docs/scripts/steps_page.py") and "issue" not in text("skills/workflow-docs/scripts/steps_page.py").replace("issues", ""))
case("fix-per-cause", sp.fix_for("merge:failed") != sp.fix_for("merge:HEAD_MOVED") and sp.fix_for("freeze:failed") != sp.fix_for("plan:failed")
     and "(SOME_CODE)" in sp.fix_for("tests:SOME_CODE"), "two causes share a fix")

# 11. a new script that writes JSON must be looked at: every one now writing it is named here (run records go through steps.commit or goal.save)
WRITES = ['audit.py', 'board_lines.py', 'board_model.py', 'controls.py', 'docs.py', 'flow.py', 'govern_hook.py', 'graph.py', 'guards.py', 'lane.py', 'lanekit.py', 'lanes.py', 'layers.py', 'machines.py', 'mailbox.py', 'mend.py', 'monitor.py', 'notify.py', 'replan.py', 'review.py', 'routing.py', 'sessions.py', 'settings.py', 'steps.py', 'sync.py', 'unattended.py', 'update.py', 'workflows.py']
found_writers = sorted({n for dp, _d, fs in os.walk(SKILLS) for n in fs if n.endswith(".py") and "json.dump(" in open(os.path.join(dp, n)).read()})
case("writers-are-all-known", found_writers == WRITES, "new or gone JSON writers: %s" % sorted(set(found_writers) ^ set(WRITES)))

# 12. a record written as write(path, json.dumps(...)) must not appear outside the known non-record files
FORMS = re.compile(r"\bwrite\([^\n]*json\.dumps\(|handle\.write\(json\.dumps\(")
KNOWN_FORMS = ['agents.py', 'auto.py', 'board.py', 'board_page.py', 'board_status.py', 'controls.py', 'defects.py', 'goal.py', 'govern_hook.py', 'lane.py', 'narrow.py', 'operate.py', 'reply_hook.py', 'setup.py', 'slots.py', 'unattended.py']
found_forms = sorted({n for dp, _d, fs in os.walk(SKILLS) for n in fs if n.endswith(".py") and FORMS.search(open(os.path.join(dp, n)).read())})
case("writers-by-dumps-are-known", found_forms == KNOWN_FORMS, "new or gone write(json.dumps) users: %s" % sorted(set(found_forms) ^ set(KNOWN_FORMS)))

# 13. a step stays open across saves until the step changes (autorelease.finish's save order)
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

# 14. a copy loaded before the disk record's last step change cannot move the step or status back
tmps = os.path.join(mk(), "runs", "st.json")
steps.commit(tmps, run_state("build", "running", log=[]), "2026-11-22T10:00:00Z")
stale_copy, fresh = json.load(open(tmps)), json.load(open(tmps))
fresh.update(step="tests")
steps.commit(tmps, fresh, "2026-11-22T10:10:00Z")
stale_copy["note"] = "late"
steps.commit(tmps, stale_copy, "2026-11-22T10:11:00Z")
after = json.load(open(tmps))
case("a-stale-copy-cannot-move-the-step-back", after["step"] == "tests" and after.get("note") == "late", str((after["step"], after.get("note"))))

# 15. layers: a done goal at "after the merge" is a pending merge, not a worker
layers = importlib.import_module("layers")
with tempfile.TemporaryDirectory() as tmp:
    repo = os.path.join(tmp, "r")
    subprocess.run(["git", "init", "-q", "-b", "main", repo], check=True)
    os.makedirs(os.path.join(repo, ".git", "loop", "runs"))
    for slug, step, num in (("late-goal", "after the merge", 3), ("pr-goal", "release", 4)):
        json.dump({"slug": slug, "status": "done", "step": step, "pr": "https://example.test/pull/%d" % num}, open(os.path.join(repo, ".git", "loop", "runs", slug + ".json"), "w"))
    built = layers.build(os.path.join(repo, ".git"), {})
case("layers-list-after-the-merge-as-a-pending-merge", sorted(m["slug"] for m in built["merges"]) == ["late-goal", "pr-goal"] and not built["workers"], str(built["merges"]))

# 16. lanekit.hit saves through the hook, reading inside the lock
lanekit = importlib.import_module("lanekit")
hit_path = os.path.join(mk(), "hk.json")
steps.commit(hit_path, run_state("build", "running", log=["2026-11-22T10:00:00Z first"], slug="hk"), "2026-11-22T10:00:00Z")
lanekit.hit(os.path.dirname(hit_path), "hk", "build", "step", 10, "2m")
hit_rec = json.load(open(hit_path))
case("budget-hit-saves-through-the-hook", hit_rec.get("budget_hits") and any("first" in l for l in hit_rec["log"]) and hit_rec["step_clock"]["since"] > "2026", str(hit_rec.get("step_clock")))

# 17. later saves of a released goal do not start and end release again
later = fin
for at in ("2026-11-22T11:00:00Z", "2026-11-22T12:00:00Z", "2026-11-22T13:00:00Z", "2026-11-22T14:00:00Z"):
    nxt = dict(later, step_clock=dict(later["step_clock"]), note="saved " + at)
    steps.transition(dict(later), nxt, at)
    later = nxt
again = {r["step"]: r for r in steps.entries(later)}["release"]
case("saves-after-the-steps-are-done-add-nothing", again["minutes"] == 4 and again["attempts"] == 1 and sum(1 for l in later["log"] if " end release:" in l) == 1,
     str((again["minutes"], again["attempts"])))

# 18. the stale guard: a legitimate move after another writer's note save is kept; a status move back on the same step is refused
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

# 19. board_page's note and retire commands save through steps.commit, checked per function (red under both reverts)
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

# 20. the board's depth line names the steps of the one list (TD1148): same values show once, differing values are joined with /
live_board = importlib.import_module("live_board")
same = live_board.depth_of({"depth": {"idea": "full", "plan": "full", "review": "full", "qa": "full", "ship": "full"}}, "full")
diff = live_board.depth_of({"depth": {"idea": "full", "plan": "condensed", "review": "full", "qa": "condensed", "ship": "full"}}, "full")
case("depth-line-same-values-show-once", same == "freeze full, plan full, tests full (setting full)", same)
case("depth-line-differing-values-are-joined", diff == "freeze full, plan condensed, tests full/condensed (setting full)", diff)
case("depth-line-has-no-older-names", not re.search(r"\b(idea|review|qa|ship)\b", same + diff), same + " | " + diff)

# 21. a label that is not on the list keeps the last known flow step from the record's own evidence (a fixture of its own)
off = {"slug": "off", "status": "running", "step": "zzz", "worker": "session", "pid": os.getpid(), "updated": "2026-11-22T10:00:00Z",
       "reports": [{"at": "2026-11-22T09:30:00Z", "step": "build", "status": "running", "text": ""}],
       "log": ["2026-11-22T09:00:00Z start idea", "2026-11-22T09:10:00Z idea done", "2026-11-22T09:20:00Z start build"]}
live_board = importlib.import_module("live_board")
moved_mon = importlib.import_module("moved_mon")
off_flow = "\n".join(live_board.flow_lines(off))
case("off-list-label-keeps-the-last-known-step", moved_mon.shown(off, "build")[:2] == ("build", 3) and "[build]" in off_flow and live_board.place(off) == live_board.place(dict(off, step="build")),
     str((moved_mon.shown(off, "build"), off_flow)))
case("off-list-label-break-fixture-is-a-real-label", moved_mon.shown(dict(off, step="checks"), "build")[:2] == ("quick checks", 4))

# 22. the percent bar counts the one list: a goal on quick checks has three of eight steps behind it
case("the-bar-counts-the-one-list", live_board.place(dict(off, step="checks")) == 3 and live_board.place(dict(off, step="review")) == 4 and live_board.place(dict(off, step="release")) == 7,
     str([live_board.place(dict(off, step=x)) for x in ("checks", "review", "release")]))

# 23. a report naming a step by an older label is said with the list's name wherever the board repeats it
said = live_board.next_line(dict(off, step="build", reports=[], report={"at": "2026-11-22T09:50:00Z", "text": "worker off: step ship, running"}))
case("the-next-line-says-the-list-name", "step tests" in said and "step ship" not in said, said)

# 24. the task lines and the handoff draw the list's name only, not the older label beside it
tasks_src, board_src2 = text("skills/workflow-monitoring/scripts/board_tasks.py"), text("skills/workflow-monitoring/scripts/board.py")
case("task-lines-draw-only-the-list-name", "moved_mon.shown(r, FLOW[current(r)])[0]" in tasks_src and ".label(" not in tasks_src)
case("the-handoff-draws-only-the-list-name", 'r["shown"]' in board_src2 and ".label(" not in board_src2)

# 25. a status-only save by another writer does not make a later legitimate step move look stale
sp2 = os.path.join(mk(), "runs", "sm.json")
steps.commit(sp2, run_state("tests", "running", slug="sm"), "2026-11-22T10:00:00Z")
a_copy, b_copy = json.load(open(sp2)), json.load(open(sp2))
b_copy["status"] = "waiting"
steps.commit(sp2, b_copy, "2026-11-22T10:01:00Z")
a_copy["step"] = "pr"
steps.commit(sp2, a_copy, "2026-11-22T10:02:00Z")
sm = json.load(open(sp2))
case("a-step-move-after-a-status-only-save-sticks", sm["step"] == "pr" and sm["status"] == "waiting", str((sm["step"], sm["status"])))

# 26. the per-function scan refuses a direct write beside the commit call
extra = board_src.replace('moved_mon.steps().commit(path, run, run["updated"])\n    print("NOTED', 'moved_mon.steps().commit(path, run, run["updated"])\n    open(path, "w").write("x")\n    print("NOTED', 1)
case("a-direct-write-beside-the-commit-is-caught", extra != board_src and not commits(extra, "cmd_note"))

# what say() reads and leaves alone, and where goal.py names the step
case("say-leaves-other-text-alone", [steps.say(t) for t in ("plan-review step", "next step review the diff", "review: approve?", "step pr-check failed", "pre-step ship, x", None, 3)]
     == ["plan-review step", "next step review the diff", "review: approve?", "step pr-check failed", "pre-step ship, x", None, 3], "")
src = open(os.path.join(SKILLS, "workflow-delivery", "scripts", "goal.py")).read()  # goal.py names the step where it writes the ask and the note
case("goal-names-the-step-at-the-source", "name_of(step), took[:240]" in src and 'name_of(step), "; ".join(pending)' in src
     and all("name_of(step)" in l for l in src.splitlines() if any(k in l for k in ("wasn't run by flow.py", "has no STEP line", "gave no STEP line"))), "")
case("say-reads-the-written-asks", steps.say("review left this for you: x") == "tests left this for you: x" and steps.say("auto-approved at qa: y") == "auto-approved at tests: y", "")

print("ALL PASS" if not failed else "FAILED: %s" % ", ".join(failed))
sys.exit(1 if failed else 0)
