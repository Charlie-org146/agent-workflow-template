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


def check(ok, text, detail=""):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)
        detail and print("  " + str(detail)[:500].replace("\n", "\n  "))


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
    for value, level in (("land", "L1"), ("nightly", "L2")):
        got, out, err, code = plan(True, value)
        check(out.strip() == 'SETTINGS (GOAL_LEVELS_OLD): goal_levels "%s" in .loop/config.json is read as %s. Fix: set "goal_levels": "%s" and commit it.' % (value, level, level),
              "the old-word line for %r names exactly what to set: %s" % (value, level))
    got, out, err, code = plan(True, "weekly")
    check(code not in (None, 0) and "REFUSED (GOAL_LEVELS_BAD)" in err and "Nothing was run." in err, "levelled table: goal_levels 'weekly' is refused before any work")
    check(err.strip() == "REFUSED (GOAL_LEVELS_BAD): goal_levels is 'weekly' in .loop/config.json; the values are L0, L1 and L2. Fix: set one there and commit it. Nothing was run.",
          "the refusal lists all three levels, L0, L1 and L2, in exactly this text")
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
    check(len(line) == 1 and "L0 (the default), L1 or L2" in line[0] and "| `L0` | **overridden:** `L1` |" in line[0], "the How-to-use-Setup row for goal_levels names L0, L1 and L2, the default L0 and this repository's override L1")


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


def drafts():
    print("== R5: making and readying a draft")
    # Value: protects=a draft is made with the level it will have and readied by a command, and every refusal leaves both tables as they were;
    #   fails_when=add --level draft needs no --test-level, a refusal still writes, --ready readies a placeholder command, or the state stays draft
    from lvl_fixture import Repo, entry, row
    risks = ["label\tsecurity\tsecurity\tfixture label"]
    repo = Repo([row("alpha")], [entry("alpha")], risks)
    repo.commit()
    before = (repo.read(".loop/regression.tsv"), repo.read(".loop/regression-relevel.tsv"))
    done, said = repo.run("add", "drf", "--level", "draft", "--command", "echo write a test")
    check(done != 0 and "LEVELS_NO_STAGE" in said and "--test-level L1" in said and "add drf --level draft --test-level" in said,
          "add --level draft without --test-level is refused (LEVELS_NO_STAGE) with the values and the whole command", said)
    check((repo.read(".loop/regression.tsv"), repo.read(".loop/regression-relevel.tsv")) == before, "the refusal changed neither table")
    done, said = repo.run("add", "drf", "--level", "draft", "--test-level", "L2", "--command", "echo write a test")
    check(done == 0, "add --level draft --test-level L2 makes the draft", said)
    cells = [l.split("\t") for l in repo.read(".loop/regression-relevel.tsv").splitlines() if l.startswith("drf\t")]
    check(len(cells) == 1 and cells[0][1:3] == ["draft", "L2"] and cells[0][8] == "draft", "the record holds old draft, level L2 and state draft", cells)
    done, said = repo.run("level", "drf", "--ready")
    check(done != 0 and "real command" in said, "--ready refuses a draft whose command is still the placeholder, and says a real command is needed", said)
    done, said = repo.run("add", "drf", "--level", "draft", "--test-level", "L2", "--command", "true")
    done, said = repo.run("level", "drf", "--ready")
    check(done == 0 and "drf" in said and "L2" in said, "--ready readies a draft with a real command and prints what it changed", said)
    cells = [l.split("\t") for l in repo.read(".loop/regression-relevel.tsv").splitlines() if l.startswith("drf\t")]
    table = [l.split("\t") for l in repo.read(".loop/regression.tsv").splitlines() if l.startswith("drf\t")]
    check(len(cells) == 1 and cells[0][1] == "nightly" and cells[0][2] == "L2" and cells[0][8] == "" and table[0][1] == "nightly",
          "afterwards the state is blank and the table's own word is the level's (nightly for L2)", (cells, table))
    done, said = repo.run("level", "alpha", "--ready")
    check(done != 0 and "not a draft" in said, "--ready on a row that is not a draft is refused and says so", said)
    repo.close()


def notrun():
    print("== R5/R6: not run: draft")
    # Value: protects=a draft is named on every run route and never run; fails_when=a route is silent about a draft, names it twice, gives it a
    #   result line, or runs its command (the command writes a file)
    from lvl_fixture import Repo, entry, row
    risks = ["label\tsecurity\tsecurity\tfixture label"]
    rows = [row("alpha"), row("drf", level="draft", command="touch RAN-DRAFT")]
    repo = Repo(rows, [entry("alpha"), entry("drf", old="draft", level="L1")], risks)
    repo.commit()
    for args in (("run", "land"), ("run", "nightly"), ("run", "drf"), ("run", "nightly", "--reuse"), ("run", "land", "--reuse", "--tier", "goal")):
        done, said = repo.run(*args)
        lines = [l for l in said.splitlines() if "drf" in l]
        check(lines == ["not run: draft drf"], "%s: the draft is named only in its own line (not run: draft drf)" % " ".join(args), said)
    check(not os.path.exists(os.path.join(repo.path, "RAN-DRAFT")), "no route ran the draft's command")
    done, said = repo.run("run", "--ids", "no-such-row")
    check(done != 0 and "not run: draft drf" in said.splitlines(), "a refused run (no such row) still names the draft first (R6: before any early exit)", said)
    repo.close()


def plaindraft():
    print("== R5: on a table that is not levelled a draft is added without --test-level")
    # Value: protects=add --level draft works where --test-level is refused; fails_when=the stage is demanded on a table with no record
    from lvl_fixture import Repo, row
    repo = Repo([row("alpha")], None, None)
    repo.commit()
    done, said = repo.run("add", "drf", "--level", "draft", "--command", "echo write a test")
    check(done == 0 and "LEVELS_NO_STAGE" not in said and "drf" in (repo.read(".loop/regression.tsv") or ""), "a draft is added without --test-level on a table that is not levelled", said)
    repo.close()


def syncdraft():
    print("== R5: sync --write drafts")
    # Value: protects=a drafted row is a draft at L1 whose state says so, and the DRAFT line names the command that readies it;
    #   fails_when=the drafted row has no draft state or a level other than L1, or the line says nothing of --ready or "not enforced"
    from lvl_fixture import Repo, entry, row
    repo = Repo([row("alpha")], [entry("alpha")], ["label\tsecurity\tsecurity\tfixture label"])
    repo.write("docs/wiki/Page.md", "# Page\n\n## Requirements\n\n- ABC-1: it works\n")
    repo.commit()
    done, said = repo.run("sync", "--write")
    line = [l for l in said.splitlines() if l.startswith("DRAFT ABC-1")]
    check(len(line) == 1 and "level ABC-1 --ready" in line[0] and "not enforced" in line[0], "the DRAFT line names the ready command and says not enforced", said)
    cells = [l.split("\t") for l in (repo.read(".loop/regression-relevel.tsv") or "").splitlines() if l.startswith("ABC-1\t")]
    check(len(cells) == 1 and cells[0][1:3] == ["draft", "L1"] and cells[0][8:] == ["draft"], "the drafted row is draft, L1, state draft in the record", cells)
    repo.close()


def enforced():
    print("== R7: a requirement held only by drafts or covered rows is not enforced")
    # Value: protects=health says "not enforced" for a requirement no run-able row holds, whatever the sync line is; fails_when=health
    #   shows such a requirement as a draft FAIL or drops it, or a requirement with a land row is reported not enforced
    import subprocess
    from lvl_fixture import Repo, entry, row, ROOT
    page = "# Page\n\n## Requirements\n\n- ABC-1: **Unreviewed** held by a draft\n- ABC-2: **Unreviewed** held by a covered row\n- ABC-3: **Unreviewed** held by a land row\n"
    rows = [row("ABC-1", level="draft"), row("ABC-2", level="covered", command="read by a person"), row("ABC-3"), row("cov-src")]
    ents = [entry("ABC-1", old="draft"), entry("ABC-2", old="covered", covers="cov-src"), entry("ABC-3"), entry("cov-src")]
    repo = Repo(rows, ents, ["label\tsecurity\tsecurity\tfixture label"])
    repo.write("docs/wiki/Page.md", page)
    repo.write(".loop/config.json", "{}")
    repo.commit()
    health = os.path.join(ROOT, "skills", "workflow-health", "scripts", "health.py")
    got = subprocess.run([sys.executable, health, "check", "--json"], cwd=repo.path, env=repo.env, capture_output=True, text=True, timeout=300)
    try:
        found = {r["subject"]: r for r in json.loads(got.stdout)["rows"] if r.get("subject", "").startswith("ABC-")}
    except ValueError:
        found = {}
    for key, state in (("ABC-1", "FAIL"), ("ABC-2", "WARN")):  # a draft-only requirement keeps today's FAIL (R7: no weaker); a covered-only one was silent before
        item = found.get(key, {})
        check(item.get("state") == state and "not enforced" in item.get("detail", ""), "%s shows %s, not enforced" % (key, state), item or "no row for %s among %s" % (key, sorted(found)))
    check("ABC-3" not in found or "not enforced" not in found["ABC-3"].get("detail", ""), "a requirement with a land row is not reported not enforced")
    repo.close()


def critcover():
    print("== R8: a covered row is met only when its covers are")
    # Value: protects=criteria applies a covered row's covers: it is met when every cover passes at HEAD and unmet when a cover fails or is a
    #   draft; fails_when=a covered row is met whatever its covers do
    from lvl_fixture import Repo, entry, row
    page = "# Page\n\n## Requirements\n\n- ABC-1: **Unreviewed** covers a passing row\n- ABC-2: **Unreviewed** covers a failing row\n- ABC-3: **Unreviewed** covers a draft\n"
    rows = [row("lvl-armed"), row("good"), row("bad", command="false"), row("drf", level="draft"),
            row("ABC-1", level="covered", command="read by a person"), row("ABC-2", level="covered", command="read by a person"),
            row("ABC-3", level="covered", command="read by a person")]
    ents = [entry("lvl-armed"), entry("good"), entry("bad"), entry("drf", old="draft"), entry("ABC-1", old="covered", covers="good"),
            entry("ABC-2", old="covered", covers="bad"), entry("ABC-3", old="covered", covers="drf")]
    repo = Repo(rows, ents, ["label\tsecurity\tsecurity\tfixture label"])
    repo.write("docs/wiki/Page.md", page)
    repo.write(".github/workflows/regression-pr.yml", "# Written by workflow-regression\n")
    repo.commit()
    done, said = repo.run("criteria")
    lines = said.splitlines()
    check(not any(l.startswith("ABC-1") for l in lines), "a covered row whose cover passes is met", said)
    check(any(l.startswith("ABC-2") and "bad" in l for l in lines), "a covered row whose cover fails is unmet, and names the cover", said)
    check(any(l.startswith("ABC-3") and "drf" in l for l in lines), "a covered row whose cover is a draft is unmet, and names the cover", said)
    os.remove(os.path.join(repo.path, ".github", "workflows", "regression-pr.yml"))
    done, said = repo.run("criteria")
    check("ABC-2" not in said and "ABC-3" not in said, "R10: levelled but not armed, a covered row is not checked against its covers (what ran before)", said)
    repo.close()


def unarmed():
    print("== R10: what runs switches on armed(), not on levelled")
    # Value: protects=a levelled table that is not armed (no lvl-armed row) plans from land for goal_levels L0, as before this goal;
    #   fails_when=an unarmed levelled repository takes the level words
    import completion, tiers
    from lvl_fixture import Repo, entry, row
    repo = Repo([row("a"), row("b")], [entry("a"), entry("b")], ["label\tsecurity\tsecurity\tfixture label"])
    repo.write(".loop/config.json", json.dumps({"goal_levels": "L0"}))
    repo.commit()
    args = types.SimpleNamespace(tier=True, target="land")
    check(not completion.armed(repo.path), "control: the fixture is levelled and not armed")
    got = tiers.target(repo.path, args)
    check(got == "land", "levelled but unarmed, goal_levels L0: the lane plans from land", got)
    repo.write(".loop/config.json", json.dumps({"goal_levels": "land"}))
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        got = tiers.target(repo.path, args)
    check(got == "land" and out.getvalue() == "", "levelled but unarmed, the old word land: no translation line, still land", out.getvalue())
    repo.close()


def writers():
    print("== R4: fill and an interrupted two-file write keep the state column")
    # Value: protects=a record written by fill, or finished from a pending mark, has nine cells whose state follows the table's own word;
    #   fails_when=fill leaves the draft's state blank, or an interrupted --ready finishes with a stale state
    import subprocess
    from lvl_fixture import Repo, entry, row, REG
    risks = ["label\tsecurity\tsecurity\tfixture label"]
    repo = Repo([row("alpha"), row("drf", level="draft")], [entry("alpha")], risks)
    repo.commit()
    done, said = repo.run("levels", "--fill")
    cells = {l.split("\t")[0]: l.split("\t") for l in repo.read(".loop/regression-relevel.tsv").splitlines() if l and l[0] != "#"}
    check(len(cells.get("drf", [])) == 9 and cells["drf"][8] == "draft" and cells["drf"][1] == "draft", "levels --fill adds the draft's entry as nine cells with state draft", cells.get("drf"))
    repo.close()
    repo = Repo([row("drf", level="draft", command="true")], [entry("drf", old="draft")], risks)
    repo.commit()
    code = ("import sys; sys.path.insert(0, %r); import levels_write as w, regression\n"
            "real = w.put\n"
            "def put(root, name, text):\n"
            "    if name == 'regression.tsv': raise OSError('stopped')\n"
            "    real(root, name, text)\n"
            "w.put = put\n"
            "sys.argv = ['regression.py', 'level', 'drf', '--ready']\n"
            "sys.exit(regression.main())\n") % REG
    got = subprocess.run([sys.executable, "-c", code], cwd=repo.path, env=repo.env, capture_output=True, text=True)
    check(got.returncode != 0 and "LEVELS_UNEXPECTED" in got.stdout + got.stderr, "control: the --ready write stops between the two files", got.stdout + got.stderr)
    done, said = repo.run("levels", "--fill")
    cells = [l.split("\t") for l in repo.read(".loop/regression-relevel.tsv").splitlines() if l.startswith("drf\t")]
    table = [l.split("\t") for l in repo.read(".loop/regression.tsv").splitlines() if l.startswith("drf\t")]
    check(done == 0 and len(cells[0]) == 9 and cells[0][8] == "" and cells[0][1] == "land" and table[0][1] == "land", "the pending mark finishes the --ready: both files agree, state blank", (cells, table, said))
    repo.close()


def coverstate():
    print("== R8: a covered row shows the worst state of its covers, with a commit")
    # Value: protects=the Runs of a covered row is the worst of its covers bound to a commit, never a bare green; results keep their commit;
    #   fails_when=a covered row shows its own placeholder, a legacy record counts as proof, or PASS wins over FAIL
    import subprocess
    from lvl_fixture import Repo, entry, row, REG
    risks = ["label\tsecurity\tsecurity\tfixture label"]
    rows = [row("lvl-armed"), row("a"), row("b", command="false"), row("drf", level="draft"), row("c", level="covered", command="read by a person"),
            row("d", level="covered", command="read by a person"), row("e", level="covered", command="read by a person")]
    ents = [entry("lvl-armed"), entry("a"), entry("b"), entry("drf", old="draft"), entry("c", old="covered", covers="a"),
            entry("d", old="covered", covers="a,b"), entry("e", old="covered", covers="a,drf")]
    repo = Repo(rows, ents, risks)
    repo.write(".github/workflows/regression-pr.yml", "# Written by workflow-regression\n")
    repo.commit()

    def result(key):
        got = subprocess.run([sys.executable, os.path.join(REG, "tests.py"), "list", "--tsv"], cwd=repo.path, env=repo.env, capture_output=True, text=True)
        said = got.stdout + got.stderr
        got = [l.split("\t") for l in said.splitlines() if l.split("\t")[1:2] == [key]]
        return got[0][6] if got else said
    check(result("c").startswith("no result recorded"), "no cover has a result: no result recorded", result("c"))
    done, said = repo.run("run", "land")
    head = repo.git("rev-parse", "HEAD").stdout.strip()[:12]
    record = [l.split("\t") for l in repo.read(".loop/regression-runs.tsv").splitlines() if l.startswith("a\t")]
    check(record and len(record[0]) == 6 and record[0][5] == head, "a run record keeps the commit it ran at (sixth cell)", record)
    check(result("c").startswith("PASS " + head), "the sole cover passed at this commit: PASS with the commit", result("c"))
    check(result("d").startswith("FAIL " + head), "one cover failed: the worst state, FAIL, with its commit, not PASS", result("d"))
    check(result("e").startswith("draft"), "a cover that is a draft: draft", result("e"))
    ghost = [l for l in repo.read(".loop/regression-runs.tsv").splitlines() if l.startswith("a\t")]
    repo.write(".loop/regression-runs.tsv", repo.read(".loop/regression-runs.tsv") + "ghost\tPASS\t2026-11-27\t\t\t" + head + "\n")
    repo.write(".loop/regression-relevel.tsv", repo.read(".loop/regression-relevel.tsv") + "\t".join(["g", "covered", "L1", "none", "ghost", "", "", "covers"]) + "\n")
    repo.write(".loop/regression.tsv", repo.read(".loop/regression.tsv") + "\t".join(["g", "covered", "read by a person", "", "2026-01-01", "checks g", "criterion", ""]) + "\n")
    check(result("g").startswith("no result recorded"), "a covered row whose cover is no longer a row is no result, even with a PASS record for that id (review round 1)", result("g"))
    legacy = "".join(l.split("\t")[0] and "\t".join(l.split("\t")[:5]) + "\n" for l in repo.read(".loop/regression-runs.tsv").splitlines() if l and l[0] != "#")
    repo.write(".loop/regression-runs.tsv", "# id\tstatus\tdate\trun\tflaky\n" + legacy)
    check(result("c").startswith("no result recorded"), "a record from before the commit cell is unproven: no result recorded", result("c"))
    repo.close()


def mixedruns():
    print("== R13: a run record with 5-cell and 6-cell lines survives a union merge")
    # Value: protects=the merge repair unions regression-runs.tsv lines of both formats and keeps the later date; fails_when=the repair
    #   gives up on a pair of lines that differ only in the new commit cell, or a reader fails on a 6-cell line
    import subprocess
    from lvl_fixture import Repo, row, ROOT
    sys.path.insert(0, os.path.join(ROOT, "skills", "workflow-delivery", "scripts"))
    import mend_tables
    repo = Repo([row("a"), row("b")], None, None)
    head = "# id\tstatus\tdate\trun\tflaky\tcommit\n"
    repo.write(".loop/regression-runs.tsv", head + "a\tPASS\t2026-11-01\t\t\nb\tPASS\t2026-11-01\t\t\n")
    repo.commit("base")
    repo.git("checkout", "-q", "-b", "other")
    repo.write(".loop/regression-runs.tsv", head + "a\tPASS\t2026-11-03\t\t\nb\tPASS\t2026-11-01\t\t\n")  # an old-format line, later date
    repo.commit("old format")
    repo.git("checkout", "-q", "main")
    repo.write(".loop/regression-runs.tsv", head + "a\tPASS\t2026-11-02\t\t\tabc123456789\nb\tPASS\t2026-11-04\t\t\tabc123456789\n")  # new format
    repo.commit("new format")
    merged = repo.git("merge", "other", "--no-edit", check_it=False)
    git = lambda *a: subprocess.run(["git"] + list(a), cwd=repo.path, env=repo.env, capture_output=True, text=True)
    cwd = os.getcwd()
    os.chdir(repo.path)
    try:
        ok = mend_tables.mend(git, [".loop/regression-runs.tsv"], "other")
    finally:
        os.chdir(cwd)
    text = repo.read(".loop/regression-runs.tsv") or ""
    check(merged.returncode != 0 and ok and "a\tPASS\t2026-11-03" in text and "b\tPASS\t2026-11-04\t\t\tabc123456789" in text,
          "the repair unions a 5-cell line (later date) and a 6-cell line, keeping each id's later date", text)
    repo.close()


def swallow():
    print("== TD2346: a failing cover_results fails the run; in CI (level_words absent) a covered row shows its raw record")
    # Value: protects=an error inside level_words is never swallowed as "not installed", and the raw CI state of a covered row is known;
    #   fails_when=an ImportError or ValueError raised inside cover_results is hidden, or the CI case below changes
    import shutil, subprocess
    from lvl_fixture import Repo, entry, row, REG
    risks = ["label\tsecurity\tsecurity\tfixture label"]
    rows = [row("lvl-armed"), row("good"), row("bad", command="false"), row("c", level="covered", command="read by a person")]
    ents = [entry("lvl-armed"), entry("good"), entry("bad"), entry("c", old="covered", covers="bad")]
    repo = Repo(rows, ents, risks)
    repo.write(".github/workflows/regression-pr.yml", "# Written by workflow-regression\n")
    repo.write(".loop/regression-runs.tsv", "# id\tstatus\tdate\trun\tflaky\tcommit\nbad\tFAIL\t2026-11-27\t\t\tabc123456789\nc\tPASS\t2026-11-01\t\t\t\n")
    repo.commit()
    tests_py = os.environ.get("LW_TESTS_PY") or os.path.join(REG, "tests.py")

    def listing(fake):
        folder = tempfile.mkdtemp(prefix="test-level-words-ci.")
        shutil.copy(tests_py, os.path.join(folder, "tests.py"))
        fake and open(os.path.join(folder, "level_words.py"), "w").write(fake)
        got = subprocess.run([sys.executable, os.path.join(folder, "tests.py"), "list", "--tsv"], cwd=repo.path, env=dict(repo.env, PYTHONPATH=""),
                             capture_output=True, text=True)
        shutil.rmtree(folder, ignore_errors=True)
        return got
    for name, fake in (("ValueError", "def cover_results(*a):\n    raise ValueError('boom')\n"),
                       ("ImportError", "def cover_results(*a):\n    import no_such_module_anywhere\n")):
        got = listing(fake)
        check(got.returncode != 0 and ("boom" in got.stderr or "no_such_module_anywhere" in got.stderr), "a %s raised inside cover_results fails the run" % name, got.stderr[-300:])
    got = listing("")
    line = [l.split("\t") for l in got.stdout.splitlines() if l.split("\t")[1:2] == ["c"]]
    raw = line[0][6] if line else got.stdout + got.stderr
    check(got.returncode == 0 and raw.startswith("no result"), "in CI (level_words absent) a covered row's own stale PASS record is ignored: it shows no result, never PASS (R2, TD2348)", raw)
    real = subprocess.run([sys.executable, os.path.join(REG, "tests.py"), "list", "--tsv"], cwd=repo.path, env=repo.env, capture_output=True, text=True)
    local = [l.split("\t")[6] for l in real.stdout.splitlines() if l.split("\t")[1:2] == ["c"]]
    check(local and local[0].startswith("FAIL abc123456789"), "locally the same row shows the worst of its covers: FAIL with the commit", local)
    repo.close()


def runbook():
    print("== line 1: the Regression runbook uses L0, L1 and L2; the old words are in one table")
    # Value: protects=the runbook speaks one set of level words and the old words that must still be typed are listed once, each with
    #   where and what replaces it; fails_when=an old word is back in the runbook, a level is missing, or a table line is dropped
    import re
    page = open(os.path.join(root, "docs", "wiki", "Regression.md"), encoding="utf-8").read()
    book = page.split("\n## Runbook\n", 1)[1].split("\n## Requirements", 1)[0]
    found = sorted(set(w.lower() for w in re.findall(r"\b(land|nightly|covered|draft)\b", book, re.I)))
    check(not found, "the Runbook section holds none of land, nightly, covered, draft: %s" % (found or "none"))
    check(all(re.search(r"\b%s\b" % level, book) for level in ("L0", "L1", "L2")) and "L0, L1, L2 or one row id" in book, "the Runbook names the targets L0, L1, L2 and a row id")
    how = open(os.path.join(root, "docs", "wiki", "How-to-use-Regression.md"), encoding="utf-8").read()
    table = how.split("**Old words and the new levels**", 1)
    check(len(table) == 2, "How-to-use-Regression.md has the block 'Old words and the new levels'")
    rows = [l for l in (table[1].split("**Run targets**", 1)[0].split("\n#", 1)[0] if len(table) == 2 else "").splitlines() if l.startswith("| `")]
    want = (("regression.py add --level", ("land", "nightly", "draft", "covered"), "--test-level"),
            ("regression.py run", ("land", "nightly"), "L1"),
            ("goal_levels", ("land", "nightly"), "L2"),
            ("ci_levels", ("land", "nightly"), "unchanged"),
            ("regression-limits.tsv", ("land", "nightly"), "unchanged"))
    for where, olds, new in want:
        line = [l for l in rows if where in l.split("|")[1]]
        check(len(line) == 1 and all(w in line[0] for w in olds) and new in line[0], "the table has one line for %s with its old words and %s" % (where, new), line)


def prlevel():
    print("== S7: the pull request check runs L1 on an armed table; ci_levels no longer steers it")
    # Value: protects=regression-pr.yml names L1 on an armed table and is otherwise unchanged (same triggers, permissions, steps), the cover's
    #   pinned sha follows the file, and an unarmed table keeps ci_levels; fails_when=an armed repository still writes ci_levels, anything but
    #   the run line differs, or WF_SHA is not the sha1 of the committed file
    import hashlib
    from lvl_fixture import Repo, entry, row, REG
    risks = ["label\tsecurity\tsecurity\tfixture label"]

    def written(armed, levels):
        rows = [row("a")] + ([row("lvl-armed")] if armed else [])
        repo = Repo(rows, [entry("a")] + ([entry("lvl-armed")] if armed else []), risks)
        os.makedirs(os.path.join(repo.path, "skills", "workflow-regression"))
        os.symlink(REG, os.path.join(repo.path, "skills", "workflow-regression", "scripts"))
        repo.write(".loop/config.json", json.dumps({"ci_levels": levels}))
        armed and repo.write(".github/workflows/regression-pr.yml", "# Written by workflow-regression\n")
        repo.commit()
        repo.run("workflow", "--visibility", "public")
        text = repo.read(".github/workflows/regression-pr.yml")
        repo.close()
        return text
    armed_land, armed_night = written(True, "land"), written(True, "nightly")
    plain_land = written(False, "land")
    check("run L1 --reuse --tier goal" in armed_land and "run land" not in armed_land, "armed, ci_levels land: the check runs L1 and ci_levels does not steer it")
    check(armed_land == armed_night, "armed: ci_levels land and nightly write the same file")
    check("run land --reuse --tier goal" in plain_land, "not armed: ci_levels land still steers the check, as before")
    check(armed_land.replace("run L1 ", "run land ") == plain_land, "the armed file differs from the unarmed one only in the run line: triggers, permissions and steps are the same")
    committed = open(os.path.join(root, ".github", "workflows", "regression-pr.yml"), encoding="utf-8").read()
    cover = open(os.path.join(root, "skills", "workflow-delivery", "scripts", "cover.py"), encoding="utf-8").read()
    sha = hashlib.sha1(committed.strip().replace("\r\n", "\n").encode()).hexdigest()
    sys.path.insert(0, os.path.join(root, "skills", "workflow-delivery", "scripts"))
    import cover as cover_mod
    check(tuple(cover_mod.WF_SHA) == ("533fbed6f28fac049a2bd2c45eaa3bdbffed1ac6", sha), "cover.py's WF_SHA is exactly two shas: the nightly-line text and the sha1 of the committed regression-pr.yml (they move together)", cover_mod.WF_SHA)
    check("run L1 --reuse --tier goal" in committed, "this repository's regression-pr.yml names L1")


def wfpin():
    print("== S7/R14: the cover pins exactly two generated texts; the fix is named; update reports the old text")
    # Value: protects=the cover accepts the two reviewed generated workflows (nightly line, L1 line) and nothing else, a refusal says how to fix it,
    #   and update names an old generated workflow on an armed table; fails_when=the old text turns the cover off for an unarmed adopter, a third
    #   text passes, or either message has no runnable fix
    import contextlib, hashlib, io
    delivery = os.path.join(root, "skills", "workflow-delivery", "scripts")
    sys.path.insert(0, delivery)
    sys.path.insert(0, os.path.join(root, "skills", "workflow-setup", "scripts"))
    import cover
    new = open(os.path.join(root, ".github", "workflows", "regression-pr.yml"), encoding="utf-8").read()
    old = new.replace("run L1 --reuse --tier goal", "run nightly --reuse --tier goal")
    third = new.replace("run L1 --reuse --tier goal", "run L1 --reuse --tier goal --kind defect")
    sha = lambda t: hashlib.sha1(t.strip().replace("\r\n", "\n").encode()).hexdigest()
    check(tuple(cover.WF_SHA) == ("533fbed6f28fac049a2bd2c45eaa3bdbffed1ac6", "19b5c86b5523cea9c2219fb081e82592e9f48370") and sha(old) == cover.WF_SHA[0] and sha(new) == cover.WF_SHA[1],
          "WF_SHA holds exactly two shas: the nightly-line text and the L1-line text", cover.WF_SHA)
    check(cover.pinned(new) and cover.pinned(old), "the cover accepts the L1 text and the nightly text", (cover.pinned(new), cover.pinned(old)))
    check(not cover.pinned(third), "a third, edited regression-pr.yml is still off")
    folder = tempfile.mkdtemp(prefix="test-level-words-cover.")
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        cover.off(folder, "slug", "pr", "WF")
    said = out.getvalue()
    check("COVER OFF: WF" in said and "regression.py workflow" in said and "regression-pr.yml" in said, "COVER OFF: WF names the fix: regenerate with regression.py workflow, commit regression-pr.yml", said)
    import update
    from lvl_fixture import Repo, entry, row
    risks = ["label\tsecurity\tsecurity\tfixture label"]

    def report(armed, text, levels="land"):
        repo = Repo([row("a")] + ([row("lvl-armed")] if armed else []), [entry("a")] + ([entry("lvl-armed")] if armed else []), risks)
        repo.write(".loop/config.json", json.dumps({"ci_levels": levels}))
        repo.write(".github/workflows/regression-pr.yml", text)
        got = update.old_workflow(repo.path)
        repo.close()
        return got
    armed_old = report(True, old)
    check(armed_old and "regression.py workflow" in " ".join(armed_old) and "ci_levels" in " ".join(armed_old), "update names an old generated workflow on an armed table, the fix, and that ci_levels is ignored", armed_old)
    check(report(True, new) == [], "update says nothing when the armed table's workflow is the L1 text")
    check(report(False, old) == [], "update says nothing on an unarmed table: the nightly text is the one it writes")


def advice():
    print("== R15: advice and help text name L0, L1 and L2 (the old words only as the column-2 words they still are)")
    # Value: protects=the health advice and the --level help send a person to the level words; fails_when=an advice line goes back to
    #   "run land"/"run nightly" as the level to run, or the --level error forgets the levels
    def src(rel):
        return open(os.path.join(root, rel), encoding="utf-8").read()
    lean, mile = src("skills/workflow-health/scripts/lean.py"), src("skills/workflow-health/scripts/milestone.py")
    check("run what it left with regression.py run L1 (land: the land rows), or raise the budget" in lean and "run regression.py run L1 --reuse (land --reuse works too)" in lean, "lean.py's lane advice says run L1 and keeps the old word land beside it")
    check("move the slowest rows to L2 (nightly in column 2 of .loop/regression.tsv)" in lean, "lean.py says where to move a slow row: L2, the nightly word of column 2")
    check("regression.py run L2" in mile and "regression.py run nightly" not in mile, "milestone.py's full-suite advice says run L2")
    check(mile.count("move the slowest to L2 (nightly in column 2)") == 1 and "move the slowest to nightly" not in mile, "milestone.py's slow-row advice says L2 and where the word nightly still goes")
    from lvl_fixture import Repo
    repo = Repo([], None, None)
    done, said = repo.run("add", "x", "--level", "L1", "--command", "true")
    repo.close()
    said = " ".join(said.split())
    check(done != 0 and "--level takes the old words land, nightly, draft or covered (the levels are L0, L1 and L2)" in said, "the --level error names the old words and the levels", said[-250:])


def advice2():
    print("== R15: no advice line names run land or run nightly without the L0, L1, L2 meaning beside it")
    # Value: protects=an old word a person types still works and is always shown with the level it means; fails_when=a prose or advice line
    #   in the seven named surfaces says "run land"/"run nightly" with no L0, L1 or L2 on the line (a bare command example is exempt)
    import re
    names = ("skills/workflow-health/scripts/lean.py", "skills/workflow-health/scripts/milestone.py", "skills/workflow-regression/scripts/levels_write.py",
             "skills/workflow-regression/scripts/levels_cli.py", ".loop/START.md", "skills/loop-files.md", "skills/workflow-regression/SKILL.md")
    bad = []
    for rel in names:
        for n, line in enumerate(open(os.path.join(root, rel), encoding="utf-8").read().splitlines(), 1):
            if re.search(r"\b(run|add [\w-]+ --level) (land|nightly)\b|--level land|to nightly\b", line) and not re.search(r"\bL[012]\b", line):
                bare = re.match(r"^\s*(python3 |/workflow-regression |\|? ?`?/workflow-regression|- `/workflow-regression)", line)
                bare or bad.append("%s:%d" % (rel, n))
    check(not bad, "every advice line that names run land or run nightly has L0, L1 or L2 beside it: %s" % (bad or "none"))
    book = open(os.path.join(root, "skills", "workflow-regression", "SKILL.md"), encoding="utf-8").read()
    check("| `land` | `run land` and `run nightly` (L1's rows: `run L1`" in book and "| `nightly` | `run nightly` (L2's rows: `run L2`" in book, "SKILL.md's level table says what land and nightly mean in L1 and L2")


def draftl0():
    print("== R5: L0 and covers for a draft, and every refusal's fix command runs")
    # Value: protects=a draft is never run to measure it and takes no covers; each refusal's fix is a command that works;
    #   fails_when=--retime runs a draft's command, a draft takes --covers, or a printed fix does not run once its placeholders are filled
    import re
    from lvl_fixture import Repo, entry, row
    repo = Repo([row("alpha")], [entry("alpha")], ["label\tsecurity\tsecurity\tfixture label"])
    repo.commit()
    marker = os.path.join(repo.path, "RAN-DRAFT")

    def fix_of(said, command="true"):
        """The command a refusal's Fix: line prints (up to its first '. ' or ';'), its placeholders filled in, as an argument list."""
        text = re.split(r"\. |; |\n", said.split("Fix:", 1)[1].strip())[0]
        for old, value in (("'...'", "'%s'" % command), ("'<a real command>'", "'%s'" % command), ("<L>", "L1"), ("<workflow-regression>/scripts/", "")):
            text = text.replace(old, value)
        return __import__("shlex").split(re.sub(r"^(python3 )?(regression\.py )?", "", text.strip()))
    done, said = repo.run("add", "d1", "--level", "draft", "--command", "touch RAN-DRAFT")
    check(done != 0 and "LEVELS_NO_STAGE" in said, "control: a draft with no stage is refused", said)
    fixed = fix_of(said, "touch RAN-DRAFT")
    done, said = repo.run(*fixed)
    check(done == 0 and not os.path.exists(marker), "the LEVELS_NO_STAGE fix runs and makes the draft without running it", (fixed, said))
    done, said = repo.run("level", "d1", "--test-level", "L0", "--retime")
    check(done != 0 and "LEVELS_DRAFT_NOT_READY" in said and "level d1 --ready" in said and not os.path.exists(marker),
          "--retime on a draft is refused with the fix 'level d1 --ready' and does not run the draft's command", said)
    done, said = repo.run("level", "d1", "--covers", "alpha")
    check(done != 0 and "LEVELS_DRAFT_NOT_READY" in said, "a draft takes no --covers: it is refused until it is ready", said)
    done, said = repo.run("add", "d2", "--level", "draft", "--test-level", "L1", "--covers", "alpha", "--command", "true")
    check(done != 0 and "LEVELS_DRAFT_NOT_READY" in said, "add --level draft --covers is refused (a draft is not a covered row)", said)
    done, said = repo.run("level", "d1", "--ready", "--risk", "security")
    check(done != 0 and "LEVELS_BAD_FLAGS" in said, "--ready goes alone: another flag beside it is refused, not ignored (review round 1)", said)
    done, said = repo.run("add", "d3", "--level", "draft", "--test-level", "L1", "--command", "echo write a test")
    done, said = repo.run("level", "d3", "--ready")
    check(done != 0 and "LEVELS_NO_REAL_COMMAND" in said, "control: a placeholder draft cannot be readied", said)
    fixed = fix_of(said)
    done, said = repo.run(*fixed)
    check(done == 0, "the LEVELS_NO_REAL_COMMAND fix runs once its placeholders are filled", (fixed, said))
    done, said = repo.run("level", "d3", "--ready")
    check(done == 0, "and then --ready works", said)
    done, said = repo.run("level", "d1", "--ready")
    fixed = "level d1 --test-level L0 --retime"
    done, said = repo.run(*fixed.split())
    check(done == 0 and "LEVEL d1 L0" in said, "after --ready, L0 is measured with --retime (the fix text says so)", said)
    repo.close()


def wfrows():
    print("== R14: update names the rows that stop running in the pull request check when the old workflow is replaced")
    # Value: protects=an adopter is told, before regenerating, which rows the new L1 check no longer runs; fails_when=the report is silent about
    #   rows, names a row that still runs, or says nothing is lost when a land row's stage is L2
    sys.path.insert(0, os.path.join(root, "skills", "workflow-setup", "scripts"))
    import update
    from lvl_fixture import Repo, entry, row
    risks = ["label\tsecurity\tsecurity\tfixture label"]
    rows = [row("lvl-armed"), row("a"), row("x"), row("n", level="nightly")]
    ents = [entry("lvl-armed"), entry("a"), entry("x", level="L2"), entry("n", old="nightly", level="L2")]
    new = open(os.path.join(root, ".github", "workflows", "regression-pr.yml"), encoding="utf-8").read()
    for word, want in (("land", "ROWS: 1 row stops running in the pull request check: x"), ("nightly", "ROWS: no row stops running")):
        repo = Repo(rows, ents, risks)
        repo.write(".loop/config.json", json.dumps({"ci_levels": word}))
        repo.write(".github/workflows/regression-pr.yml", new.replace("run L1 --reuse", "run %s --reuse" % word))
        got = update.old_workflow(repo.path)
        repo.close()
        check(any(want in line for line in got), "old text 'run %s': %s" % (word, want), got)


def gate():
    print("== R2, R8, R9: the major gate evaluates a covered row through its covers, on a levelled table only; PASS never wins over FAIL")
    # Value: protects=a requirement held by a covered row is unmet when a cover is failing, a draft or missing, is met when every cover passes
    #   or is known, and the old skip stays for a table that is not levelled; a PASS never wins over a FAIL for the same commit;
    #   fails_when=the gate skips a covered row whatever its covers do
    import json as _json, subprocess
    sys.path.insert(0, os.path.join(root, "skills", "workflow-release", "scripts"))
    import review
    from lvl_fixture import Repo, entry, row

    def unmet(rows, ents, known="", failing=(), proven=()):
        repo = Repo(rows, ents, ["label\tsecurity\tsecurity\tfixture label"])
        repo.write("docs/wiki/P.md", "# P\n\n## Requirements\n\n" + "".join("- %s: **Unreviewed** t\n" % r["id"] for r in rows if r["id"].startswith("ABC-")))
        known and repo.write(".loop/regression-known.tsv", known)
        ents is None and os.remove(os.path.join(repo.path, ".loop", "regression-relevel.tsv")) if ents is None and os.path.exists(os.path.join(repo.path, ".loop", "regression-relevel.tsv")) else None
        repo.commit()
        old = review.proven
        review.proven = lambda top: set(proven)
        try:
            got = review.criteria(repo.path, {}, lambda top: ["P"], lambda cmd, top: cmd in failing)
        finally:
            review.proven = old
        repo.close()
        return got[0]
    base = [row("good", command="g"), row("bad", command="b"), row("drf", level="draft"), row("ABC-1", level="covered", command="x"),
            row("ABC-2", level="covered", command="x"), row("ABC-3", level="covered", command="x"), row("ABC-4", level="covered", command="x")]
    ents = [entry("good"), entry("bad"), entry("drf", old="draft"), entry("ABC-1", old="covered", covers="good"), entry("ABC-2", old="covered", covers="bad"),
            entry("ABC-3", old="covered", covers="drf"), entry("ABC-4", old="covered", covers="good,bad")]
    got = unmet(base, ents, failing=("b",))
    check(not any(u.startswith("ABC-1") for u in got), "a covered row whose cover passes is met", got)
    check(any(u.startswith("ABC-2") and "bad" in u for u in got), "a covered row whose cover fails is unmet and names the cover", got)
    check(any(u.startswith("ABC-3") and "drf" in u for u in got), "a covered row whose cover is a draft is unmet and names the cover", got)
    check(any(u.startswith("ABC-4") and "bad" in u for u in got), "one failing cover among two makes the row unmet", got)
    got = unmet(base, ents, known="bad\tknown red\n", failing=("b",))
    check(not any(u.startswith("ABC-2") for u in got), "a known cover is treated as the gate treats a known row today (met), and nothing says green", got)
    more = base + [row("ABC-5", level="covered", command="x"), row("ABC-6", level="covered", command="x")]
    got = unmet(more, ents + [entry("ABC-6", old="covered", covers="")], failing=("b",))
    check(any(u.startswith("ABC-5") for u in got) and any(u.startswith("ABC-6") for u in got),
          "on a levelled table a covered row with no record entry, or an empty covers list, is unmet (fail closed, review round 1)", got)
    got = unmet(base, None, failing=("b",))
    check(not any(u.startswith(("ABC-2", "ABC-3", "ABC-4")) for u in got), "a table with no levels record keeps the old skip of covered rows (R9: levelled tables only)", got)
    repo = Repo([row("a")], [entry("a")], ["label\tsecurity\tsecurity\tx"])
    repo.commit()
    head = repo.git("rev-parse", "HEAD").stdout.strip()
    folder = os.path.join(review.common_of(repo.path), "tests")
    os.makedirs(folder, exist_ok=True)
    for name, status in (("pass", "PASS"), ("fail", "FAIL")):
        open(os.path.join(folder, name + ".json"), "w").write(_json.dumps({"rows": {"a": {"status": status, "commit": head}}}))
    only = {"a"} if review.proven(repo.path) else set()
    os.remove(os.path.join(folder, "fail.json"))
    check("a" in review.proven(repo.path), "control: with only the PASS record the row is proven", only)
    open(os.path.join(folder, "fail.json"), "w").write(_json.dumps({"rows": {"a": {"status": "FAIL", "commit": head}}}))
    found = review.proven(repo.path)
    repo.close()
    check("a" not in found, "a row with a PASS and a FAIL for the same commit is not proven (R8: PASS never wins over FAIL)", found)


def mixedrecord():
    print("== R13: an old branch with 8-cell record lines merges with a new record of 9-cell lines")
    # Value: protects=a branch written before the state column merges cleanly where it touched other rows, mixed lines read, and one id changed
    #   on both sides is left to the person merging; fails_when=a mixed record is refused, or the repair merges two different lines of one id
    import subprocess
    from lvl_fixture import Repo, entry, row, ROOT
    sys.path.insert(0, os.path.join(ROOT, "skills", "workflow-delivery", "scripts"))
    import mend_tables
    risks = ["label\tsecurity\tsecurity\tfixture label"]
    rec = ".loop/regression-relevel.tsv"
    line = lambda e, extra="": "\t".join([e[c] for c in ("id", "old", "level", "risk", "covers", "seconds", "cmdhash", "reason")]) + extra + "\n"
    rows = [row("a"), row("b"), row("c")]

    def merged(ours, theirs):
        repo = Repo(rows, None, risks)
        repo.write(rec, line(entry("a")) + line(entry("b")) + line(entry("c")))
        repo.commit("base")
        repo.git("checkout", "-q", "-b", "other")
        repo.write(rec, theirs)
        repo.commit("old branch, 8 cells")
        repo.git("checkout", "-q", "main")
        repo.write(rec, ours)
        repo.commit("new record, 9 cells")
        got = repo.git("merge", "other", "--no-edit", check_it=False)
        text = repo.read(rec)
        git = lambda *a: subprocess.run(["git"] + list(a), cwd=repo.path, env=repo.env, capture_output=True, text=True)
        ok = None
        if got.returncode:
            cwd = os.getcwd()
            os.chdir(repo.path)
            try:
                ok = mend_tables.mend(git, [rec], "other")
            finally:
                os.chdir(cwd)
            text = repo.read(rec)
        check_state = repo.run("levels", "--check")
        repo.close()
        return got.returncode, ok, text, check_state
    new9 = line(entry("a"), "\t") + line(entry("b"), "\t") + line(entry("c"), "\t")
    code, ok, text, chk = merged(new9, line(entry("a")) + line(entry("b")) + line(entry("c")) + line(entry("d")))
    cells = sorted({len(l.split("\t")) for l in text.splitlines()})
    check((code == 0 or ok) and set(cells) <= {8, 9} and "d\t" in text and "<<<<" not in text and ">>>>" not in text,
          "an old branch's added row merges (git, or the repair) with a new record of 9-cell lines; the result has only 8- or 9-cell lines", (code, ok, cells, text[-160:]))
    check(chk[0] in (0, 2) and "doesn't have" not in chk[1], "a mixed record reads: no 'the line doesn't have' refusal", chk[1][:200])
    code, ok, text, chk = merged(new9, line(entry("a", level="L2")) + line(entry("b")) + line(entry("c")))
    check(code != 0 and not ok, "one id changed on both sides (a 9-cell line against an 8-cell edit) is left to the person merging", (code, ok))
    code, ok, text, chk = merged(line(entry("a"), "\t") + line(entry("b"), "\t") + line(entry("c"), "\t"),
                                 line(entry("a"), "\tdraft") + line(entry("b"), "\t") + line(entry("c"), "\t"))
    check(code != 0 and not ok, "two 9-cell lines of one entry whose state cells differ are left to the person merging, not resolved by length (review round 1)", (code, ok))
    repo = Repo(rows, None, risks)
    repo.close()


def targets():
    print("== R11: the run targets table, one asserted case per line; L0, L1 and L2 wait for memory like land and nightly")
    # Value: protects=every surface that takes a target is listed once with what it does, and the memory wait is the same for the level words
    #   as for the old words; fails_when=a level target skips the memory wait, or a table line is dropped or says something the tool does not do
    import re
    from lvl_fixture import Repo, entry, row
    from lvl_fixture import sha
    repo = Repo([row("a")], [entry("a", level="L0", seconds="1.0", cmdhash=sha("true"), reason="time:1.0")], ["label\tsecurity\tsecurity\tfixture label"])
    repo.commit()
    for target in ("land", "nightly", "L0", "L1", "L2"):
        done, said = repo.run("run", target, LOOP_FREE_GB="0.5", LOOP_MEMORY_WAIT_SECONDS="1")
        check(done == 6 and "LANE_MEMORY" in said, "run %s waits for memory (exit 6 after the wait under 0.5 GB free)" % target, (done, said[-160:]))
    done, said = repo.run("run", "--ids", "a", LOOP_FREE_GB="0.5", LOOP_MEMORY_WAIT_SECONDS="1")
    check(done == 6 and "LANE_MEMORY" in said, "run --ids waits for memory", (done, said[-160:]))
    done, said = repo.run("run", "a", LOOP_FREE_GB="0.5", LOOP_MEMORY_WAIT_SECONDS="1")
    check(done == 0 and "LANE_MEMORY" not in said, "run <row id> does not wait: it runs the one row", (done, said[-160:]))
    repo.close()
    how = open(os.path.join(root, "docs", "wiki", "How-to-use-Regression.md"), encoding="utf-8").read()
    block = how.split("**Run targets**", 1)
    check(len(block) == 2, "How-to-use-Regression.md has the block 'Run targets'")
    lines = [l for l in (block[1].split("\n#", 1)[0] if len(block) == 2 else "").splitlines() if l.startswith("| `") or l.startswith("| the ")]
    want = (("regression.py run", ("L0", "L1", "L2", "land", "nightly", "a row id", "waits for memory")),
            ("regression.py run --ids", ("takes a slot", "waits for memory")),
            ("regression.yml", ("land", "nightly", "L2", "L0 and L1 only when the table is armed", "BAD_TARGET", "COVERED_ROW", "not run: draft")),
            ("suite time", ("plain `run nightly`", "SUITE_TIME")),
            ("ci_levels", ("regression-pr.yml", "L1 when the table is armed", "land or nightly otherwise")),
            ("review.py", ("run nightly", "major gate", "covers")),
            ("goal lane", ("goal_levels", "L0 by default", "--reuse --tier goal", "cover", "regression-pr.yml")))
    for name, tokens in want:
        cell = lambda l: l.split("|")[1].replace("`", "").strip()
        got = [l for l in lines if cell(l) == name or cell(l).startswith(name + " (")]
        check(len(got) == 1 and all(t in got[0] for t in tokens), "the Run targets table has one line for %s with %s" % (name, ", ".join(tokens)), got)


cases = {"goal": goal, "settings": settings, "moved": moved, "coverlevel": coverlevel, "superset": superset, "state": state, "drafts": drafts, "notrun": notrun, "syncdraft": syncdraft, "enforced": enforced, "critcover": critcover, "plaindraft": plaindraft, "unarmed": unarmed, "writers": writers, "coverstate": coverstate, "mixedruns": mixedruns, "swallow": swallow, "runbook": runbook, "prlevel": prlevel, "advice": advice, "advice2": advice2, "draftl0": draftl0, "wfrows": wfrows, "gate": gate, "targets": targets, "mixedrecord": mixedrecord, "wfpin": wfpin}
for name in (sys.argv[1:] or list(cases)):
    cases[name]()
print("%d failed" % len(failed))
print("ALL PASS" if not failed else "FAILED")
sys.exit(1 if failed else 0)
