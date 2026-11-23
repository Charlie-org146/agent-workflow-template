#!/usr/bin/env python3
# reads: skills/workflow-regression/scripts/lanes_cli.py skills/workflow-regression/scripts/regression.py .github/workflows/row-times.tsv
"""shard-fits-budget (o852): the PR shards split the rows by time, and every shard fits its budget.

The shard job restores the times cache from the same path the affected job saves it to, so the cache can hit; the shard
step lays the committed times (.github/workflows/row-times.tsv, measured on GitHub) under the cache's, so a first run
of a PR splits by time, not by count; a repo with neither gets an empty file and the step goes on. Split with the real
regression.split over every PR-shard row (a row with no time weighs the median), the most loaded of the 8 shards fits
the o852 budget. Negative controls: the old restore path, a missing seed line, and one row grown past the budget."""
import os
import re
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
scripts = os.path.join(root, "skills", "workflow-regression", "scripts")
sys.path.insert(0, scripts)
sys.dont_write_bytecode = True
import lanes_cli  # noqa: E402
import regression  # noqa: E402

TARGET = 866  # o852: the owner's per-shard budget, set in the workflow only after timed runs show every shard fits
failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


flow = lanes_cli.NARROW


def cache_paths(text):
    """(restore path, save path) of the times cache in a workflow text."""
    def path(kind):
        part = text.split("actions/cache/%s@" % kind)[1]
        return re.search(r"path: (\S+)", part).group(1)
    return path("restore"), path("save")


budget = re.search(r"B=(\d+);", flow)
check(budget is not None and int(budget.group(1)) <= TARGET, "the workflow's own shard budget (B=%s) never exceeds the owner's %d s" % (budget and budget.group(1), TARGET))
check(budget is not None and int(budget.group(1)) in (120, TARGET), "the workflow's shard budget is the current 120 s or the owner's %d s, nothing else" % TARGET)
got = cache_paths(flow)
check(got[0] == got[1] == "all.tsv", "the shard job restores the times cache from the path the affected job saves it to: %s" % (got,))
old = flow.replace("          path: all.tsv\n          key: row-times-", "          path: ${{ runner.temp }}/t.tsv\n          key: row-times-", 1)
check(len(set(cache_paths(old))) == 2, "negative control: the old restore path differs from the save path, so the cache never hits")

seed = [x.strip() for x in flow.splitlines() if "row-times.tsv" in x and "cat " in x]
check(len(seed) == 1 and ">$T" in seed[0], "the shard step has one seed line, written to the shard's times file $T")


def run_seed(files):
    """Run the seed line in a temp checkout holding files; (exit, t.tsv text, all.tsv left)."""
    work = tempfile.mkdtemp(prefix="shard-budget-")
    temp = os.path.join(work, "_temp")
    os.makedirs(os.path.join(work, ".github", "workflows"))
    os.makedirs(temp)
    for name, body in files.items():
        with open(os.path.join(work, name), "w") as handle:
            handle.write(body)
    line = seed[0].split("  #")[0].replace("$T", temp + "/t.tsv")
    r = subprocess.run(["bash", "--noprofile", "--norc", "-e", "-c", line], cwd=work, capture_output=True, text=True)
    out = os.path.join(temp, "t.tsv")
    return r.returncode, open(out).read() if os.path.exists(out) else None, os.path.exists(os.path.join(work, "all.tsv"))


if seed:
    committed = "a\t100.0\t\nb\t5.0\t\n"
    code, text, left = run_seed({".github/workflows/row-times.tsv": committed})
    check(code == 0 and text == committed and not left, "with no cache the shard's times file is the committed times (exit %d)" % code)
    code, text, left = run_seed({".github/workflows/row-times.tsv": committed, "all.tsv": "a\t40\tRAN\nc\t7\tCUT\n"})
    rows = regression.merged(os.devnull)
    if text is not None:
        path = os.path.join(tempfile.mkdtemp(prefix="shard-budget-m-"), "t.tsv")
        open(path, "w").write(text)
        rows = regression.merged(path)
    check(code == 0 and rows.get("a") == [40.0, ""] and rows.get("b") == [5.0, ""] and rows.get("c") == [7.0, "CUT"] and not left,
          "the cache's times override the committed ones, its CUT marks stay, and the restored file is moved out of the checkout")
    code, text, left = run_seed({})
    check(code == 0 and text == "" and not left, "a repo with no committed times and no cache gets an empty times file and the step goes on (exit %d)" % code)

times = {}
for line in open(os.path.join(root, ".github", "workflows", "row-times.tsv")):
    cols = line.rstrip("\n").split("\t")
    if len(cols) > 1:
        times[cols[0]] = float(cols[1])
rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(root, ".loop", "regression.tsv")) if l.strip() and not l.startswith("#")]
ids = [r[0] for r in rows if len(r) > 1 and r[1] in ("land", "nightly") and (r[6:7] or [""])[0] != "workflow" and r[0] in times]
missing = [r[0] for r in rows if len(r) > 1 and r[1] in ("land", "nightly") and (r[6:7] or [""])[0] != "workflow" and r[0] not in times]


def loads(weights):
    return [sum(weights[k] for k in shard) for shard in regression.split(sorted(weights), weights, 8)]


known = sorted(times[k] for k in ids)
weights = dict({k: times[k] for k in ids}, **{k: known[len(known) // 2] for k in missing})
load = loads(weights)
print("loads: %s (rows %d, %d with no time; total %d s)" % ([round(x) for x in load], len(weights), len(missing), sum(weights.values())))
check(len(ids) > 500 and max(load) <= TARGET, "the most loaded of 8 shards, %d s, fits the %d s budget" % (max(load), TARGET))
grown = dict(weights, **{ids[0]: TARGET + 1})
check(max(loads(grown)) > TARGET, "negative control: one row grown past the budget makes a shard exceed it")
print("ALL PASS" if not failed else "FAILED: %d" % len(failed))
sys.exit(1 if failed else 0)
