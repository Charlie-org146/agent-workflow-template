#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-monitoring/scripts/machines.py skills/workflow-monitoring/scripts/graph.py skills/workflow-monitoring/scripts/checkin.py
"""machine-coordination (#4787): a goal owned by one machine moves to the other with a handover, nothing runs twice, the repo has
one merge turn across both machines, and the Machine lines of a check-in come from published structured SNAPSHOTs.
Two toy clones of one bare origin stand for the PC and the Mac. No network, no model."""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
MON = os.path.join(HERE, "..", "..", "skills", "workflow-monitoring", "scripts")
MACHINES = os.path.join(MON, "machines.py")
sys.path.insert(0, MON)
FAILS = []


def check(name, ok):
    print(("PASS: " if ok else "FAIL: ") + name)
    if not ok:
        FAILS.append(name)


def git(cwd, *args):
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    return subprocess.run(["git", "-c", "commit.gpgsign=false"] + list(args), cwd=cwd, env=env, capture_output=True, text=True)


def env_of(machine):
    env = dict(os.environ, LOOP_FLOW=os.path.join(TMP, "flow.json"), LOOP_MACHINE_NAME=machine, LOOP_MACHINE="9,9,10,1,1", HOME=TMP, USERPROFILE=TMP)
    for name in ("LOOP_ROLE", "LOOP_POD_ID", "CLAUDE_SESSION_ID", "LOOP_SESSION_TOOL"):
        env.pop(name, None)
    return env


def run(cwd, machine, *args):
    done = subprocess.run([sys.executable, MACHINES] + list(args), cwd=cwd, env=env_of(machine), capture_output=True, text=True)
    return done.returncode, done.stdout + done.stderr


with tempfile.TemporaryDirectory() as TMP:
    TMP = os.path.realpath(TMP)
    origin, pc, mac = (os.path.join(TMP, n) for n in ("origin.git", "pc", "mac"))
    git(TMP, "init", "-q", "--bare", "-b", "main", origin)
    git(TMP, "clone", "-q", origin, pc)
    git(pc, "checkout", "-q", "-b", "main")
    os.makedirs(os.path.join(pc, ".loop"))
    with open(os.path.join(pc, ".loop", "config.json"), "w") as f:
        json.dump({"base": "main", "agent_command": [sys.executable, "-c", "pass"]}, f)
    git(pc, "add", "-A")
    git(pc, "commit", "-q", "-m", "init")
    git(pc, "push", "-q", "origin", "main")
    tree = os.path.join(pc, ".git", "loop", "worktrees", "g1")
    git(pc, "worktree", "add", "-q", "-b", "loop/g1", tree)
    with open(os.path.join(tree, "work.txt"), "w") as f:
        f.write("progress\n")
    git(tree, "add", "-A")
    git(tree, "commit", "-q", "-m", "work")
    runs = os.path.join(pc, ".git", "loop", "runs")
    os.makedirs(runs)
    state = {"slug": "g1", "goal": "toy", "status": "queued", "step": "plan", "worktree": tree, "branch": "loop/g1", "log": [],
             "worker": "", "session": None, "pid": None}
    with open(os.path.join(runs, "g1.json"), "w") as f:
        json.dump(state, f)
    git(TMP, "clone", "-q", origin, mac)

    code, out = run(pc, "pc", "handover", "g1", "--to", "mac")
    check("a handover pushes the branch and the record", code == 0 and "HANDED OVER g1 to mac" in out)
    old = json.load(open(os.path.join(runs, "g1.json")))
    check("the old machine marks it moved, with no worker", old["status"] == "moved" and old["moved_to"] == "mac" and not old["pid"] and not old["session"])
    code, out = run(pc, "pc", "take", "g1")
    check("a handover the machine made to the other is refused here", code != 0)
    code, out = run(mac, "mac", "take", "g1")
    new = json.load(open(os.path.join(mac, ".git", "loop", "runs", "g1.json")))
    check("the new machine binds a worker on the pushed branch", code == 0 and "TAKEN g1: worker background" in out and new["machine"] == "mac"
          and new["status"] == "running" and os.path.exists(os.path.join(new["worktree"], "work.txt")))
    code, out = run(mac, "mac", "take", "g1")
    check("it never runs twice: a second take is refused", code != 0 and "never runs on two machines" in out)
    code, out = run(pc, "pc", "handover", "g1", "--to", "mac")
    check("a moved goal can't be handed over again from the old machine", code != 0)

    import machines
    FLOW = os.path.join(TMP, "flow.json")
    os.environ["LOOP_FLOW"] = FLOW
    with open(FLOW, "w") as f:
        json.dump({}, f)
    os.chdir(pc)
    os.environ.update(LOOP_MACHINE_NAME="pc")
    check("with machine_sync off nothing is pushed and the turn is never held",
          machines.turn("turn", runs, "g1") == "" and not git(pc, "ls-remote", "origin", "refs/loop/pr-turn").stdout.strip()
          and machines.lines(pc, {}, "Machine: x") == ["Machine: x"])
    with open(FLOW, "w") as f:
        json.dump({"machine_sync": True}, f)
    os.chdir(pc)
    os.environ.update(LOOP_MACHINE_NAME="pc")
    check("the first goal takes the merge turn", machines.turn("turn", runs, "g1") == "")
    os.chdir(mac)
    os.environ.update(LOOP_MACHINE_NAME="mac")
    check("a merge on the other machine waits for the pr turn", machines.turn("turn", runs, "g2") == "g1 on pc")
    os.chdir(pc)
    os.environ.update(LOOP_MACHINE_NAME="pc")
    machines.turn("free", runs, "g1")
    os.chdir(mac)
    os.environ.update(LOOP_MACHINE_NAME="mac")
    check("it goes on once the turn is freed", machines.turn("turn", runs, "g2") == "")
    machines.turn("free", runs, "g2")
    os.environ["LOOP_MERGE_LOCK_SECONDS"] = "0"
    os.chdir(pc)
    os.environ.update(LOOP_MACHINE_NAME="pc")
    machines.turn("turn", runs, "g1")
    os.chdir(mac)
    os.environ.update(LOOP_MACHINE_NAME="mac")
    check("a silent holder's turn is dropped", machines.turn("turn", runs, "g2") == "")
    os.environ.pop("LOOP_MERGE_LOCK_SECONDS")

    for where, name in ((pc, "pc"), (mac, "mac")):
        run(where, name, "snapshot", "--publish")
    code, out = run(mac, "mac", "snapshot")
    snap = json.loads(out)
    check("the SNAPSHOT is structured data", snap["machine"] == "mac" and snap["goals"][0]["slug"] == "g1" and "line" in snap)
    os.chdir(pc)
    os.environ.update(LOOP_MACHINE_NAME="pc")
    shown = machines.lines(pc, {}, "Machine: RAM 9.0 GB free")
    check("a check-in draws both Machine lines from the SNAPSHOTs", len(shown) == 2 and shown[1].startswith("Machine mac (") and "1 goal: g1" in shown[1])
    mine = [g for g in json.loads(run(pc, "pc", "snapshot")[1])["goals"] if g["status"] in ("running", "waiting", "queued")]
    check("the goal shows once, under the Mac", not mine)
    os.chdir(TMP)
    check("with no origin a check-in keeps its one Machine line", machines.lines(TMP, {}, "Machine: x") == ["Machine: x"])

if FAILS:
    print("FAILED %d" % len(FAILS))
    sys.exit(1)
print("OK")
