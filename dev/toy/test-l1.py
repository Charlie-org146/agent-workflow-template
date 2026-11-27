#!/usr/bin/env python3
# reads: skills/workflow-regression/scripts/regression.py skills/workflow-regression/scripts/completion.py
# reads: skills/workflow-regression/scripts/tiers.py skills/workflow-regression/scripts/runs.py dev/toy/lvl_fixture.py
"""v110-lvl-l1: what a goal-tier run picks on an armed table (lines 1 and 4). usage: test-l1.py [select]

Every repository here is a temporary one with its own HOME and a stand-in gh; nothing reads the live loop records."""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.dont_write_bytecode = True
from lvl_fixture import RISKS, Repo, check, done, entry, row, sha  # noqa: E402

OURS = "# Written by workflow-regression (regression.py workflow). fixture\nname: regression-pr\n"
FLOW = ".github/workflows/regression-pr.yml"


def levelled(specs, armed=True):
    """A repository whose rows each name their own data file. specs: (id, level, risk[, old word])."""
    rows, entries = [], []
    for spec in specs:
        key, level, risk = spec[:3]
        old = spec[3] if len(spec) > 3 else "land"
        rows.append(row(key, old, command="test -f data/%s" % key))
        timed = dict(seconds="1.0", cmdhash=sha("test -f data/%s" % key), reason="time:1.0") if level == "L0" else {}
        entries.append(entry(key, old, level, risk, **timed))
    rows.append(row("lvl-armed", command="test -f data/lvl-armed"))
    entries.append(entry("lvl-armed"))
    repo = Repo(rows, entries, [x for x in RISKS if not x.startswith("row")])  # no listed row without a table row
    for r in rows:
        repo.write("data/" + r["id"], r["id"])
    if armed:
        repo.write(FLOW, OURS)
    repo.commit()
    repo.git("checkout", "-q", "-b", "loop/l1")
    return repo


def touch(repo, *keys):
    for key in keys:
        repo.write("data/" + key, key + " changed\n")
    repo.commit("touch " + " ".join(keys))


def ran(said):
    return {m for m in re.findall(r"^(?:PASS|FAIL|KNOWN) ([a-z0-9-]+)", said, re.M)}


def pr_run(repo):
    """The pull request shard's command."""
    return repo.run("run", "nightly", "--reuse", "--tier", "goal")


def goal_run(repo):
    """A goal lane's local run."""
    return repo.run("run", "land", "--reuse", "--tier", "goal")


THREE = [("zero", "L0", "none"), ("one", "L1", "none"), ("two", "L2", "none")]


def select():
    repo = levelled(THREE)
    touch(repo, "zero", "one", "two")
    _, said = pr_run(repo)
    check(ran(said) >= {"zero", "one"} and "two" not in ran(said),
          "line 1: a change reaching an L0, an L1 and an L2 row runs the L0 and L1 rows on the pull request and not the L2 row", said)
    repo.close()

    repo = levelled(THREE)
    touch(repo, "zero", "one", "two")
    _, said = goal_run(repo)
    check(ran(said) >= {"zero"} and not ran(said) & {"one", "two"}, "a goal lane's local run on an armed table runs the L0 rows only",
          said)
    repo.close()

    repo = levelled(THREE, armed=False)
    touch(repo, "zero", "one", "two")
    _, said = goal_run(repo)
    check(ran(said) >= {"zero", "one", "two"}, "control: with no workflow of ours the table is not armed and runs as before", said)
    repo.close()

    specs = THREE + [("hidden", "L1", "private"), ("kept", "L1", "private"), ("guard", "L1", "security")]  # a tagged row is L1
    repo = levelled(specs)
    touch(repo, "one")
    _, said = pr_run(repo)
    check(ran(said) >= {"one", "hidden", "kept"} and "guard" not in ran(said),
          "line 4: a change reaching no private row runs every private row, and not an unreached security row", said)
    touch(repo, "zero")
    _, said = pr_run(repo)
    check(ran(said) >= {"hidden", "kept"} and "REUSED" not in said.split("ROWS:")[0],
          "line 4: a private row that passed before runs again, never reused", said)
    repo.close()

    repo = levelled(specs)
    touch(repo, "kept")
    _, said = pr_run(repo)
    check("kept" in ran(said) and "hidden" not in ran(said), "a change reaching a private row runs it, not the other private rows",
          said)
    repo.close()

    repo = levelled(specs)
    touch(repo, "guard", "two")
    _, said = pr_run(repo)
    check("guard" in ran(said) and "two" not in ran(said), "a reached security row runs; a reached untagged L2 row does not", said)
    repo.close()

    repo = levelled(specs)
    repo.write(".loop/regression-limits.tsv", "hidden\tnightly\tfixture\n")
    repo.commit("limits")
    touch(repo, "one")
    said = "".join(repo.run("run", "nightly", "--reuse", "--tier", "goal", LOOP_PR_SHARD="%d/2" % n)[1] for n in (0, 1))
    check("hidden" in ran(said) and said.count("NOTE hidden: listed nightly in regression-limits.tsv but tagged private") == 2,
          "a private row listed nightly still runs on L1, with one NOTE on each shard's run", said)
    repo.close()

    repo = levelled(specs)
    touch(repo, "zero", "hidden", "guard", "kept")
    _, said = goal_run(repo)
    check(not ran(said) & {"hidden", "kept", "guard"}, "a goal lane's L0 run adds no security or private row", said)
    repo.close()

    for word, want in (("L0", {"zero"}), ("L1", {"zero", "one", "lvl-armed"}), ("L2", {"zero", "one", "two", "lvl-armed"})):
        repo = levelled(THREE)
        _, said = repo.run("run", word)
        check(ran(said) == want, "run %s, typed, runs the rows of that level" % word, said)
        repo.close()


if __name__ == "__main__":
    for name in sys.argv[1:] or ["select"]:
        {"select": select}[name]()
    sys.exit(done())
