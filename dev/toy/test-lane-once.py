#!/usr/bin/env python3
# reads: skills/workflow-delivery/scripts/lane.py skills/workflow-delivery/scripts/lanekit.py
# reads: skills/workflow-delivery/scripts/role.py
"""lane-once (#5734, Reviewed DEL-17): one test lane per goal head; its pass satisfies the qa, ship and pr steps.

Done 1: a pass by one lane at HEAD answers the other two with no lane started; any move of HEAD needs a new lane.
Done 2: the one lane is the qa lane's own record (rows and all) and the three names run one argv.
Done 3: a failed lane, a pass at another head, a dirty tree and a head mismatch are refused as before.
The fixture is a throwaway git repo with hand-written lane records; lane.prep is a stub that counts starts, so no
regression row runs. usage: test-lane-once.py (env LANE_ONCE_SCRIPTS names another copy of the delivery scripts)."""
import inspect
import json
import os
import shutil
import subprocess
import sys
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


def git(*args):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid"] + list(args), cwd=repo,
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


def record(name, head, state="pass", line=QA, ok=True, **extra):
    with open(base(name) + ".last", "w") as handle:
        json.dump(dict({"attempt": "a-" + name, "head": head, "state": state, "line": line}, **extra), handle)
    with open(base(name) + ".txt", "w") as handle:
        handle.write(ROWS)
    if ok:
        with open(base(name) + ".ok", "w") as handle:
            handle.write(head)


def ask(name):
    return lane.lane(runs, SLUG, name, {}, cfg, 0)


def gate(step, text="STEP: done\n"):
    reply = os.path.join(tmp, "reply.txt")
    open(reply, "w").write(text)
    return role.need_lane(runs, SLUG, reply, step)


def sibling_job(name, head):
    """A live job of lane `name` at `head`, owned by this process."""
    rc = "%s.job.rc" % base(name)
    held = {"head": head, "attempt": "job", "started": time.time(), "limit": 600, "rc": rc, "pool": tmp, "markers": 1,
            "pid": os.getpid(), "pstart": lanekit.pstart(os.getpid())}
    with open(base(name) + ".job", "w") as handle:
        json.dump(held, handle)


head1 = git("rev-parse", "HEAD")

# Done 1: one pass answers all three
record("qa", head1)
got = {name: ask(name) for name in ("ship", "pr")}
check(all(got[n][0] == "pass" for n in got) and not starts, "a qa pass at HEAD answers ship and pr with no lane started")
check(all(os.path.exists(base(n) + ".ok") and open(base(n) + ".ok").read() == head1 and not os.path.exists(base(n) + ".job") for n in got),
      "each copy writes its own .ok (HEAD) and leaves no job")
check(got["ship"][1].count("; reused:") == 1 and "the qa lane passed on this head" in got["ship"][1].split("\n")[0],
      "the reuse is said once on the line: reused: the qa lane passed on this head")
check(gate("ship") is None, "need_lane accepts ship after a qa-only pass")
check(open(base("ship") + ".txt").read() == ROWS and json.load(open(base("ship") + ".last"))["reused_from"] == "qa",
      "the copy carries the qa lane's rows and says where it came from (Done 2: the qa lane's own record)")
check(role.lane_note(runs, SLUG, "ship") == "2 pass; 1 not runnable here", "lane_note keeps the not-runnable note on the reused pass")
check("SELECTED r1" in role.lane_part(SLUG) and "; reused: the qa lane" in role.lane_part(SLUG), "the PR body's lane part shows the rows and the reuse")
check(lane.lane_status(runs, SLUG, "ship")[0] == "pass" and subprocess.run(
    [sys.executable, os.path.join(scripts, "role.py"), "lane-wait", SLUG, "ship"], cwd=repo, capture_output=True, text=True,
    env=dict(os.environ, LOOP_ROLE="worker")).returncode in (0, 3), "lane_status and lane-wait read the same pass")
# a chain: ship holds a copy, qa's own record is gone: pr copies the copy and still names qa once
clear()
record("qa", head1)
ask("ship")
os.remove(base("qa") + ".ok")
pr_line = ask("pr")[1]
check(pr_line.count("; reused:") == 1 and "the qa lane" in pr_line, "a copy of a copy names the lane that ran, once")

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

# A copy cut short is finished, never taken for complete
clear()
record("qa", head2)
shutil.copy(base("qa") + ".last", base("ship") + ".last")
check(lanekit.passed(runs, SLUG, head2, "ship") == "qa", "a .last pass with no .ok is an incomplete alias: the pass is qa's")
check(ask("ship")[0] == "pass" and os.path.exists(base("ship") + ".ok") and os.path.exists(base("ship") + ".txt"), "the next call finishes the copy")
clear()
record("qa", head2)
os.makedirs(base("ship") + ".txt")
broken = ask("ship")
check(broken[0] == "fail" and broken[1].startswith("LANE_REUSE_COPY") and "no .ok was written" in broken[1] and not os.path.exists(base("ship") + ".ok"),
      "an unwritable target: LANE_REUSE_COPY and no .ok")
# a fail at this head is kept when a pass answers it
clear()
record("qa", head2)
record("ship", head2, state="fail", line="LANE ship FAILED", ok=False)
check(ask("ship")[0] == "pass" and os.path.exists(base("ship") + ".last.prev") and lane.lane_status(runs, SLUG, "ship")[0] == "pass",
      "a pass beats an own fail at one head, and the fail is kept as .last.prev")

# lane and lane_status agree over the same states
clear()
record("qa", head2)
sibling_job("ship", head2)
a, b = ask("pr"), lane.lane_status(runs, SLUG, "pr")
check(a[0] == b[0] == "running", "a live sibling job at this head: both say running")
os.remove(base("ship") + ".job")
check(ask("pr")[0] == lane.lane_status(runs, SLUG, "pr")[0] == "pass", "no job left: both say pass")

# the three names run one argv
check(list(inspect.signature(lane.lane_argv).parameters) == ["seconds"] and inspect.getsource(lane.lane).count("lane_argv(") == 1,
      "the lane command comes from lane_argv alone, which takes no lane name")
check(lane.NAMES == lanekit.LANES == ("qa", "ship", "pr"), "one list of lane names")

# Control (d): the same steps against a copy whose passed() answers only its own name must fail the happy case
if not os.environ.get("LANE_ONCE_SCRIPTS"):
    cut = os.path.join(tmp, "cut")
    shutil.copytree(scripts, cut, ignore=shutil.ignore_patterns("__pycache__"))
    text = open(os.path.join(cut, "lanekit.py")).read()
    old = 'if (last.get("head"), last.get("state")) == (head, "pass") and'
    open(os.path.join(cut, "lanekit.py"), "w").write(text.replace(old, 'if n == name and (last.get("head"), last.get("state")) == (head, "pass") and'))
    check(old in text and open(os.path.join(cut, "lanekit.py")).read() != text, "the control's cut changed the file")
    done = subprocess.run([sys.executable, os.path.abspath(__file__)], capture_output=True, text=True, env=dict(os.environ, LANE_ONCE_SCRIPTS=cut))
    said = done.stdout + done.stderr
    check(done.returncode == 1 and "FAIL: a qa pass at HEAD answers ship and pr with no lane started" in said and "Traceback" not in said,
          "negative control: with reuse cut to the own name, ship starts its own lane and the happy case fails")

shutil.rmtree(tmp, ignore_errors=True)
print("ALL PASS" if not failed else "%d FAILED" % len(failed))
sys.exit(1 if failed else 0)
