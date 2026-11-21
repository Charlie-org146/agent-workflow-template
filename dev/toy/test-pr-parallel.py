#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-monitoring/scripts/pool.py
"""DEL-15, parallel by files: goals at pr whose touches share no path take their turn at once; a goal waits only for an earlier
goal whose touches overlap its own."""
import json
import os
import sys
import tempfile
import time

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, "..", "..", "skills", "workflow-monitoring", "scripts"))
import pool  # noqa: E402

failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


with tempfile.TemporaryDirectory() as tmp:
    runs = os.path.join(tmp, "runs")
    os.makedirs(runs)

    def goal(slug, touches, step="pr"):
        with open(os.path.join(runs, slug + ".json"), "w") as handle:
            json.dump({"slug": slug, "status": "running", "step": step, "touches": touches}, handle)

    goal("g1", ["skills/a"])
    goal("g2", ["skills/b"])
    goal("g3", ["skills/a/x"])
    goal("g4", [])
    check(pool.pr_turn(runs, "g1") == "", "the first goal at pr has its turn")
    time.sleep(0.01)
    check(pool.pr_turn(runs, "g2") == "", "a goal with disjoint touches has its turn while the first lane runs")
    time.sleep(0.01)
    check(pool.pr_turn(runs, "g3") == "g1", "a goal whose touches sit inside an earlier goal's waits for that goal")
    time.sleep(0.01)
    check(pool.pr_turn(runs, "g4") == "g1", "a goal with no touches and no readable branch overlaps everything and waits for the first goal")
    goal("g1", ["skills/a"], step="release")  # g1 opened its PR and loses its place
    check(pool.pr_turn(runs, "g3") == "", "when the overlapping goal is done, the waiting goal has its turn")
    check(pool.pr_turn(runs, "g4") == "g2", "a goal with no touches and no readable branch still waits for the earlier goals left in the line")

# #5344: a goal with no recorded touches gets them from its branch's diff against the base
import subprocess  # noqa: E402

with tempfile.TemporaryDirectory() as tmp:
    runs = os.path.join(tmp, "runs")
    os.makedirs(runs)
    main = os.path.join(tmp, "main")

    def git(*a, cwd=main):
        subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "-c", "commit.gpgsign=false"] + list(a), cwd=cwd, check=True, capture_output=True)

    os.makedirs(main)
    git("init", "-q", "-b", "main")
    open(os.path.join(main, "seed"), "w").write("s")
    git("add", "seed")
    git("commit", "-q", "-m", "seed")

    def branch(slug, files, touches):
        tree = os.path.join(tmp, slug)
        git("worktree", "add", "-q", "-b", slug, tree, "main")
        for f in files:
            os.makedirs(os.path.dirname(os.path.join(tree, f)), exist_ok=True)
            open(os.path.join(tree, f), "w").write(slug)
        git("add", "-A", cwd=tree)
        git("commit", "-q", "-m", slug, cwd=tree)
        with open(os.path.join(runs, slug + ".json"), "w") as handle:
            json.dump({"slug": slug, "status": "running", "step": "pr", "worktree": tree, "touches": touches}, handle)

    branch("d1", ["skills/a/x.py"], [])
    branch("d2", ["docs/b.md"], [])
    branch("d3", ["skills/a/x.py"], [])
    branch("d4", ["skills/a/z.py"], ["skills/a"])
    check(pool.pr_turn(runs, "d1") == "", "5344: the first goal with no recorded touches has its turn")
    time.sleep(0.01)
    check(pool.pr_turn(runs, "d2") == "", "5344: two goals with no recorded touches and disjoint diffs do not wait on each other")
    time.sleep(0.01)
    check(pool.pr_turn(runs, "d3") == "d1", "5344: negative control: no recorded touches, a diff sharing a file with an earlier goal still waits")
    time.sleep(0.01)
    check(pool.pr_turn(runs, "d4") == "d1", "5344: negative control: recorded touches overlapping an earlier goal's diff still wait")
if not failed:
    print("PASS: DEL-15: goals with disjoint touches take their pr turn at once and overlapping ones wait")
sys.exit(1 if failed else 0)
