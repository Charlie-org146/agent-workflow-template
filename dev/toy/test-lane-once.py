#!/usr/bin/env python3
# reads: skills/workflow-delivery/scripts/lane.py skills/workflow-delivery/scripts/lanekit.py
# reads: skills/workflow-delivery/scripts/role.py skills/workflow-regression/scripts/lanes_cli.py
"""lane-once (#5734, Reviewed DEL-17): one test lane per goal head; its pass satisfies the qa, ship and pr steps.

Done 1: a pass by one lane at HEAD answers the other two with no lane started and no file written; any move of HEAD
        needs a new lane; `--fresh` forces a lane through the tool.
Done 2: the rows a lane selects for a diff are the same as the base branch's (lanes_cli.py affected, both trees).
Done 3: a failed lane, a pass at another head, a dirty tree and a head mismatch are refused as before.
The fixture is a throwaway git repo with hand-written lane records; lane.prep is a stub that counts starts, so no
regression row runs. usage: test-lane-once.py (env LANE_ONCE_SCRIPTS names another copy of the delivery scripts)."""
import inspect
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
scripts = os.environ.get("LANE_ONCE_SCRIPTS") or os.path.join(root, "skills", "workflow-delivery", "scripts")
sys.path.insert(0, scripts)
sys.dont_write_bytecode = True
import lane  # noqa: E402
import lanekit  # noqa: E402
import role  # noqa: E402

failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


tmp = tempfile.mkdtemp(prefix="lane-once-")
home = os.path.join(tmp, "home")
os.makedirs(home)
os.environ.update(HOME=home, USERPROFILE=home, GIT_TERMINAL_PROMPT="0")
for var in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "_LOOP_LANE_HELD"):
    os.environ.pop(var, None)
repo = os.path.join(tmp, "repo")
os.makedirs(os.path.join(repo, ".loop"))
os.chdir(repo)


def git(*args, cwd=None):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid"] + list(args), cwd=cwd or repo,
                          capture_output=True, text=True).stdout.strip()


with open(os.path.join(repo, ".loop", "config.json"), "w") as handle:
    json.dump({"min_free_memory_gb": 0, "base": "main"}, handle)
git("init", "-q", "-b", "main")
git("add", "-A")
git("commit", "-qm", "one")
runs = os.path.join(repo, ".git", "loop", "runs")
os.makedirs(runs)
cfg = json.load(open(os.path.join(repo, ".loop", "config.json")))
starts = []
lane.prep = lambda top, c, out: (starts.append(out) or ("", "TOY_STOP: the lane would start here"))
SLUG = "g"
QA = "LANE qa AFFECTED 3/3 in 5s; 2 pass; 1 not runnable here (a)"
ROWS = "SELECTED r1: reaches x\nSELECTED r2: reaches y\n"


def base(name):
    return lanekit.lane_base(runs, SLUG, name)


def clear():
    for name in os.listdir(runs):
        path = os.path.join(runs, name)
        shutil.rmtree(path) if os.path.isdir(path) else os.remove(path)
    del starts[:]


def record(name, head, state="pass", line=QA, ok=True):
    with open(base(name) + ".last", "w") as handle:
        json.dump({"attempt": "a-" + name, "head": head, "state": state, "line": line, "ended": time.time()}, handle)
    with open(base(name) + ".txt", "w") as handle:
        handle.write(ROWS)
    if ok:
        with open(base(name) + ".ok", "w") as handle:
            handle.write(head)


def ask(name, fresh=False):
    return lane.lane(runs, SLUG, name, {}, cfg, 0, redo=fresh)


def gate(step):
    reply = os.path.join(tmp, "reply.txt")
    open(reply, "w").write("STEP: done\n")
    return role.need_lane(runs, SLUG, reply, step)


def sibling_job(name, head):
    """A live job of lane `name` at `head`, owned by this process."""
    held = {"head": head, "attempt": "job", "started": time.time(), "limit": 600, "rc": "%s.job.rc" % base(name), "pool": tmp,
            "markers": 1, "pid": os.getpid(), "pstart": lanekit.pstart(os.getpid())}
    with open(base(name) + ".job", "w") as handle:
        json.dump(held, handle)


head1 = git("rev-parse", "HEAD")

# Done 1: one pass answers all three, and nothing is written
record("qa", head1)
before = sorted(os.listdir(runs))
got = {name: ask(name) for name in ("ship", "pr")}
check(all(got[n][0] == "pass" for n in got) and not starts, "a qa pass at HEAD answers ship and pr with no lane started")
check(sorted(os.listdir(runs)) == before, "the answer writes no file: no .ok, .last, .txt or job for ship or pr")
check(got["ship"][1].count("; reused:") == 1 and "the qa lane passed on this head" in got["ship"][1].split("\n")[0],
      "the answer says once, on its first line, that the qa lane passed on this head")
if os.environ.get("LANE_ONCE_SCRIPTS"):  # the control run: only the happy case matters
    shutil.rmtree(tmp, ignore_errors=True)
    sys.exit(1 if failed else 0)
check(gate("ship") is None, "need_lane accepts ship after a qa-only pass")
check(role.lane_note(runs, SLUG, "ship") == "2 pass; 1 not runnable here", "lane_note reads the not-runnable note from qa's record")
part = role.lane_part(SLUG)
check("SELECTED r1" in part and "(qa lane ended " in part, "the PR body's lane part shows qa's rows and names the lane and when it ended")
check(lane.lane_status(runs, SLUG, "ship")[0] == "pass", "lane_status gives the same pass")
waited = subprocess.run([sys.executable, os.path.join(scripts, "role.py"), "lane-wait", SLUG, "ship"], cwd=repo, capture_output=True,
                        text=True, env=dict(os.environ, LOOP_ROLE="worker"))
check(waited.returncode == 0 and "reused: the qa lane" in waited.stdout, "lane-wait ship exits 0 with the same reused pass (%s)" % waited.returncode)

# pr lane wins over an older qa record in the PR body, and only a pass at HEAD is shown
record("pr", head1, line="LANE pr AFFECTED 1/1 in 3s")
check("LANE pr AFFECTED" in role.lane_part(SLUG) and "(qa lane" not in role.lane_part(SLUG), "a pr lane that passed at HEAD is the one the PR body shows")

# Done 1/3: HEAD moves
clear()
record("qa", head1)
open(os.path.join(repo, "x.txt"), "w").write("x")
git("add", "-A")
git("commit", "-qm", "two")
head2 = git("rev-parse", "HEAD")
status = ask("ship")
check(status[0] == "fail" and "TOY_STOP" in status[1] and len(starts) == 1, "negative control: HEAD moved, ship starts its own lane")
refusal = gate("ship")
check(refusal is not None and refusal[2] == "HEAD_MOVED" and "HEAD moved since the qa lane passed (lane on %s, HEAD %s)" % (head1[:12], head2[:12]) in refusal[0],
      "HEAD_MOVED names the lane that passed and both heads")
check("SELECTED" not in role.lane_part(SLUG) or head1 == head2, "the PR body shows no pass from an older head")
clear()
check(gate("ship")[2] == "LANE_MISSING", "no lane ever passed: LANE_MISSING")

# Done 3: failed lane, other head, dirty tree
record("qa", head2, state="fail", ok=False)
check(ask("ship")[0] == "fail" and len(starts) == 1 and gate("ship")[2] == "LANE_MISSING", "negative control: a failed qa lane gives ship no pass")
clear()
record("qa", head1)
check(ask("pr")[0] == "fail" and len(starts) == 1, "negative control: a pass at another head is never reused")
clear()
record("qa", head2)
open(os.path.join(repo, "dirty.txt"), "w").write("d")
check(ask("ship")[0] == "fail" and len(starts) == 1 and gate("ship") is None, "a dirty tree gets no reuse in lane(); need_lane is unchanged (today's behavior)")
check(lane.lane_status(runs, SLUG, "ship")[0] != "pass", "lane_status agrees: no pass on a dirty tree")
os.remove(os.path.join(repo, "dirty.txt"))

# a record is a pass only when .last and .ok both say so; the own lane's older record still counts, as today
clear()
record("qa", head2, ok=False)
check(lanekit.passed(runs, SLUG, head2, "ship") == "" and ask("ship")[0] == "fail" and len(starts) == 1, "a .last pass with no .ok on another lane is no pass")
clear()
record("ship", head2, ok=False)
check(ask("ship")[0] == "pass" and not starts, "the own lane's earlier .last pass, with no .ok, still answers as before this change")

# lane and lane_status agree over the same states
clear()
record("qa", head2)
record("ship", head2, state="fail", line="LANE ship FAILED", ok=False)
check(ask("ship")[0] == lane.lane_status(runs, SLUG, "ship")[0] == "pass", "own fail plus a sibling pass: both say pass")
clear()
record("qa", head2)
sibling_job("ship", head2)
check(ask("pr")[0] == lane.lane_status(runs, SLUG, "pr")[0] == "running", "a live sibling job at this head: both say running")
os.remove(base("ship") + ".job")
check(ask("pr")[0] == lane.lane_status(runs, SLUG, "pr")[0] == "pass", "no job left: both say pass")

# --fresh: the tool removes the three .ok files and starts a lane; a live job blocks it
clear()
record("qa", head2)
fresh = ask("ship", fresh=True)
check(fresh[0] == "fail" and "TOY_STOP" in fresh[1] and len(starts) == 1 and not os.path.exists(base("qa") + ".ok") and not os.path.exists(base("qa") + ".last") and gate("ship")[2] == "LANE_MISSING",
      "--fresh removes the passes and records and starts a lane; the gate then waits for that lane's own pass")
clear()
record("qa", head2)
sibling_job("pr", head2)
blocked = ask("ship", fresh=True)
check(blocked[0] == "fail" and blocked[1].startswith("LANE_FRESH") and os.path.exists(base("qa") + ".ok") and not starts, "--fresh while a lane runs refuses and removes nothing")
os.remove(base("pr") + ".job")

# a dead job with no exit status is cleared and a new lane starts (the crashed-job path)
clear()
with open(base("ship") + ".job", "w") as handle:
    json.dump({"head": head2, "attempt": "dead", "started": time.time() - 100, "limit": 600, "rc": base("ship") + ".dead.rc", "pool": tmp,
               "markers": 1, "pid": 999999, "pstart": ""}, handle)
check(ask("ship")[0] == "fail" and len(starts) == 1, "a dead job record is cleared and the lane starts (no crash on the stale-job path)")

# the three names run one argv
check(list(inspect.signature(lane.lane_argv).parameters) == ["seconds"] and inspect.getsource(lane.lane).count("lane_argv(") == 1,
      "the lane command comes from lane_argv alone, which takes no lane name")
check(lane.NAMES == lanekit.LANES == ("qa", "ship", "pr"), "one list of lane names")

# Done 2, as a test: the rows a diff selects are the base branch's rows (lanes_cli.py affected, both trees)
base_ref = next((r for r in ("origin/main", "main") if git("rev-parse", "--verify", "-q", r, cwd=root)), "")
if not base_ref:
    check(False, "the base ref (origin/main or main) is missing in this checkout. Fix: fetch it, then run this toy again")
else:
    changed = git("diff", "--name-only", git("merge-base", base_ref, "HEAD", cwd=root), cwd=root).split()
    changed = [p for p in changed if not p.startswith(".loop/goals/")] or ["skills/workflow-delivery/scripts/lane.py"]
    old = os.path.join(tmp, "base-tree")
    os.makedirs(old)
    archive = subprocess.run(["git", "archive", base_ref, "skills/workflow-regression"], cwd=root, capture_output=True).stdout
    open(os.path.join(tmp, "base.tar"), "wb").write(archive)
    tarfile.open(os.path.join(tmp, "base.tar")).extractall(old)

    def selected(tree):
        done = subprocess.run([sys.executable, os.path.join(tree, "skills", "workflow-regression", "scripts", "lanes_cli.py"), "affected", "--root", root, "--level", "all"] + changed,
                              capture_output=True, text=True, env=dict(os.environ, LOOP_ROLE="worker"))
        return done.returncode, [x for x in done.stdout.splitlines() if x.startswith(("AFFECTED", "ALWAYS"))]
    new_rows, base_rows = selected(root), selected(old)
    check(new_rows == base_rows and new_rows[0] == 0 and len(new_rows[1]) > 0,
          "the rows selected for this diff are identical to the base branch's (%d lines, base %s)" % (len(new_rows[1]), base_ref))

# Control (g): the same steps against a copy whose passed() answers only the own lane must fail the happy case
cut = os.path.join(tmp, "cut")
shutil.copytree(scripts, cut, ignore=shutil.ignore_patterns("__pycache__"))
text = open(os.path.join(cut, "lanekit.py")).read()
old = " for n in done if lane_ok("
if old not in text:
    check(False, "the control cannot cut passed(): its text changed. Fix: update this control")
else:
    open(os.path.join(cut, "lanekit.py"), "w").write(text.replace(old, " for n in done if n == name and lane_ok(", 1))
    done = subprocess.run([sys.executable, os.path.abspath(__file__)], capture_output=True, text=True, env=dict(os.environ, LANE_ONCE_SCRIPTS=cut))
    said = done.stdout + done.stderr
    check(done.returncode == 1 and "FAIL: a qa pass at HEAD answers ship and pr with no lane started" in said and "Traceback" not in said,
          "negative control: with reuse cut to the own lane, a lane would start and the happy case fails")

shutil.rmtree(tmp, ignore_errors=True)
print("ALL PASS" if not failed else "%d FAILED" % len(failed))
sys.exit(1 if failed else 0)
