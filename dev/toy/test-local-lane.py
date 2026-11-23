#!/usr/bin/env python3
# reads: skills/workflow-delivery/scripts/skip.py skills/workflow-delivery/scripts/lane.py skills/workflow-delivery/scripts/fit.py
"""local-lane (DEL-25.3): no local full lane while GitHub runs the tests.

Done: with regression-pr.yml in the repo and GitHub answering, a goal's lane is recorded `skipped` (never pass, never .ok): pr goes on with a
SKIPPED first line (the PR body prints it), and qa and ship count the skip only while every GitHub check run on that exact head is green (otherwise
they refuse with LANE_MISSING). Controls: GitHub not answering, LOOP_LANE_LOCAL=1, no workflow file, a dirty tree and a lane already running each run
the lane (or refuse) exactly as before, and a lane that was never a skip is refused as before. The probe and the checks are stubs here;
skip.probe and skip.accepts run against a fake gh on a POSIX machine.
Needs fcntl (lane.py does): Mac, Linux and CI; without it the toy exits 77 (skipped). usage: test-local-lane.py"""
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
    sys.exit(77)
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
    handle.write("name: regression-pr\njobs:\n  shard:\n    if: github.event_name != 'merge_group'\n    runs-on: ubuntu-latest\n  affected:\n    needs: shard\n    if: always() && github.event_name != 'merge_group'\n    runs-on: ubuntu-latest\n"
                 "  small:\n    if: github.event_name == 'merge_group'\n    runs-on: ubuntu-latest\n")
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
git("update-ref", "refs/remotes/origin/main", head1)  # the base branch the required jobs are read from
git("symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")

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


SHARDS = "".join("shard (%d)" % n + chr(9) + "completed" + chr(9) + "success" + chr(10) for n in range(40))  # more than one page of 30
GREEN = SHARDS + "affected" + chr(9) + "completed" + chr(9) + "success" + chr(10)
FAIL = GREEN.replace("shard (7)" + chr(9) + "completed" + chr(9) + "success", "shard (7)" + chr(9) + "completed" + chr(9) + "failure")
UNRELATED = "lint" + chr(9) + "completed" + chr(9) + "success" + chr(10)
QUEUED = "shard (0)" + chr(9) + "queued" + chr(9) + chr(10) + UNRELATED
asked = []


def fake_gh(runs_out, rc=0):
    """skip.accepts with a fake gh: the check-runs call answers runs_out in the shape of its --jq projection (name, status, conclusion)."""
    def run(argv, **kw):
        if argv[0] != "gh":
            return real_run(argv, **kw)
        asked.append(argv)
        return subprocess.CompletedProcess(argv, rc, stdout=runs_out, stderr="")
    return run


skip.subprocess.run = fake_gh("")
check(skip.accepts(runs, SLUG, "ship", head1) == "" and (role.need_lane(runs, SLUG, reply, "ship") or ("",) * 3)[2] == "LANE_MISSING", "with no check run on this exact head, record ship refuses the skip")
check(skip.accepts(runs, SLUG, "qa", head1) == "" and (role.need_lane(runs, SLUG, reply, "qa") or ("",) * 3)[2] == "LANE_MISSING", "with no check run on this exact head, record qa refuses the skip")
skip.subprocess.run = fake_gh(UNRELATED)
check(skip.accepts(runs, SLUG, "ship", head1) == "", "an unrelated green check run does not count while regression-pr's jobs are not there")
skip.subprocess.run = fake_gh(QUEUED)
check(skip.accepts(runs, SLUG, "ship", head1) == "", "regression-pr's shard still queued beside an unrelated green check: refused")
skip.subprocess.run = fake_gh(SHARDS)
check(skip.accepts(runs, SLUG, "ship", head1) == "", "regression-pr's shards green but its other pull-request job missing: refused")
WORKFLOW_TEXT = ("name: regression-pr" + chr(10) + "jobs:" + chr(10) + "  shard:" + chr(10) + "    if: github.event_name != 'merge_group'" + chr(10) + "    runs-on: ubuntu-latest" + chr(10)
                 + "  affected:" + chr(10) + "    runs-on: ubuntu-latest" + chr(10) + "  small:" + chr(10) + "    if: github.event_name == 'merge_group'" + chr(10) + "    runs-on: ubuntu-latest" + chr(10))
check(skip.required_jobs(WORKFLOW_TEXT) == ["shard", "affected"], "required_jobs: the pull-request jobs of the workflow text, not the merge-queue job")
check(skip.required_jobs("") == [] and skip.required_jobs("name: x" + chr(10)) == [], "required_jobs: an empty or job-less text gives no jobs, so accepts refuses")
short = WORKFLOW_TEXT.replace("  affected:", '  "affected":')
check(skip.required_jobs(short) == [], "required_jobs: a parse that missed a job id (counts differ) gives no jobs, so accepts refuses")
skip.subprocess.run = fake_gh(GREEN)
check(skip.accepts(runs, SLUG, "ship", head1) == head1 and role.need_lane(runs, SLUG, reply, "ship") is None and role.need_lane(runs, SLUG, reply, "qa") is None, "every regression-pr job (41 runs here, more than one page) is green on this exact head: qa and ship accept the skip, and role.py is unchanged")
# a head that edits the workflow still gets the base branch's required set
with open(os.path.join(repo, skip.WORKFLOW), "w") as handle:
    handle.write("name: regression-pr" + chr(10) + "jobs:" + chr(10) + "  small:" + chr(10) + "    runs-on: ubuntu-latest" + chr(10))
check(skip.accepts(runs, SLUG, "ship", head1) == head1, "the required set is the base branch's, whatever the working copy's workflow says")
git("add", "-A")
git("commit", "-qm", "edit the workflow")
head_edit = git("rev-parse", "HEAD")
for step in ("ship",):
    with open(base(step) + ".skip", "w") as handle:
        handle.write(head_edit)
    with open(base(step) + ".last", "w") as handle:
        json.dump({"attempt": "skip", "head": head_edit, "state": "skipped", "skipped": True, "line": "SKIPPED", "ended": time.time()}, handle)
skip.subprocess.run = fake_gh("small" + chr(9) + "completed" + chr(9) + "success" + chr(10))
check(skip.accepts(runs, SLUG, "ship", head_edit) == "", "the required set is the base branch's, whatever the head's workflow says: only the head's own job green is refused")
skip.subprocess.run = fake_gh(GREEN)
check(skip.accepts(runs, SLUG, "ship", head_edit) == head_edit, "the same head with the base branch's jobs green is accepted")
# the base branch name comes from the default branch's config: a head that sets its own base still gets the default branch's set
with open(os.path.join(repo, ".loop", "config.json"), "w") as handle:
    json.dump({"min_free_memory_gb": 0, "base": "elsewhere"}, handle)
git("add", "-A")
git("commit", "-qm", "own base")
head_cfg = git("rev-parse", "HEAD")
with open(base("ship") + ".skip", "w") as handle:
    handle.write(head_cfg)
with open(base("ship") + ".last", "w") as handle:
    json.dump({"attempt": "skip", "head": head_cfg, "state": "skipped", "skipped": True, "line": "SKIPPED", "ended": time.time()}, handle)
skip.subprocess.run = fake_gh("small" + chr(9) + "completed" + chr(9) + "success" + chr(10))
check(skip.accepts(runs, SLUG, "ship", head_cfg) == "", "the base name comes from the default branch's config: a head that names another base is still held to the default branch's set")
skip.subprocess.run = fake_gh(GREEN)
check(skip.accepts(runs, SLUG, "ship", head_cfg) == head_cfg, "the same head with the default branch's jobs green is accepted")
# a base ref that is missing or cannot be read refuses
git("update-ref", "-d", "refs/remotes/origin/main")
check(skip.accepts(runs, SLUG, "ship", head_cfg) == "", "a missing base ref refuses")
git("symbolic-ref", "--delete", "refs/remotes/origin/HEAD")
check(skip.base_ref() == "" and skip.accepts(runs, SLUG, "ship", head_cfg) == "", "a default branch that cannot be resolved refuses")
git("update-ref", "refs/remotes/origin/main", head1)
git("symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")
check(skip.base_ref() == "origin/main", "the base branch is resolved again once the ref exists")
git("reset", "-q", "--hard", head1)
skip.subprocess.run = fake_gh(GREEN)
check("--paginate" in asked[-1] and not any("merge_group" in a for a in asked[-1]), "the check-runs call is paginated")
skip.subprocess.run = fake_gh(FAIL)
check(skip.accepts(runs, SLUG, "ship", head1) == "" and (role.need_lane(runs, SLUG, reply, "ship") or ("",) * 3)[2] == "LANE_MISSING", "a check pending or failed on that head: ship refuses the skip")
skip.subprocess.run = fake_gh("", rc=1)
check(skip.accepts(runs, SLUG, "ship", head1) == "", "gh failing is a refusal, never an acceptance")
# a skip, then a real lane on the same head that fails: the old .skip no longer counts, for every step
skip.subprocess.run = fake_gh(GREEN)
kept = {}
for step in ("qa", "ship", "pr"):
    with open(base(step) + ".last") as handle:
        kept[step] = handle.read()
    with open(base(step) + ".last", "w") as handle:
        json.dump({"attempt": "real", "head": head1, "state": "fail", "line": "LANE %s FAIL" % step, "ended": time.time()}, handle)
check(os.path.exists(base("ship") + ".skip") and skip.accepts(runs, SLUG, "ship", head1) == "" and (role.need_lane(runs, SLUG, reply, "ship") or ("",) * 3)[2] == "LANE_MISSING",
      "a skip followed by a failing real lane on the same head: the old .skip no longer counts")
for step in kept:
    with open(base(step) + ".last", "w") as handle:
        handle.write(kept[step])
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
skip.subprocess.run = fake_gh(GREEN)
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
del posted[:]
check(private.pr_result(repo, "main", head1, "loop/x", None) is True and posted == [], "pr_result(ok=None) returns True (goal.py records statuses ok) and posts nothing")
origin_dir = os.path.join(tmp, "origin")  # a non-bare local origin; nothing is pushed in this toy (TD1152): its branch is made by a fetch into it
os.makedirs(origin_dir)
subprocess.run(["git", "init", "-q", "-b", "other"], cwd=origin_dir, capture_output=True, check=True)
subprocess.run(["git", "fetch", "-q", repo, head1 + ":refs/heads/loop/x"], cwd=origin_dir, capture_output=True, check=True)
git("remote", "add", "origin", origin_dir)
private.pr_result(repo, "main", head1, "loop/x", False)
check(posted == [False], "pr_result(ok=False) posts failure when the head is on the remote")
# goal.py pr itself, run with everything around it stubbed: what it hands pr_result and what it records in the goal's statuses
import types  # noqa: E402
import goal  # noqa: E402


def run_pr(gate):
    seen, saved = [], {}
    stubs = dict(held=lambda slug: {"flow": {s: "done" for s in goal.FLOW}, "branch": "loop/x", "log": [""]}, config=lambda: {"base": "main"},
                 queue=lambda *a, **k: None, pods=None, round_stop=lambda *a, **k: None, git=lambda *a, **k: "", read=lambda path: "", goal_file=lambda slug: "g.md",
                 root=lambda: repo, state_dir=lambda: runs, save=lambda state, note=None: saved.update(state=dict(state)),
                 run=lambda argv, **k: subprocess.CompletedProcess(argv, 1, "", ""), no=lambda text: (_ for _ in ()).throw(AssertionError(text)))
    fits = dict(budget_stop=lambda *a, **k: None, owed=lambda *a, **k: [], regen=lambda g, slug: "H", pr_text=lambda g, state: "",
                pr_open=lambda *a, **k: "URL", monitor=lambda name: types.SimpleNamespace(pr_closing=lambda top, body: []))
    roles = dict(sync=lambda base: ("none", ""), requirement_gate=lambda *a, **k: None, bump_version=lambda g, state, head: head,
                 lane=lambda *a, **k: (gate, "LANE LINE", []), record=lambda *a, **k: None, flow_spec=lambda: {})
    guard = dict(waiting_gate=lambda *a, **k: None, sync_touches=lambda *a, **k: None, touches_of=lambda *a, **k: [])
    pr_result = lambda top, base, head, branch, ok: seen.append(ok) or True
    originals = []
    for module, table in ((goal, stubs), (goal.fit, fits), (goal.role, roles), (goal.guards, guard), (goal.private, dict(pr_result=pr_result))):
        for name, value in table.items():
            originals.append((module, name, getattr(module, name, None)))
            setattr(module, name, value)
    try:
        code = goal.cmd_pr(types.SimpleNamespace(slug="g"))
    finally:
        for module, name, value in reversed(originals):
            setattr(module, name, value)
    return seen, saved.get("state", {}).get("statuses"), code


import io  # noqa: E402
import contextlib  # noqa: E402
with contextlib.redirect_stdout(io.StringIO()):
    got_skip = run_pr("skipped")
    got_pass = run_pr("pass")
check(got_skip[0] == [None] and got_skip[1] == "ok" and got_skip[2] == 0, "goal.py pr with a skipped gate hands pr_result None and records statuses ok: %s" % (got_skip,))
check(got_pass[0] == [True] and got_pass[1] == "ok", "goal.py pr with a real pass hands pr_result True: %s" % (got_pass,))
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
