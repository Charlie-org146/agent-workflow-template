#!/usr/bin/env python3
# reads: skills/workflow-regression/scripts/regression.py skills/workflow-delivery/scripts/mend_tables.py dev/toy/lvl_fixture.py
"""v110-lvl-relevel lines 1 and 2: a levelled table with a wrong level or a missing risk tag is refused by name, every
other refusal, the repairs, the writes that must not lower a tag, a stopped write, selection, the cover and the merge."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.dont_write_bytecode = True
from lvl_fixture import DELIVERY, REG, RISKS, ROOT, Repo, check, done, entry, row, sha  # noqa: E402

BASE = [row("alpha"), row("beta", goal="demo:1"), row("gdel", goal="DEL-9.1"), row("grd6-pins"), row("listed-guard")]


def good():
    return [entry("alpha"), entry("beta"), entry("gdel", risk="private", reason="risk:private"),
            entry("grd6-pins", risk="security", reason="risk:security"),
            entry("listed-guard", risk="security", reason="risk:security")]


def ent(repo, key, cell):
    return repo.entries().get(key, {}).get(cell, "")


def changed(key, **new):
    return [dict(e, **new) if e["id"] == key else e for e in good()]


def refused(repo, code, *names, command=("run", "alpha")):
    status, said = repo.run(*command)
    return status == 2 and code in said and all(n in said for n in names), "exit %d\n%s" % (status, said)


def expect(code, said, rows=None, entries=None, risks=RISKS, names=()):
    repo = Repo(rows or BASE, entries if entries is not None else good(), risks)
    repo.commit()
    ok, got = refused(repo, code, *names)
    check(ok, said, got)
    repo.close()


repo = Repo(BASE, good())
repo.commit()
status, said = repo.run("run", "alpha")
check(status == 0, "control: a valid levelled table runs", said)
repo.close()

# done line 1: a level that is blank or L3, in the record and in the table's own level cell
for value, name in (("", "blank"), ("L3", "L3")):
    expect("LEVELS_BAD_LEVEL", "a %s level is refused, naming the row and the three levels" % name,
           entries=changed("beta", level=value), names=("beta", "L0, L1 or L2"))
    expect("LEVELS_BAD_OLD_WORD", "a %s level cell in the table is refused, naming the row and the three levels" % name,
           rows=[row("beta", level=value, goal="demo:1") if r["id"] == "beta" else r for r in BASE],
           names=("beta", "L0, L1 or L2"))

# done line 2: a row that guards a Principle 6 requirement, by goal cell, by id alone, or listed
for key, how in (("gdel", "its goal cell"), ("grd6-pins", "its id alone"), ("listed-guard", "a listed line")):
    for value in ("none", ""):
        expect("LEVELS_NO_RISK", "a row guarding a requirement by %s with risk %r is refused by name" % (how, value),
               entries=changed(key, risk=value), names=(key,))
expect("LEVELS_NO_RISK", "a row guarding a private requirement tagged only security is refused by name",
       entries=changed("gdel", risk="security", reason="risk:security"), names=("gdel", "private"))
repo = Repo(BASE + [row("pkg-secret-grd-60"), row("print-6-sizes")], good() + [
    entry("pkg-secret-grd-60"), entry("print-6-sizes")])
repo.commit()
status, said = repo.run("run", "alpha")
check(status == 0, "control: GRD-60 and print-6 name no requirement", said)
repo.close()

# the other refusals
repo = Repo(BASE + [row("lvl-armed")], None)
repo.commit()
ok, got = refused(repo, "LEVELS_NO_RECORD")
check(ok, "a table holding lvl-armed with no record is refused", got)
repo.close()
expect("LEVELS_NO_ENTRY", "a row with no entry is refused, naming it and the three levels", entries=good()[1:],
       names=("alpha", "L0, L1 or L2"))
expect("LEVELS_RISK_LEVEL", "a tagged row at L2 is refused", entries=changed("gdel", level="L2"), names=("gdel",))
expect("LEVELS_ORPHAN", "an entry with no row is refused", entries=good() + [entry("ghost")], names=("ghost",))
expect("LEVELS_DUPLICATE", "an id twice in the record is refused", entries=good() + [entry("alpha")], names=("alpha",))
expect("LEVELS_L0_TIME", "an L0 entry for another command is refused",
       entries=changed("alpha", level="L0", seconds="1.0", cmdhash=sha("false")), names=("alpha",))
many = [row("slow%d" % i) for i in range(10)]
expect("LEVELS_L0_OVER", "L0 times over 45 seconds are refused, naming the total", rows=BASE + many,
       entries=good() + [entry(r["id"], level="L0", seconds="4.9", cmdhash=sha("true"), reason="time:4.9") for r in many],
       names=("49.0",))
cov = BASE + [row("done-x", level="covered", command="proved elsewhere")]
for covers, name in (("", "empty"), ("done-x", "itself"), ("nope", "unknown")):
    expect("LEVELS_BAD_COVERS", "a covers list that is %s is refused" % name, rows=cov,
           entries=good() + [entry("done-x", old="covered", covers=covers, reason="covers")], names=("done-x",))
expect("LEVELS_BAD_RISK_DATA", "missing risk data is refused", risks=None)
expect("LEVELS_BAD_RISK_DATA", "an unknown risk-data tag is refused",
       risks=RISKS + ["row\talpha\tsecret\twhy"])
expect("LEVELS_BAD_FILE", "a misspelled risk value is refused", entries=changed("alpha", risk="privte"), names=("alpha",))
expect("LEVELS_BAD_FILE", "a blank old word is refused", entries=changed("alpha", old=""), names=("alpha",))
repo = Repo(BASE, good())
repo.write(".loop/regression-relevel.tsv", repo.read(".loop/regression-relevel.tsv") + "<<<<<<< ours\n")
repo.commit()
ok, got = refused(repo, "LEVELS_BAD_FILE")
check(ok, "a conflict marker in the record is refused", got)
repo.close()
bug = [row("bug", category="defect", link="https://github.com/o/r/issues/1")]
expect("LEVELS_STALE_RISK", "a defect entry read from another link is refused", rows=BASE + bug,
       entries=good() + [entry("bug", reason="src:0000000000")], names=("bug",))
repo = Repo(BASE + [row("n%02d" % i) for i in range(30)], good())
repo.commit()
status, said = repo.run("run", "alpha")
check(status == 2 and said.count("LEVELS_NO_ENTRY") == 20 and "30 in all" in said, "the first 20 problems and a count", said)

# which commands refuse, and the repairs that run on a refused table
before = repo.snapshot()
for command in (("criteria",), ("sync",), ("sync", "--write"), ("red", "alpha", "--break", "true"), ("run", "land")):
    ok, got = refused(repo, "LEVELS_NO_ENTRY", command=command)
    check(ok and repo.snapshot() == before, "`%s` refuses and writes nothing" % " ".join(command), got)
status, said = repo.run("levels", "--check")
check(status == 2 and "missing entry to fill" in said, "levels --check reports and exits 2", said)
status, said = repo.run("levels")
check(status == 0 and "problems: 30" in said, "levels lists and exits 0", said)
status, said = repo.run("levels", "--fill")
status2, said2 = repo.run("levels", "--check")
check(status == 0 and status2 == 0 and "valid" in said2 and all(
    e["level"] != "L0" for e in repo.entries().values()), "levels --fill repairs the refused table, never L0", said + said2)
repo.close()

# a table that is not levelled reads and writes as before
repo = Repo(BASE, None, None)
repo.commit()
status, said = repo.run("add", "plain", "--level", "land", "--command", "true")
status2, said2 = repo.run("levels", "--check")
check(status == 0 and repo.read(".loop/regression-relevel.tsv") is None and "not levelled" in said2 and status2 == 0,
      "an unlevelled table takes add with no record", said + said2)
status, said = repo.run("add", "plain", "--level", "land", "--command", "true", "--risk", "private")
check(status != 0 and "relevel" in said, "--risk on an unlevelled table is refused, not dropped", said)
repo.close()

# add
repo = Repo(BASE, good())
repo.commit()
status, said = repo.run("add", "newrow", "--level", "nightly", "--command", "true")
got = repo.entries().get("newrow", {})
check(status == 0 and got.get("level") == "L1" and got.get("old") == "nightly" and "LEVEL newrow L1" in said,
      "add gives a new row L1 and prints it", said)
status, said = repo.run("add", "grd6-new", "--command", "true")
check(status == 0 and ent(repo, "grd6-new", "risk") == "security", "add derives a requirement tag", said)
status, said = repo.run("add", "x", "--level", "L1", "--command", "true")
check(status != 0 and "--test-level" in said, "--level L1 points to --test-level", said)
status, said = repo.run("add", "x", "--command", "true", "--test-level", "L0")
check(status != 0 and "x" not in repo.rows() and "--retime" in said, "add never sets L0", said)
status, said = repo.run("add", "done-y", "--level", "covered", "--command", "by alpha")
check(status != 0 and "--covers" in said and "done-y" not in repo.rows(), "a covered add without --covers is refused", said)
status, said = repo.run("add", "done-y", "--level", "covered", "--command", "by alpha", "--covers", "alpha")
status2, said2 = repo.run("levels", "--check")
check(status == 0 and status2 == 0, "a covered add with --covers is valid", said + said2)
repo.labels({"repos/o/r/issues/7": ["bug", "area:private-data"]})
url = "https://github.com/o/r/pull/7"
status, said = repo.run("add", "bug7", "--command", "true", "--category", "defect", "--link", url)
check(status == 0 and ent(repo, "bug7", "risk") == "private", "a pull request's labels tag a defect", said)
check("area:private-data" not in "".join(x or "" for x in repo.snapshot()), "no fetched label text is written")
calls = len(repo.calls())
status, said = repo.run("add", "bug7", "--command", "true", "--category", "defect", "--link", url, "--describe", "again")
check(status == 0 and len(repo.calls()) == calls, "an unchanged link keeps its tag without a read", said)
status, said = repo.run("add", "bug9", "--command", "true", "--category", "defect", "--link",
                        "https://github.com/o/r/issues/9")
check(status != 0 and "bug9" not in repo.rows(), "an unreadable defect link is refused without a tag", said)
status, said = repo.run("add", "bug9", "--command", "true", "--category", "defect", "--link", "#9", "--risk", "security")
check(status == 0 and ent(repo, "bug9", "risk") == "security", "raising needs no owner record", said)
status, said = repo.run("add", "bug8", "--command", "true", "--category", "defect", "--link", "#8", "--risk", "none")
check(status != 0 and "bug8" not in repo.rows() and "LEVELS_NEEDS_OWNER" in said, "none needs an owner record", said)

# lowering, removing and renaming keep the guard
status, said = repo.run("level", "bug9", "--risk", "none")
check(status != 0 and ent(repo, "bug9", "risk") == "security", "lowering a tag needs an owner record", said)
ledger = os.path.join(repo.path, ".git", "loop")
os.makedirs(ledger, exist_ok=True)
with open(os.path.join(ledger, "owner-words.tsv"), "w") as out:
    out.write("o5\t2026-01-01T00:00:00Z\toperation\tyes\tbug9\no6\t2026-01-01T00:00:00Z\toperation\tyes\tother\n")
for record in ("o999", "o6"):
    status, said = repo.run("level", "bug9", "--risk", "none", "--owner-record", record)
    check(status != 0 and ent(repo, "bug9", "risk") == "security", "record %s does not lower bug9" % record, said)
status, said = repo.run("level", "bug9", "--risk", "none", "--owner-record", "o5")
check(status == 0 and ent(repo, "bug9", "risk") == "none" and "owner:o5" in ent(repo, "bug9", "reason"),
      "a record covering the row lowers it and is stored", said)
status, said = repo.run("level", "gdel", "--risk", "none", "--owner-record", "o5")
check(status != 0 and ent(repo, "gdel", "risk") == "private", "a requirement row is never set to none", said)
before = repo.snapshot()
status, said = repo.run("level", "listed-guard", "--remove")
check(status != 0 and repo.snapshot() == before, "removing a tagged row needs an owner record", said)
status, said = repo.run("level", "alpha", "--remove")
check(status != 0 and "done-y" in said and repo.snapshot() == before, "a cover can't be removed", said)
status, said = repo.run("level", "listed-guard", "--rename", "listed-guard-2")
data = repo.read(".loop/regression-risk.tsv") or ""
check(status == 0 and "listed-guard-2" in repo.rows() and ent(repo, "listed-guard-2", "risk") ==
      "security" and "row\tlisted-guard-2\t" in data, "a rename moves the row, entry and risk line", said)
status, said = repo.run("level", "alpha", "--rename", "alpha2")
check(status == 0 and ent(repo, "done-y", "covers") == "alpha2", "a rename moves the covers lists", said)
status, said = repo.run("level", "alpha2", "--rename", "beta")
check(status != 0, "a rename onto another row is refused", said)
status, said = repo.run("level", "newrow", "--retime")
check(status == 0 and ent(repo, "newrow", "level") == "L0" and ent(repo, "newrow", "seconds"),
      "level --retime measures a passing row into L0", said)
status, said = repo.run("add", "newrow", "--level", "nightly", "--command", "true && true")
check(status == 0 and ent(repo, "newrow", "level") == "L1" and not ent(repo, "newrow", "seconds"),
      "a changed command leaves L0", said)
for command, why in (("exit 1", "a failing row"), ("exit 77", "a skipped row")):
    repo.run("add", "probe", "--command", command)
    status, said = repo.run("level", "probe", "--retime")
    check(status != 0 and ent(repo, "probe", "level") == "L1", "%s is no measurement" % why, said)
status, said = repo.run("level", "grd6-pins", "--retime")
check(status != 0 and "tagged" in said, "a tagged row is never retimed into L0", said)
repo.close()

# what a branch removes or lowers since its merge base
repo = Repo(BASE, good())
repo.commit()
repo.git("checkout", "-q", "-b", "loop/demo")
repo.record(changed("listed-guard", risk="none", reason="default"))
repo.write(".loop/regression-risk.tsv", "".join(x + "\n" for x in RISKS if "listed-guard" not in x))
repo.commit("hand edit")
ok, got = refused(repo, "LEVELS_LOWERED", "listed-guard")
check(ok, "a hand edit that drops a tag and its risk line is refused", got)
repo.record(changed("listed-guard", risk="none", reason="owner:o404"))
repo.write(".loop/regression-risk.tsv", "".join(x + "\n" for x in RISKS if "listed-guard" not in x)
           + "removed\trow:listed-guard\tnone\towner:o404\n")
status, said = repo.run("run", "alpha")
check(status == 0, "with no ledger (GitHub) a recorded owner id is accepted", said)
os.makedirs(os.path.join(repo.path, ".git", "loop"), exist_ok=True)
with open(os.path.join(repo.path, ".git", "loop", "owner-words.tsv"), "w") as out:
    out.write("o5\t2026-01-01T00:00:00Z\toperation\tyes\tsomething-else\n")
ok, got = refused(repo, "LEVELS_LOWERED", "listed-guard")
check(ok, "where a ledger exists the owner id is checked", got)
os.remove(os.path.join(repo.path, ".git", "loop", "owner-words.tsv"))
os.remove(os.path.join(repo.path, ".loop", "regression-relevel.tsv"))
ok, got = refused(repo, "LEVELS_LOWERED", "record")
check(ok, "removing the record is refused", got)
repo.close()

# a write that stops between the two files: reported, then completed; never replayed over later changes
CRASH = """import os, sys
sys.path.insert(0, sys.argv.pop(1)); sys.dont_write_bytecode = True
import levels_write, regression
real, seen = levels_write.put, []
def put(root, name, text):
    if seen:
        os._exit(9)
    seen.append(name)
    real(root, name, text)
levels_write.put = put
sys.exit(regression.main())
"""


def crash(repo, *args):
    return subprocess.run([sys.executable, "-c", CRASH, REG] + list(args), cwd=repo.path, env=repo.env,
                          capture_output=True, text=True).returncode


for args, name in ((("add", "late", "--command", "true"), "add"),
                   (("level", "beta", "--rename", "beta2"), "level --rename"),
                   (("level", "beta", "--remove"), "level --remove"),
                   (("level", "alpha", "--risk", "security"), "level --risk"),
                   (("sync", "--write"), "sync --write")):
    repo = Repo(BASE, good())
    repo.write(".loop/goals/open.md", "## Done lines\n\n1. Given x, when y, then z.\n")
    repo.commit()
    os.makedirs(os.path.join(repo.path, ".git", "loop", "runs"), exist_ok=True)
    with open(os.path.join(repo.path, ".git", "loop", "runs", "open.json"), "w") as out:
        json.dump({"status": "running"}, out)
    code = crash(repo, *args)
    ok, got = refused(repo, "LEVELS_INTERRUPTED", "levels --fill")
    status, said = repo.run("levels", "--fill")
    status2, said2 = repo.run("levels", "--check")
    check(code == 9 and ok and status == 0 and status2 == 0 and "valid" in said2,
          "a stopped %s is reported and levels --fill completes it" % name, "crash %d\n%s\n%s%s" % (code, got, said, said2))
    repo.close()
repo = Repo(BASE, good())
repo.commit()
crash(repo, "add", "late", "--command", "true")
repo.write(".loop/regression.tsv", repo.read(".loop/regression.tsv") + "\t".join(
    row("merged").values()) + "\n")
before = repo.snapshot()
status, said = repo.run("levels", "--fill")
check(status != 0 and repo.snapshot() == before and "--discard" in said,
      "a stopped write is not replayed over a later change", said)
status, said = repo.run("levels", "--discard")
status2, said2 = repo.run("levels", "--fill")
check(status == 0 and "merged" in repo.rows() and "merged" in repo.entries(), "after --discard the table fills", said2)
repo.close()

# a reader waits for a writer
repo = Repo(BASE, good())
repo.commit()
HOLD = """import sys, time
sys.path.insert(0, sys.argv[1]); sys.dont_write_bytecode = True
import slots
slots.edit(sys.argv[2], "regression.tsv", lambda: (print("held", flush=True), time.sleep(3)))
"""
holder = subprocess.Popen([sys.executable, "-c", HOLD, REG, repo.path], stdout=subprocess.PIPE, env=repo.env, text=True)
holder.stdout.readline()
began = time.time()
status, said = repo.run("sync")
check(time.time() - began > 1.5 and "LEVELS_" not in said, "a read waits for a write under way", said)
holder.wait()

# the new modules are part of the cached-result fingerprint
copy = tempfile.mkdtemp(prefix="lvl-scripts-")
shutil.copytree(REG, os.path.join(copy, "s"))
SAY = "import sys; sys.path.insert(0, sys.argv[1]); sys.dont_write_bytecode = True; import lanes; print(lanes.runner())"


def fingerprint():
    return subprocess.run([sys.executable, "-c", SAY, os.path.join(copy, "s")], capture_output=True, text=True).stdout


first = fingerprint()
for name in ("levels.py", "levels_gate.py", "levels_write.py", "levels_read.py", "levels_cli.py"):
    with open(os.path.join(copy, "s", name), "a") as out:
        out.write("# changed\n")
    now = fingerprint()
    check(now.strip() and now != first, "a change to %s makes cached results invalid" % name, now)
    first = now
shutil.rmtree(copy, ignore_errors=True)

# the local cover never leaves an L0 row to GitHub
sys.path.insert(0, DELIVERY)
sys.path.insert(0, REG)
import cover  # noqa: E402

real = cover.sh


def fake(args, root):
    if "affected" in args:
        return 0, "AFFECTED 2 of 2 rows (alpha, beta)"
    if "-c" in args:
        return 0, json.dumps({"todo": ["alpha", "beta"], "bad": [], "l0": ["alpha"]})
    return 128, ""


cover.sh = lambda args, root: (1, "") if "ls-tree" in args and False else (
    (0, "") if args[:2] == ["git", "ls-tree"] else fake(args, root))
got = cover.select(".", {"base": "main"}, ["x"])
cover.sh = real
check(got[0] == ["beta"] and "alpha" in got[1], "an L0 row stays on the local lane", got)
repo.record(changed("alpha", level="L0", seconds="0.1", cmdhash=sha("true"), reason="time:0.1"))
repo.commit()
plan = subprocess.run([sys.executable, "-B", "-c", cover.PLAN, REG], cwd=repo.path, env=repo.env, capture_output=True,
                      text=True)
check(plan.returncode == 0 and json.loads(plan.stdout.splitlines()[-1]).get("l0") == ["alpha"],
      "the cover's plan names the L0 rows", plan.stdout + plan.stderr)
repo.close()

# a one-row record change picks that row and the table's readers, not every row
# commands that name a file of their own (a command that names none always reruns)
mine = [dict(r, command="test -f data/%s" % r["id"]) for r in BASE + [row("gamma")]]
mine.append(row("reader", command="grep -q alpha .loop/regression.tsv"))
repo = Repo(mine, good() + [entry("gamma"), entry("reader")])
for r in mine:
    repo.write("data/" + r["id"], r["id"])
repo.commit()
repo.git("checkout", "-q", "-b", "loop/sel")
status, said = repo.run("run", "land", "--reuse")
repo.record(changed("beta", level="L2") + [entry("gamma"), entry("reader")])
repo.commit("one entry")
status, said = repo.run("run", "land", "--reuse")
line = next((x for x in said.splitlines() if x.startswith("AFFECTED")), "")
check("beta" in line and "reader" in line and "gamma" not in line and "alpha," not in line,
      "run --reuse picks the changed entry and the table's readers", said)
got = subprocess.run([sys.executable, os.path.join(REG, "lanes_cli.py"), "affected", "--root", repo.path,
                      ".loop/regression-relevel.tsv"], cwd=repo.path, env=repo.env, capture_output=True, text=True).stdout
check("beta" in got and "reader" in got and "gamma" not in got, "lanes_cli affected picks the same rows", got)
repo.close()

# two branches that each add a row: the merge repair joins the record
repo = Repo(BASE, good())
repo.commit()
repo.git("checkout", "-q", "-b", "other")
repo.run("add", "from-other", "--command", "true")
repo.commit("other")
repo.git("checkout", "-q", "main")
repo.git("checkout", "-q", "-b", "loop/mine")
repo.run("add", "from-mine", "--command", "true")
repo.commit("mine")
merge = repo.git("merge", "--no-edit", "other", check_it=False)
files = repo.git("diff", "--name-only", "--diff-filter=U").stdout.split()
MEND = """import os, subprocess, sys
sys.path.insert(0, sys.argv[1]); sys.dont_write_bytecode = True
import mend_tables
git = lambda *a: subprocess.run(["git"] + list(a), capture_output=True, text=True)
sys.exit(0 if mend_tables.mend(git, sys.argv[2:], "other") else 1)
"""
fixed = subprocess.run([sys.executable, "-c", MEND, DELIVERY] + files, cwd=repo.path, env=repo.env,
                       capture_output=True, text=True)
status, said = repo.run("levels", "--check")
check(merge.returncode != 0 and ".loop/regression-relevel.tsv" in files and fixed.returncode == 0 and status == 0
      and {"from-mine", "from-other"} <= set(repo.entries()), "two added rows merge with the record intact",
      "%s\n%s\n%s%s" % (files, fixed.stdout + fixed.stderr, said, merge.stdout))
repo.close()

# the excused rows and the Principles page
goal, command = "v110-pkg-secret-print:3", ("proved by the 90-day search recorded in the goal's run record (ids kept in "
                                            "the git dir, not committed)")
excused = row("done-pkg-secret-print-3", level="covered", command=command, goal=goal)
repo = Repo(BASE + [excused], good() + [entry("done-pkg-secret-print-3", old="covered", reason="excepted:TD2022")])
repo.commit()
status, said = repo.run("run", "alpha")
check(status == 0 and "EXCEPTED done-pkg-secret-print-3" in said and "not an owner record" in said,
      "the excused row is named with what excuses it", said)
repo.table(BASE + [dict(excused, command="another proof")])
ok, got = refused(repo, "LEVELS_BAD_COVERS", "done-pkg-secret-print-3")
check(ok, "a changed command ends the excuse", got)
repo.table(BASE + [excused])
page = "# P\n\n## 6. Private\n\n| R |\n|---|\n| [DEL-9 x](a) |\n| [GRD-6 y (absorbs GRD-16)](b) |\n\n## 7. Next\n"
repo.write("docs/wiki/Principles.md", page)
status, said = repo.run("levels", "--check")
check(status == 2 and "LEVELS_REQUIREMENTS" in said and "GRD-16" in said,
      "levels --check compares the requirement list with the Principles page", said)
repo.close()
sys.exit(done())
