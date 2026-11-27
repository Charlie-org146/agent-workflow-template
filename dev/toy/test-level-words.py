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
    for key, want in (("ABC-1", "not enforced"), ("ABC-2", "not enforced")):
        item = found.get(key, {})
        check(item.get("state") == "WARN" and want in item.get("detail", ""), "%s shows WARN, not enforced" % key, item or "no row for %s among %s" % (key, sorted(found)))
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
    check(all(re.search(r"\b%s\b" % level, book) for level in ("L0", "L1", "L2")) and "target L0, L1, L2 or one row id" in book, "the Runbook names the targets L0, L1, L2 and a row id")
    how = open(os.path.join(root, "docs", "wiki", "How-to-use-Regression.md"), encoding="utf-8").read()
    table = how.split("### Old words and the new levels", 1)
    check(len(table) == 2, "How-to-use-Regression.md has the section 'Old words and the new levels'")
    rows = [l for l in (table[1].split("\n##", 1)[0] if len(table) == 2 else "").splitlines() if l.startswith("| `")]
    want = (("regression.py add --level", ("land", "nightly", "draft", "covered"), "--test-level"),
            ("regression.py run", ("land", "nightly"), "L1"),
            ("goal_levels", ("land", "nightly"), "L2"),
            ("ci_levels", ("land", "nightly"), "unchanged"),
            ("regression-limits.tsv", ("land", "nightly"), "unchanged"))
    for where, olds, new in want:
        line = [l for l in rows if l.split("|")[1].strip("` ").startswith(where)]
        check(len(line) == 1 and all(w in line[0] for w in olds) and new in line[0], "the table has one line for %s with its old words and %s" % (where, new), line)


cases = {"goal": goal, "settings": settings, "moved": moved, "coverlevel": coverlevel, "superset": superset, "state": state, "drafts": drafts, "notrun": notrun, "syncdraft": syncdraft, "enforced": enforced, "critcover": critcover, "plaindraft": plaindraft, "unarmed": unarmed, "writers": writers, "coverstate": coverstate, "mixedruns": mixedruns, "swallow": swallow, "runbook": runbook}
for name in (sys.argv[1:] or list(cases)):
    cases[name]()
print("%d failed" % len(failed))
print("ALL PASS" if not failed else "FAILED")
sys.exit(1 if failed else 0)
