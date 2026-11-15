#!/usr/bin/env python3
# reads: skills/workflow-regression/scripts/lanes.py skills/workflow-regression/scripts/narrow.py
"""Proves a change to .loop/config.json affects a row only when the row (or a script it runs) names a changed key.
Two rows in a temp repo both read the config; one names min_free_memory_gb, the other other_key (#4321)."""
import os
import subprocess
import sys
import tempfile

here = os.environ.get("TOY_HERE") or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(here, "skills", "workflow-regression", "scripts"))
import lanes  # noqa: E402
import tiers  # noqa: E402

fails = []


def git(repo, *args):
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    return subprocess.run(["git", "-c", "commit.gpgsign=false"] + list(args), cwd=repo, env=env, capture_output=True, text=True,
                          check=True).stdout.strip()


def put(repo, rel, text):
    os.makedirs(os.path.dirname(os.path.join(repo, rel)), exist_ok=True)
    with open(os.path.join(repo, rel), "w", newline="\n") as handle:
        handle.write(text)


def check(name, ok):
    print(("PASS " if ok else "FAIL ") + name)
    if not ok:
        fails.append(name)


BASE = '{\n  "min_free_memory_gb": 3.0,\n  "other_key": 1,\n  "min_free_memory_gb": 3.0\n}\n'
SCRIPT = 'import json\njson.load(open(".loop/config.json"))["%s"]\n'
ROW = "#!/bin/bash\n# reads: skills/x/scripts/%s.py .loop/config.json\npython3 skills/x/scripts/%s.py\n"


def stale_rows(after):
    """The row ids plan() reruns after config.json goes from BASE to `after`."""
    with tempfile.TemporaryDirectory() as repo:
        git(repo, "init", "-q", "-b", "main")
        put(repo, ".loop/config.json", BASE)
        for name, key in (("a", "min_free_memory_gb"), ("b", "other_key")):
            put(repo, "skills/x/scripts/%s.py" % name, SCRIPT % key)
            put(repo, "dev/toy/r%s.sh" % name, ROW % (name, name))
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "base")
        head = git(repo, "rev-parse", "HEAD")
        selected = [{"id": n, "command": "bash dev/toy/r%s.sh" % n} for n in "ab"]
        record = {"rows": {n: {"status": "PASS", "commit": head} for n in "ab"}}
        put(repo, ".loop/config.json", after)
        git(repo, "commit", "-qam", "config")
        run, reused, notes, why = lanes.plan(repo, selected, record, {}, {})
        memo, cache = {"tsv": {}, "known": {}, "moved": []}, {}
        lane = sorted(r["id"] for r in selected if tiers.reason(repo, r, record, True, head, cache, memo))  # what the pr lane runs
        assert lane == sorted(run), (lane, sorted(run))
        return sorted(run)


check("a removed duplicate min_free_memory_gb reruns only the row that names it",
      stale_rows('{\n  "min_free_memory_gb": 3.0,\n  "other_key": 1\n}\n') == ["a"])
check("a changed value reruns only the row that names its key",
      stale_rows(BASE.replace('"other_key": 1', '"other_key": 2')) == ["b"])
check("an added key nobody reads reruns no row", stale_rows(BASE.replace("}\n", ', "brand_new": 1}\n')) == [])
check("a removed key reruns the row that names it", stale_rows('{"min_free_memory_gb": 3.0, "min_free_memory_gb": 3.0}') == ["b"])
check("a reformat-only change reruns no row", stale_rows(BASE.replace("\n  ", " ")) == [])
check("a config that does not parse reruns every row that reads it", stale_rows("{ not json") == ["a", "b"])
sys.exit(1 if fails else 0)
