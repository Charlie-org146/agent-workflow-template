#!/usr/bin/env python3
# reads: skills/workflow-regression/scripts/regression.py skills/workflow-regression/scripts/lanes_cli.py
"""shard-balance (o643): PR CI shards split the selected rows by recorded time, longest first to the least-loaded shard.

D1: each row lands in exactly one shard, the split is the same whatever order a shard sees the rows in, and the largest
shard is within 20% of the mean or one row's time (negative control: todo[i::n] is not); LOOP_PR_SHARD unset changes nothing.
D2: in a PR shard a row cut off by the per-row limit is LEFT with its name and does not fail the shard, a row that exits
non-zero still does, and without the shard it fails as before. The workflow carries the times file and lists the LEFT rows."""
import os
import random
import re
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
# The first push of a PR has no times file at all: no row is in it, every row is marked, none twice.
def fresh(shard):
    extra = dict(env, LOOP_PR_SHARD=shard, LOOP_ROW_TIMES=os.path.join(here, "none." + shard[0]))
    done = subprocess.run([sys.executable, REG, "run", "land", "--timeout", "2"], cwd=here, env=extra, capture_output=True, text=True)
    return done.stdout + done.stderr, open(extra["LOOP_ROW_TIMES"]).read() if os.path.exists(extra["LOOP_ROW_TIMES"]) else ""


o0, f0 = fresh("0/2")
o1, f1 = fresh("1/2")
marks = [line.split("\t") for f in (f0, f1) for line in f.splitlines()]
ran = sorted(m[0] for m in marks if m[2] in ("RAN", "LEFT"))
check("Traceback" not in o0 + o1 and ran == ["bad", "fast", "slow"] and sorted(m[0] for m in marks) == ["bad", "bad", "fast", "fast", "slow", "slow"],
      "with no times file every shard marks every selected row and each row is RAN in exactly one shard (%s)" % ran)
budget = subprocess.run([sys.executable, REG, "run", "land", "--reuse", "--budget", "1", "--timeout", "30"], cwd=here, env=dict(env, LOOP_PR_SHARD="0/1"),
                        capture_output=True, text=True)
check("BUDGET" in budget.stdout and "LEFT" in budget.stdout and "FAIL slow" not in budget.stdout and "Traceback" not in budget.stdout + budget.stderr,
      "rows left under the shard's time budget are LEFT and not failed (exit %d)" % budget.returncode)
check(code0 == 0 and "LEFT 1 over the 2 s row limit, not failed: slow" in out0 and "SPLIT 0/2: 1 of 3 rows" in out0,
      "a PR shard names a row cut off by the per-row limit as LEFT and does not fail (exit %d)" % code0)
check(code1 == 1 and "FAIL bad" in out1 and "PASS fast" in out1 and "LEFT" not in out1,
      "negative control: a row that exits non-zero inside the limit still fails its shard (exit %d)" % code1)
check(plain == 1 and "FAIL slow" in outp and "FAIL bad" in outp and "SPLIT" not in outp and "LEFT" not in outp,
      "negative control: with LOOP_PR_SHARD unset nothing changes, the slow row fails and every row runs (exit %d)" % plain)
check("slow\t2\tLEFT" in open(stamp + ".0").read() and "fast\t" in open(stamp + ".1").read(),
      "a shard's times file keeps its rows' seconds and stamps the LEFT row at the limit")
check(re.search(r"bad\t[\d.]+\tSEL", open(stamp + ".0").read()) and re.search(r"fast\t[\d.]+\tRAN", open(stamp + ".1").read()),
      "a shard marks the rows it ran RAN and the rest of the selection SEL")
flow = lanes_cli.NARROW
check("LOOP_ROW_TIMES" in flow and "actions/cache/save" in flow and 'awk \'$3 == "LEFT"' in flow and "upload-artifact" in flow,
      "the PR workflow restores and saves the times file and its affected job lists the LEFT rows")
# The affected job's coverage guard: run its script on fixtures where one row ran in no shard and one ran in two.
script = [b for b in flow.split("      - run: |\n")[1:] if "ran.txt" in b][0].split("      - ")[0]
script = "\n".join(x[10:] for x in script.splitlines())
work = tempfile.mkdtemp(prefix="shard-balance-affected-")
for name, body in (("shard-0", "a\t5\tRAN\nb\t1\tSEL\nc\t1\tSEL\nd\t2\tSEL\nold\t9\t\n"), ("shard-1", "a\t5\tSEL\nb\t3\tRAN\nc\t1\tRAN\nd\t0\tSEL\n"),
                   ("shard-2", "a\t5\tSEL\nb\t3\tSEL\nc\t2\tRAN\nd\t0\tSEL\ne\t7\tLEFT\n")):
    os.makedirs(os.path.join(work, "s", name))
    with open(os.path.join(work, "s", name, "t.tsv"), "w") as handle:
        handle.write(body)
stub = os.path.join(work, "skills", "workflow-regression", "scripts")
os.makedirs(stub)
with open(os.path.join(stub, "regression.py"), "w") as handle:
    handle.write("import sys\nopen('ran-here.txt', 'a').write(sys.argv[2] + '\\n')\nsys.exit(int(sys.argv[2] == 'd' and 'FAILD' in __import__('os').environ))\n")
gate = subprocess.run(["bash", "-c", script], cwd=work, capture_output=True, text=True)
sel = sorted(open(os.path.join(work, "ran-here.txt")).read().split()) if os.path.exists(os.path.join(work, "ran-here.txt")) else []
check(gate.returncode == 0 and sel == ["d"] and "run twice: c" in gate.stdout and "not failed: e" in gate.stdout,
      "affected runs the row no shard ran, names the row two shards ran and the LEFT row, and passes (ran %s, exit %d)" % (sel, gate.returncode))
os.remove(os.path.join(work, "ran-here.txt"))
bad = subprocess.run(["bash", "-c", script], cwd=work, capture_output=True, text=True, env=dict(os.environ, FAILD="1"))
check(bad.returncode == 1, "negative control: a missing row that fails when affected runs it fails the job (exit %d)" % bad.returncode)
kept = open(os.path.join(work, "all.tsv")).read().split("\n")
check("a\t5\tRAN" in kept and not any(x.endswith("SEL") for x in kept), "the saved times keep each row's own shard line and no SEL line")
# D3 (pr-check-fast, fast-3min): 8 shards of 120 seconds; docs.py check runs once per merge, in the merge-queue job `small` on the merged
# ref with no review log (a clone has none), so a page-level LOCKED or FORMAT line fails the merge group, not the pull request's affected job.
check("shard: [0, 1, 2, 3, 4, 5, 6, 7]" in flow and "matrix.shard }}/8 " in flow and "--budget 120 " in flow,
      "the PR workflow runs 8 shards with a 120-second budget each")
job = flow.split("\n  affected:")[1].split("\n  small:")[0]
small = flow.split("\n  small:")[1]
docs = "- run: python3 skills/workflow-docs/scripts/docs.py check"
step = [x.strip()[7:] for x in small.splitlines() if x.strip() == docs]
check(flow.count("docs.py check") == 1 and len(step) == 1 and docs not in job and "fetch-depth: 0" in small,
      "docs.py check runs exactly once per merge, in small with the history checked out, and not in affected")
clone = tempfile.mkdtemp(prefix="pr-docs-")
subprocess.run(["git", "clone", "-q", root, clone], check=True, capture_output=True)  # a CI checkout: origin set, no .git/loop/reviews.tsv
subprocess.run(["git", "update-ref", "refs/remotes/origin/main", "HEAD"], cwd=clone, check=True)  # the base is the pull request's own start
good = subprocess.run(["bash", "-c", step[0]], cwd=clone, capture_output=True, text=True)
check(good.returncode == 0 and "DOCS OK" in good.stdout, "a pull request whose docs pass passes the docs step (exit %d)" % good.returncode)
setup = os.path.join(clone, "docs", "wiki", "Setup.md")
lines = open(setup).read().split("\n")
at = next(i for i, x in enumerate(lines) if re.match(r"- [A-Z]+-\d+: \*\*Reviewed", x))
lines[at] += " (changed with no review)"
open(setup, "w").write("\n".join(lines))
subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qam", "change a reviewed requirement"], cwd=clone, check=True, capture_output=True)
bad = subprocess.run(["bash", "-c", step[0]], cwd=clone, capture_output=True, text=True)
check(bad.returncode != 0 and "LOCKED Setup" in bad.stdout, "negative control: a changed reviewed requirement with no review log fails the docs step with its own LOCKED line (exit %d)" % bad.returncode)
wf = os.path.join(root, ".github", "workflows", "regression-pr.yml")
check(not os.path.exists(wf) or open(wf).read() == flow.replace("@BASE@", "main").replace("@LEVELS@", "nightly"),
      ".github/workflows/regression-pr.yml is the rendered workflow")
sys.exit(1 if failed else 0)
