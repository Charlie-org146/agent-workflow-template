#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-monitoring/scripts/pool.py skills/workflow-delivery/scripts/goal.py
"""pr-queue-step (#4523): a goal keeps its place in the pr queue though its run record never said pr.

A joins first while its record says build, B joins later at pr: after A's goal.py pr joins (pool.pr_join), A stays first in
pr_order and pr_turn. Controls: without the join A's ticket is dropped (the bug), and a merged goal's ticket is still dropped."""
import json
import os
import sys
import tempfile
import time

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(root, "skills", "workflow-monitoring", "scripts"))
sys.dont_write_bytecode = True
import pool  # noqa: E402

failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def world(tmp, records):
    runs = os.path.join(tmp, "runs")
    os.makedirs(runs)
    for slug, rec in records.items():
        with open(os.path.join(runs, slug + ".json"), "w") as handle:
            json.dump(dict(rec, slug=slug, status="running"), handle)
    return runs


class Goal:
    def __init__(self, runs):
        self.runs = runs

    def save(self, state, note):
        with open(os.path.join(self.runs, state["slug"] + ".json"), "w") as handle:
            json.dump(state, handle)


def join(runs, slug, joined=True):
    state = json.load(open(os.path.join(runs, slug + ".json")))
    if joined:
        pool.pr_join(Goal(runs), state)
    return pool.pr_turn(runs, slug)


def names(runs):
    return [n for _, n, _ in pool.pr_order(runs)]


with tempfile.TemporaryDirectory() as tmp:
    runs = world(tmp, {"a": {"step": "build"}, "b": {"step": "pr"}})
    check(join(runs, "a") == "", "A (record at build) joins the queue first and has its turn")
    time.sleep(0.05)
    check(join(runs, "b") == "a", "B joins later at pr and waits behind A")
    check(names(runs) == ["a", "b"] and json.load(open(os.path.join(runs, "a.json")))["step"] == "pr",
          "pr_turn --list order stays A, B and A's record says pr")

with tempfile.TemporaryDirectory() as tmp:
    runs = world(tmp, {"a": {"step": "build"}, "b": {"step": "pr"}})
    join(runs, "a", joined=False)
    time.sleep(0.05)
    join(runs, "b")
    check(names(runs) == ["b"], "negative control: with no join A's ticket is dropped and B goes first (the #4523 bug)")

with tempfile.TemporaryDirectory() as tmp:
    runs = world(tmp, {"a": {"step": "pr"}, "m": {"step": "pr", "release": "merged"}})
    join(runs, "m")
    time.sleep(0.05)
    join(runs, "a")
    check(names(runs) == ["a"], "negative control: a merged goal's ticket is still dropped")
sys.exit(1 if failed else 0)
