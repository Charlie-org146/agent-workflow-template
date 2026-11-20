#!/usr/bin/env python3
# reads: skills/workflow-regression/scripts/regression.py skills/workflow-regression/scripts/lanes_cli.py
"""shard-balance (o643): PR CI shards split the selected rows by recorded time, longest first to the least-loaded shard.

D1: each row lands in exactly one shard, the split is the same whatever order a shard sees the rows in, and the largest
shard is within 20% of the mean or one row's time (negative control: todo[i::n] is not); LOOP_PR_SHARD unset changes nothing.
D2: in a PR shard a row cut off by the per-row limit is LEFT with its name and does not fail the shard, a row that exits
non-zero still does, and without the shard it fails as before. The workflow carries the times file and lists the LEFT rows."""
import os
import random
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
scripts = os.path.join(root, "skills", "workflow-regression", "scripts")
REG = os.path.join(scripts, "regression.py")
sys.path.insert(0, scripts)
sys.dont_write_bytecode = True
import lanes_cli  # noqa: E402
import regression  # noqa: E402

failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


random.seed(7)
ids = ["row%03d" % n for n in range(240)]
times = {k: random.choice([1, 1, 2, 3, 40, 150]) for k in ids[:230]}  # ten rows have no recorded time: the median
median = sorted(times.values())[len(times) // 2]
weight = {k: times.get(k, median) for k in ids}
mean = sum(weight.values()) / 6
shards = regression.split(ids, times, 6)
flat = [k for s in shards for k in s]
check(sorted(flat) == ids and len(set(flat)) == len(ids), "each row lands in exactly one of the six shards")
check(shards == regression.split(random.sample(ids, len(ids)), times, 6), "the split is the same in every shard, whatever order it sees the rows")
worst = max(sum(weight[k] for k in s) for s in shards)
check(worst <= mean + max(0.2 * mean, max(weight.values())), "the largest shard is within 20%% of the mean or one row's time (%d vs mean %.0f)" % (worst, mean))
slow = {k: 100 for k in ids[::6]}  # negative control: every sixth row is slow, so position-based slices give one shard all of them
byposition = [sum(slow.get(k, 1) for k in ids[i::6]) for i in range(6)]
bytime = [sum(slow.get(k, 1) for k in s) for s in regression.split(ids, {k: slow.get(k, 1) for k in ids}, 6)]
check(max(byposition) > 1.2 * (sum(byposition) / 6) and max(bytime) <= sum(bytime) / 6 + 100,
      "negative control: todo[i::n] leaves a shard far over the mean (%d) where the time split does not (%d)" % (max(byposition), max(bytime)))
check(regression.split(["a", "b"], {}, 3) == [["a"], ["b"], []], "rows with no recorded time still split")

here = tempfile.mkdtemp(prefix="shard-balance-")
env = dict(os.environ, LOOP_FREE_GB="100", LOOP_ROLE="", GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@e.x", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@e.x")
env.pop("LOOP_PR_SHARD", None)
for step in (["git", "init", "-q", "-b", "main"], ["git", "config", "commit.gpgsign", "false"]):
    subprocess.run(step, cwd=here, check=True, capture_output=True)
os.makedirs(os.path.join(here, ".loop"))
rows = [("fast", "exit 0"), ("slow", "sleep 20"), ("bad", "exit 1")]
with open(os.path.join(here, ".loop", "regression.tsv"), "w") as handle:
    handle.write("# id\tlevel\tcommand\tgoal\tseen_red\tdescription\tcategory\tlink\n")
    handle.writelines("%s\tland\t%s\t\t2026-01-01\tx\tcriterion\t\n" % row for row in rows)
subprocess.run(["git", "add", "-A"], cwd=here, check=True, capture_output=True)
subprocess.run(["git", "commit", "-qm", "rows"], cwd=here, check=True, capture_output=True, env=env)
stamp = os.path.join(here, "times.tsv")
with open(stamp, "w") as handle:
    handle.write("slow\t100\t\nbad\t50\t\nfast\t1\t\n")  # longest first: slow to shard 0, bad and fast to shard 1


def run(shard):
    extra = dict(env, LOOP_PR_SHARD=shard, LOOP_ROW_TIMES=stamp + "." + shard.split("/")[0]) if shard else env
    if shard:
        with open(extra["LOOP_ROW_TIMES"], "w") as handle:
            handle.write(open(stamp).read())
    done = subprocess.run([sys.executable, REG, "run", "land", "--timeout", "2"], cwd=here, env=extra, capture_output=True, text=True)
    return done.returncode, done.stdout + done.stderr


code0, out0 = run("0/2")
code1, out1 = run("1/2")
plain, outp = run("")
check(code0 == 0 and "LEFT 1 over the 2 s row limit, not failed: slow" in out0 and "SPLIT 0/2: 1 of 3 rows" in out0,
      "a PR shard names a row cut off by the per-row limit as LEFT and does not fail (exit %d)" % code0)
check(code1 == 1 and "FAIL bad" in out1 and "PASS fast" in out1 and "LEFT" not in out1,
      "negative control: a row that exits non-zero inside the limit still fails its shard (exit %d)" % code1)
check(plain == 1 and "FAIL slow" in outp and "FAIL bad" in outp and "SPLIT" not in outp and "LEFT" not in outp,
      "negative control: with LOOP_PR_SHARD unset nothing changes, the slow row fails and every row runs (exit %d)" % plain)
check("slow\t2\tLEFT" in open(stamp + ".0").read() and "fast\t" in open(stamp + ".1").read(),
      "a shard's times file keeps its rows' seconds and stamps the LEFT row at the limit")
flow = lanes_cli.NARROW
check("LOOP_ROW_TIMES" in flow and "actions/cache/save" in flow and 'awk \'$3 == "LEFT"' in flow and "upload-artifact" in flow,
      "the PR workflow restores and saves the times file and its affected job lists the LEFT rows")
wf = os.path.join(root, ".github", "workflows", "regression-pr.yml")
check(not os.path.exists(wf) or open(wf).read() == flow.replace("@BASE@", "main").replace("@LEVELS@", "nightly"),
      ".github/workflows/regression-pr.yml is the rendered workflow")
sys.exit(1 if failed else 0)
