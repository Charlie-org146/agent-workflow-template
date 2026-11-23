#!/usr/bin/env python3
# reads: skills/workflow-delivery/scripts/skip.py skills/workflow-delivery/scripts/lane.py skills/workflow-delivery/scripts/fit.py
"""local-lane (DEL-25.3): no local full lane while GitHub runs the tests.

Done: with regression-pr.yml in the repo and GitHub answering, a goal's lane is recorded `skipped` (never pass, never .ok): pr goes on with a
SKIPPED first line (the PR body prints it), qa and ship wait (running, LANE_WAITING) until every GitHub check run on the head is green and
only then count it. Controls: GitHub not answering, LOOP_LANE_LOCAL=1, no workflow file, a dirty tree and a lane already running each run
the lane (or refuse) exactly as before, and a lane that was never a skip is refused as before. The probe and the checks are stubs here;
skip.probe and skip.checks run against a fake gh on a POSIX machine.
Needs fcntl (lane.py does): Mac, Linux and CI. usage: test-local-lane.py"""
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import time

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
scripts = os.path.join(root, "skills", "workflow-delivery", "scripts")
sys.path.insert(0, scripts)
sys.dont_write_bytecode = True
try:
    import lane  # noqa: E402
except ImportError as err:
    print("SKIP: lane.py needs fcntl (%s); this toy runs on Mac, Linux and CI" % err)
    sys.exit(0)
import lanekit  # noqa: E402
import role  # noqa: E402
import skip  # noqa: E402

failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


tmp = tempfile.mkdtemp(prefix="local-lane-")
home = os.path.join(tmp, "home")
os.makedirs(home)
os.environ.update(HOME=home, USERPROFILE=home, GIT_TERMINAL_PROMPT="0")
for var in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "_LOOP_LANE_HELD", "LOOP_LANE_LOCAL"):
    os.environ.pop(var, None)
repo = os.path.join(tmp, "repo")
os.makedirs(os.path.join(repo, ".loop"))
os.makedirs(os.path.join(repo, ".github", "workflows"))
os.chdir(repo)


def git(*args):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid"] + list(args), cwd=repo,
                          capture_output=True, text=True).stdout.strip()


with open(os.path.join(repo, ".loop", "config.json"), "w") as handle:
    json.dump({"min_free_memory_gb": 0, "base": "main"}, handle)
with open(os.path.join(repo, skip.WORKFLOW), "w") as handle:
    handle.write("name: regression-pr\n")
git("init", "-q", "-b", "main")
git("add", "-A")
git("commit", "-qm", "one")
runs = os.path.join(repo, ".git", "loop", "runs")
os.makedirs(runs)
cfg = json.load(open(os.path.join(repo, ".loop", "config.json")))
SLUG = "g"
starts, probes = [], []
lane.prep = lambda top, c, out: (starts.append(out) or ("", "TOY_STOP: the lane would start here"))
answer = [""]
skip.probe = lambda limit=5: (probes.append(1) or answer[0])


def base(name):
    return lanekit.lane_base(runs, SLUG, name)


def ask(name="pr"):
    return lane.lane(runs, SLUG, name, {}, cfg, 0)


def clear():
    for name in os.listdir(runs):
        path = os.path.join(runs, name)
        shutil.rmtree(path) if os.path.isdir(path) else os.remove(path)
    del starts[:], probes[:]


head1 = git("rev-parse", "HEAD")

# the skip: a skipped lane is never a pass, in pr, qa or ship
reply = os.path.join(tmp, "reply.txt")
open(reply, "w").write("STEP: done\n")
for step in ("pr", "qa", "ship"):
    got = ask(step)
    last = json.load(open(base(step) + ".last"))
    check(got[0] == "skipped" and got[1].startswith("SKIPPED: no local lane is owed on this head") and "gh pr checks" in got[1], "%s: the status is `skipped`, never `pass`, with the SKIPPED first line: %s" % (step, got[:2]))
    check(last["state"] == "skipped" and last["skipped"] is True and last["head"] == head1 and lanekit.passed(runs, SLUG, head1, step) == "", "%s: .last records `skipped`, and the reuse never reads a pass" % step)
    check(open(base(step) + ".skip").read() == head1 and not os.path.exists(base(step) + ".ok") and not os.path.exists(base(step) + ".job"), "%s: the skip is recorded apart in .skip, .ok is never written, no job ran" % step)
check(not starts and len(probes) == 3, "no preparation or row ran")
check(lane.lane_status(runs, SLUG, "pr")[0] == "none" and ask("qa")[0] == "skipped", "lane_status never says pass for a skip (NO LANE), and asking again says skipped again")
real_run = skip.subprocess.run


def fake_gh(prs, runs_out, rc=0):
    """skip.accepts with a fake gh: `pr list` answers prs, the check-runs call answers runs_out."""
    def run(argv, **kw):
        if argv[0] != "gh":
            return real_run(argv, **kw)
        out = prs if argv[1] == "pr" else runs_out
        return subprocess.CompletedProcess(argv, rc, stdout=out + chr(10), stderr="")
    return run


skip.subprocess.run = fake_gh("0", "")
check(role.need_lane(runs, SLUG, reply, "qa") is None and role.need_lane(runs, SLUG, reply, "ship") is None, "no pull request yet: record qa and ship accept the recorded skip (the merge gate decides), and role.py is unchanged")
skip.subprocess.run = fake_gh("1", "green")
check(skip.accepts(runs, SLUG, "ship", head1) == head1, "a pull request exists and every check run on this exact head is green: ship accepts the skip")
skip.subprocess.run = fake_gh("1", "no")
check(skip.accepts(runs, SLUG, "ship", head1) == "" and (role.need_lane(runs, SLUG, reply, "ship") or ("",) * 3)[2] == "LANE_MISSING", "a pull request exists and a check is pending or failed: ship refuses the skip")
skip.subprocess.run = fake_gh("", "", rc=1)
check(skip.accepts(runs, SLUG, "ship", head1) == "", "gh failing is a refusal, never an acceptance")
skip.subprocess.run = real_run
waited = subprocess.run([sys.executable, os.path.join(scripts, "role.py"), "lane-wait", SLUG, "pr"], cwd=repo, capture_output=True, text=True,
                        env=dict(os.environ, LOOP_ROLE="worker"))
check(waited.returncode == 3 and "NO LANE" in (waited.stdout + waited.stderr), "lane-wait on a skipped lane exits 3 (NO LANE), never 0, so exit 0 still means a tested pass (%s)" % waited.returncode)
part = role.lane_part(SLUG)
check("### Regression lane" in part and "SKIPPED: no local lane is owed" in part, "the PR body's lane part prints the SKIPPED line: %s" % part.strip()[:140])

# the HEAD_MOVED case: a real .ok on an older head, then a skipped head, must not loop
clear()
with open(base("qa") + ".last", "w") as handle:
    json.dump({"attempt": "real", "head": head1, "state": "pass", "line": "LANE qa FULL 3/3 in 5s", "ended": time.time()}, handle)
with open(base("qa") + ".ok", "w") as handle:
    handle.write(head1)
open(os.path.join(repo, "a.txt"), "w").write("a")
git("add", "-A")
git("commit", "-qm", "two")
head2 = git("rev-parse", "HEAD")
check((role.need_lane(runs, SLUG, reply, "qa") or ("",) * 3)[2] == "HEAD_MOVED", "setup: a real .ok on the older head alone is HEAD_MOVED")
got = ask("qa")
skip.subprocess.run = fake_gh("0", "")
check(got[0] == "skipped" and open(base("qa") + ".ok").read() == head1 and open(base("qa") + ".skip").read() == head2 and role.need_lane(runs, SLUG, reply, "qa") is None, "a skipped head after an older real .ok leaves .ok on the old head and records the skip apart: record qa is satisfied, no HEAD_MOVED loop")
skip.subprocess.run = real_run

# private.pr_result: a skipped pr lane posts no status at all (B2), a pass posts success, a failure posts failure
import private  # noqa: E402
posted = []
real = (private.repo_is_private, private.required_checks, private.post_statuses)
private.repo_is_private = lambda top: True
private.required_checks = lambda top, base: (["ctx"], [])
private.post_statuses = lambda top, head, ok, names: posted.append(ok) or True
lane.lane_checks = lambda top, contexts: list(contexts)
private.pr_result(repo, "main", head1, "loop/x", None)
check(posted == [], "pr_result(ok=None), the skipped pr lane, posts no status")
private.pr_result(repo, "main", head1, "loop/x", True)
check(posted == [True], "pr_result(ok=True) still posts success for a real pass")
goal_src = open(os.path.join(scripts, "goal.py"), encoding="utf-8").read()
check('gate == "pass" or None' in goal_src, "goal.py pr passes the gate-derived value, so only a real pass can post success")
private.repo_is_private, private.required_checks, private.post_statuses = real

# every .ok reader is pinned: a new reader fails this until it is reviewed
found = {}
for here, _dirs, names in os.walk(os.path.join(root, "skills")):
    for name in names:
        if name.endswith(".py"):
            for n, line in enumerate(open(os.path.join(here, name), encoding="utf-8"), 1):
                if '".ok"' in line:
                    found.setdefault(name, []).append(("read" if "open(" in line and '"w"' not in line else "write/drop"))
check(found.get("lanekit.py") == ["read"] and set(found) <= {"lanekit.py", "lane.py"}, "the only .ok reader in skills/ is lanekit.lane_ok; the only writer is lane.py (a real pass): %s" % found)

# controls: the lane runs
clear()
answer[0] = "GitHub did not answer in 5s"
got = ask()
check(len(starts) == 1 and got[0] == "fail" and "TOY_STOP" in got[1] and not os.path.exists(base("pr") + ".ok"), "GitHub not answering: the lane starts (the stub stops it) and no .ok is written")
answer[0] = ""
clear()
os.environ["LOOP_LANE_LOCAL"] = "1"
got = ask()
check(len(starts) == 1 and not probes and "TOY_STOP" in got[1], "LOOP_LANE_LOCAL=1 forces the local lane without asking GitHub")
del os.environ["LOOP_LANE_LOCAL"]
clear()
wf = os.path.join(repo, skip.WORKFLOW)
os.rename(wf, wf + ".off")
git("add", "-A")
git("commit", "-qm", "no workflow")
got = ask()
check(len(starts) == 1 and not probes, "no regression-pr.yml in the repo: the local lane runs")
os.rename(wf + ".off", wf)
git("add", "-A")
git("commit", "-qm", "workflow back")
clear()
open(os.path.join(repo, "dirty.txt"), "w").write("x")
got = ask()
check(got[0] == "fail" and got[1].startswith("LANE_DIRTY") and not os.path.exists(base("pr") + ".ok") and not starts, "a dirty tree is refused with LANE_DIRTY and no pass is written")
os.remove(os.path.join(repo, "dirty.txt"))
clear()
held = {"head": git("rev-parse", "HEAD"), "attempt": "job", "started": time.time(), "limit": 600, "rc": base("pr") + ".job.rc", "pool": tmp,
        "markers": 1, "pid": os.getpid(), "pstart": lanekit.pstart(os.getpid())}
with open(base("pr") + ".job", "w") as handle:
    json.dump(held, handle)
got = ask()
check(got[0] == "running" and not probes and not os.path.exists(base("pr") + ".ok"), "a lane already running is never replaced by a skip")
clear()

# the real probe against a fake gh (POSIX only: Windows cannot run a script named gh)
if os.name != "nt":
    import importlib
    importlib.reload(skip)
    fake = os.path.join(tmp, "bin")
    os.makedirs(fake)
    gh = os.path.join(fake, "gh")

    def fake_gh(body):
        with open(gh, "w") as handle:
            handle.write("#!/bin/sh\n" + body + "\n")
        os.chmod(gh, os.stat(gh).st_mode | stat.S_IEXEC)

    os.environ["PATH"] = fake + os.pathsep + os.environ["PATH"]
    fake_gh("echo active")
    check(skip.probe() == "", "probe: gh says the workflow is active -> GitHub is answering")
    fake_gh("echo disabled_manually")
    check("not active" in skip.probe(), "probe: a disabled workflow is not a skip")
    fake_gh("exit 1")
    check(skip.probe().startswith("GitHub did not answer"), "probe: a failing gh runs the lane")
    fake_gh("exec sleep 3")
    started = time.time()
    check(skip.probe(1) == "GitHub did not answer in 1s" and time.time() - started < 2.5, "probe: a gh that does not answer in time runs the lane")
else:
    print("SKIP: the fake-gh probe cases need a POSIX machine")

shutil.rmtree(tmp, ignore_errors=True)
print("FAIL: %d case(s): %s" % (len(failed), "; ".join(failed)[:300]) if failed else "ALL PASS")
sys.exit(1 if failed else 0)
