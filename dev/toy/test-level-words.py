#!/usr/bin/env python3
# reads: skills/workflow-regression/scripts/tiers.py skills/workflow-regression/scripts/level_words.py
"""G4-2 (v110-lvl-retire-old-words-2): one set of level words, L0, L1 and L2.

Runs in a temporary folder with its own HOME, no network. Case goal: the goal_levels table (plan D2a), on a levelled table and on one
that is not. usage: test-level-words.py [goal]  (no argument: all)"""
import contextlib
import io
import json
import os
import sys
import tempfile
import types

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.dont_write_bytecode = True

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(root, "skills", "workflow-regression", "scripts"))
os.chdir(root)
os.environ["HOME"] = os.environ["USERPROFILE"] = tempfile.mkdtemp(prefix="test-level-words-home.")
failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def folder(armed, goal_levels):
    top = tempfile.mkdtemp(prefix="test-level-words.")
    os.makedirs(os.path.join(top, ".loop"))
    os.makedirs(os.path.join(top, ".github", "workflows"))
    head = "# id\tlevel\tcommand\tgoal\tseen_red\tdescription\tcategory\tlink\n"
    open(os.path.join(top, ".loop", "regression.tsv"), "w").write(head + ("lvl-armed\tland\ttrue\t-\t2026-01-01\tA row.\tcriterion\t\n" if armed else ""))
    open(os.path.join(top, ".github", "workflows", "regression-pr.yml"), "w").write("# Written by workflow-regression\n")
    open(os.path.join(top, ".loop", "config.json"), "w").write(json.dumps({"goal_levels": goal_levels} if goal_levels else {}))
    return top


def plan(armed, value):
    """What a goal lane plans from for this goal_levels value: (target, stdout, stderr, exit code or None)."""
    import tiers
    top = folder(armed, value)
    out, err, code, got = io.StringIO(), io.StringIO(), None, None
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            got = tiers.target(top, types.SimpleNamespace(tier="goal", target="land"))
    except SystemExit as stop:
        code = stop.code
    return got, out.getvalue(), err.getvalue(), code


def goal():
    print("== D2a: the goal_levels table")
    # Value: protects=a goal lane plans from the level the setting names, and an old word is read and said; fails_when=L0, L1 or L2 is
    #   ignored, or an old word is read in silence, or a bad value passes on a levelled table; why_new=the setting knew only land and nightly
    for value, want in (("land", "L1"), ("nightly", "L2"), ("L0", "L0"), ("L1", "L1"), ("L2", "L2")):
        got, out, err, code = plan(True, value)
        old = value in ("land", "nightly")
        check(got == want and code is None and (("GOAL_LEVELS_OLD" in out) == old), "levelled table: goal_levels %r plans from %s%s" % (value, want, " and says so" if old else ""))
    for armed in (True, False):
        got, out, err, code = plan(armed, None)
        check(got == "land" and code is None and not out + err, "goal_levels not set: a goal lane plans as it always did, in silence (%s table)" % ("levelled" if armed else "not levelled"))
    got, out, err, code = plan(True, "weekly")
    check(code not in (None, 0) and "REFUSED (GOAL_LEVELS_BAD)" in err and "Nothing was run." in err, "levelled table: goal_levels 'weekly' is refused before any work")
    for value, want in (("land", "land"), ("nightly", "nightly"), ("L0", "land"), ("L1", "nightly"), ("L2", "nightly")):
        got, out, err, code = plan(False, value)
        check(got == want and code is None and "GOAL_LEVELS_OLD" not in out, "table not levelled: goal_levels %r runs as %s" % (value, want))
    got, out, err, code = plan(False, "weekly")
    check(got == "land" and code is None and "GOAL_LEVELS" in out + err, "table not levelled: goal_levels 'weekly' runs as land and is warned about")


def settings():
    print("== R1: the setting's documented words, the survey's values and this repo's config")
    # Value: protects=goal_levels is documented, accepted when borrowed and set with the new words only; fails_when=the table,
    #   the survey or this repo's config still speaks land and nightly
    import re
    import subprocess
    sdir = os.path.join(root, "skills", "workflow-setup", "scripts")
    ref = subprocess.run([sys.executable, os.path.join(sdir, "settings.py"), "reference"], capture_output=True, text=True).stdout
    row = [line for line in ref.splitlines() if line.startswith("| `goal_levels` |")]
    check(len(row) == 1 and "| `L0` |" in row[0] and all(w in row[0] for w in ("L0", "L1", "L2")), "settings.py documents goal_levels with the default L0 and the values L0, L1 and L2")
    check(len(row) == 1 and not re.search(r"\b(land|nightly|covered|draft)\b", row[0]), "the goal_levels row uses none of the old words")
    sys.path.insert(0, sdir)
    import survey
    check(all(survey.fits("goal_levels", v, "L0") for v in ("L0", "L1", "L2", "land", "nightly")) and not survey.fits("goal_levels", "weekly", "L0"),
          "the survey borrows L0, L1, L2 and the two old words, and refuses another value")
    cfg = json.load(open(os.path.join(root, ".loop", "config.json")))
    check(cfg.get("goal_levels") == "L1", "this repo's config sets goal_levels to L1 (the level that selects what land did)")
    page = open(os.path.join(root, "docs", "wiki", "How-to-use-Setup.md"), encoding="utf-8").read()
    line = [l for l in page.splitlines() if l.startswith("| `goal_levels` |")]
    check(len(line) == 1 and "L0 (the default), L1 or L2" in line[0] and "`L0` | default" in line[0], "the How-to-use-Setup row for goal_levels names L0, L1 and L2 and the default L0")


def moved():
    print("== TD2333: an 8-cell record line against a 9-cell one reads as moved")
    # Value: protects=after the upgrade every row is re-picked once (more rows, never fewer); a guard that holds on today's code
    import subprocess
    import lanes
    top = tempfile.mkdtemp(prefix="test-level-words-git.")
    sh = lambda *a: subprocess.run(["git", "-C", top, "-c", "user.email=t@t", "-c", "user.name=t"] + list(a), capture_output=True, text=True)
    sh("init", "-q", "-b", "main")
    os.makedirs(os.path.join(top, ".loop"))
    record = os.path.join(top, ".loop", "regression-relevel.tsv")
    old = "a\tland\tL1\tnone\t\t\t\tdefault"
    open(record, "w").write("# id\told\tlevel\trisk\tcovers\tseconds\tcmdhash\treason\n" + old + "\nb\tland\tL1\tnone\t\t\t\tdefault\n")
    sh("add", "-A"); sh("commit", "-q", "-m", "eight cells")
    at = sh("rev-parse", "HEAD").stdout.strip()
    open(record, "w").write("# id\told\tlevel\trisk\tcovers\tseconds\tcmdhash\treason\tstate\n" + old + "\t\nb\tland\tL1\tnone\t\t\t\tdefault\t\n")
    memo = {}
    check(lanes.entry_moved(top, at, "a", memo) and lanes.entry_moved(top, at, "b", memo), "a row's 8-cell line at the branch point against the same row's 9-cell line now reads as moved")
    memo = {}
    open(record, "w").write("# id\told\tlevel\trisk\tcovers\tseconds\tcmdhash\treason\n" + old + "\nb\tland\tL1\tnone\t\t\t\tdefault\n")
    check(not lanes.entry_moved(top, at, "a", memo), "an unchanged line does not read as moved")


def coverlevel():
    print("== R3: a covered row's stored level is the one its covers give")
    # Value: protects=line 3 (a covered row takes the highest level of the rows its list names); fails_when=a hand-edited record
    #   keeps a covered row at a level its covers don't give, and nothing says so
    from lvl_fixture import Repo, entry, row
    base = [row("alpha"), row("beta"), row("done-x", level="covered", command="proved elsewhere")]

    def run(stored, covers, alpha_level="L1"):
        alpha = entry("alpha", level=alpha_level, seconds="1.0" if alpha_level == "L0" else "", cmdhash=__import__("hashlib").sha1(b"true").hexdigest() if alpha_level == "L0" else "")
        repo = Repo(base, [alpha, entry("beta", level="L2"), entry("done-x", old="covered", level=stored, covers=covers, reason="covers")], risks=["label\tsecurity\tsecurity\tfixture label"])
        repo.commit()
        status, said = repo.run("run", "alpha")
        repo.close()
        return status, said
    status, said = run("L1", "alpha")
    check(status == 0, "control: a covered row stored at the level its covers give runs")
    status, said = run("L2", "alpha")
    check(status == 2 and "LEVELS_COVER_LEVEL" in said and "done-x" in said and "L1" in said and "level done-x --covers" in said,
          "a covered row stored at L2 over an L1 cover is refused, naming the level it should have and the repair")
    status, said = run("L1", "beta")
    check(status == 2 and "LEVELS_COVER_LEVEL" in said, "a covered row stored at L1 over an L2 cover is refused")
    repo = Repo(base, [entry("alpha"), entry("beta", level="L2"), entry("done-x", old="covered", level="L2", covers="alpha", reason="covers")], risks=["label\tsecurity\tsecurity\tfixture label"])
    repo.commit()
    fix, _ = repo.run("level", "done-x", "--covers", "alpha")
    status, said = repo.run("run", "alpha")
    check(fix == 0 and status == 0 and repo.entries()["done-x"]["level"] == "L1", "the repair the refusal names (level done-x --covers alpha) rewrites the stored level and the table runs")
    repo.close()
    status, said = run("L1", "alpha,beta")
    check(status == 2 and "LEVELS_COVER_LEVEL" in said, "the highest of two covers decides: L2, not the stored L1")
    status, said = run("L0", "alpha", alpha_level="L0")
    check(status == 0, "a covered row over an L0 cover is L0 when stored as L0")


def superset():
    print("== TD2334: on this repo's real table an old word's replacement selects at least the rows the old word did")
    # Value: protects=reading "land" or "nightly" on a levelled table never plans a goal lane from fewer rows; fails_when=an old
    #   word is replaced by a level that selects fewer rows (land read as L0 planned from 3 rows instead of 720)
    import level_words
    import regression
    import runs
    rows = regression.read_rows(root)
    for old, same in (("land", False), ("nightly", True)):
        was = {r["id"] for r in runs.chosen(rows, old)}
        target = level_words.goal_target(old, True)
        now = {r["id"] for r in runs.chosen(rows, target)}
        check(was <= now and (not same or was == now) and len(was) > 100,
              "goal_levels %r reads as %s: %d rows before, %d now, %s" % (old, target, len(was), len(now), "the same set" if same else "a superset"))
    check(len({r["id"] for r in runs.chosen(rows, "L0")}) < 20, "L0 keeps only L0's rows")


def state():
    print("== R4: the record's state column")
    # Value: protects=a draft's mark is in its own column and records written before still read; fails_when=the ninth cell is refused, a
    #   bad state passes, a mismatch with the table's own word passes, or a writer still writes eight cells
    from lvl_fixture import Repo, entry, row
    risks = ["label\tsecurity\tsecurity\tfixture label"]

    def nine(e, state_cell):
        return dict(e, state=state_cell)

    def run(rows, lines):
        repo = Repo(rows, [], risks)
        repo.write(".loop/regression-relevel.tsv", "".join(lines))
        repo.commit()
        got = repo.run("run", "alpha")
        repo.close()
        return got
    cols = ("id", "old", "level", "risk", "covers", "seconds", "cmdhash", "reason")
    line = lambda e, extra=(): "\t".join([e[c] for c in cols] + list(extra)) + "\n"
    base = [row("alpha"), row("drf", level="draft")]
    a, d = entry("alpha"), entry("drf", old="draft")
    status, said = run(base, [line(a), line(d)])
    check(status == 0, "control: eight-cell lines (a record written before this goal) still read, and the draft's state comes from the table's own word")
    status, said = run(base, [line(a, [""]), line(d, ["draft"])])
    check(status == 0, "nine-cell lines with a blank state and a draft state read")
    status, said = run(base, [line(a, ["bogus"]), line(d, ["draft"])])
    check(status == 2 and "LEVELS_BAD_STATE" in said and "alpha" in said, "a state that is neither blank nor draft is refused (LEVELS_BAD_STATE)")
    status, said = run(base, [line(a, [""]), line(d, [""])])
    check(status == 2 and "LEVELS_STATE_MISMATCH" in said and "drf" in said, "a draft row (table word draft) whose nine-cell state is blank is a mismatch")
    status, said = run(base, [line(a, ["draft"]), line(d, ["draft"])])
    check(status == 2 and "LEVELS_STATE_MISMATCH" in said and "alpha" in said, "a land row whose nine-cell state says draft is a mismatch")
    repo = Repo([row("alpha")], [entry("alpha")], risks)
    repo.commit()
    done, said = repo.run("level", "alpha", "--test-level", "L2")
    text = repo.read(".loop/regression-relevel.tsv")
    check(done == 0 and all(len(l.split("\t")) == 9 for l in text.splitlines()), "a writer writes nine cells, header included")
    repo.close()


cases = {"goal": goal, "settings": settings, "moved": moved, "coverlevel": coverlevel, "superset": superset, "state": state}
for name in (sys.argv[1:] or list(cases)):
    cases[name]()
print("%d failed" % len(failed))
print("ALL PASS" if not failed else "FAILED")
sys.exit(1 if failed else 0)
