#!/usr/bin/env python3
# reads: skills/workflow-regression/scripts/regression.py skills/workflow-regression/scripts/runs.py skills/workflow-regression/scripts/lanes_cli.py skills/workflow-regression/scripts/cutgate.py
"""cut-complete (DEL-26.4, TD1202): a row counts as run only when it finished, and a shard that cannot read its diff fails.

Each case uses the real runner (regression.py run, as a PR shard) on a temp repo, and the real cutgate.py or the generated shard step:
  known-timeout  a row on the known list that passes its row limit is LEFT, so the cut gate fails it by name;
  skipped        a row that cannot run is written SKIP, never RAN; the gate passes it only when main's skip list holds it (SKIPPED,
                 never counted as run), and fails a skip main does not have;
  over-budget    the generated shard step fails a shard whose rows pass its budget B: the rows it had no time for are CUT and the gate names them;
  tree-budget    the tree job runs with no budget, so a whole-tree row is never cut by one;
  tree-skip      a whole-tree row that skips is judged by the same list rule as the numbered shards' rows;
  notrun         a row that could not start is NOTRUN and fails unless its skip-list row carries the notrun flag; a skip count is printed;
  validate       an unreadable skip list, a malformed times line and a missing argument each fail with a message, and a
                 failed run leaves the times cache as it was;
  empty-cache    a run that has no rows leaves the times cache's last record alone, a run with rows writes it;
  diff-fails     the shard step stops with a message when it cannot read the diff against the base, and does not call it
                 a documents-only change; controls: a documents-only diff ends green at once, a code diff reaches the runner.
LOOP_TOY_ONLY=<case> runs one case (red proofs)."""
import os
import shutil
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
scripts = os.path.join(root, "skills", "workflow-regression", "scripts")
sys.path.insert(0, scripts)
sys.dont_write_bytecode = True
import lanes_cli  # noqa: E402

REG, GATE = os.path.join(scripts, "regression.py"), os.path.join(scripts, "cutgate.py")
failed, only = [], os.environ.get("LOOP_TOY_ONLY")
env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.test", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.test",
           PYTHONDONTWRITEBYTECODE="1")


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def case(name):
    return only in (None, name)


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=env).stdout


def repo(rows, known=()):
    """A temp repo with the rows ({id: command}) and the known list ({id: reason})."""
    here = tempfile.mkdtemp(prefix="cut-complete-")
    git(here, "init", "-q", "-b", "main")
    git(here, "config", "commit.gpgsign", "false")
    os.makedirs(os.path.join(here, ".loop"))
    with open(os.path.join(here, ".loop", "regression.tsv"), "w") as handle:
        handle.write("# id\tlevel\tcommand\tgoal\tseen_red\tdescription\tcategory\tlink\n")
        handle.writelines("%s\tland\t%s\t\t2026-01-01\tx\tcriterion\t\n" % row for row in rows.items())
    with open(os.path.join(here, ".loop", "regression-known.tsv"), "w") as handle:
        handle.writelines("%s\t%s\n" % row for row in known.items()) if known else None
    git(here, "add", "-A")
    git(here, "commit", "-qm", "rows")
    return here


def shards(here, n=2):
    """Run each PR shard of the repo with the real runner (row limit 2 s); the times files by shard."""
    files = {}
    for i in range(n):
        stamp = os.path.join(here, "t.%d" % i)
        open(stamp, "w").close()
        subprocess.run([sys.executable, REG, "run", "land", "--timeout", "2"], cwd=here, capture_output=True, text=True,
                       env=dict(env, LOOP_PR_SHARD="%d/%d" % (i, n), LOOP_ROW_TIMES=stamp))
        files["s/shard-%d/t.tsv" % i] = open(stamp).read()
    return files


def gate(files, known=None):
    work = tempfile.mkdtemp(prefix="cut-complete-gate-")
    for name, text in files.items():
        os.makedirs(os.path.dirname(os.path.join(work, name)), exist_ok=True)
        with open(os.path.join(work, name), "w") as handle:
            handle.write(text)
    extra = []
    if known is not None:
        with open(os.path.join(work, "skips.tsv"), "w") as handle:
            handle.write("# id\treason\n" + "".join("%s\tskips by design\n" % one for one in known))
        extra = ["all.tsv", "skips.tsv"]
    done = subprocess.run([sys.executable, GATE, "s/shard-[0-7]/t.tsv", *extra], cwd=work, capture_output=True, text=True)
    return done.returncode, done.stdout + done.stderr


if case("known-timeout"):
    here = repo({"fast": "exit 0", "kt": "sleep 20"}, {"kt": "known: slow on purpose"})
    code, out = gate(shards(here))
    check(code == 1 and "FAIL cut or not run: kt" in out, "a known row that passes its row limit is LEFT and the cut gate fails it by name (exit %d)" % code)

if case("skipped"):
    here = repo({"fast": "exit 0", "sk": "exit 77"})
    files = shards(here)
    states = [line.split("\t")[2] for text in files.values() for line in text.splitlines() if line.startswith("sk\t")]
    check("RAN" not in states and "SKIP" in states, "a row that cannot run is written SKIP, never RAN (%s)" % states)
    code, out = gate(files, known=["sk"])
    check(code == 0 and "SKIPPED sk: skips by design" in out and "never counted as run: sk" in out and "FAIL" not in out,
          "a row on main's skip list shows as SKIPPED, is never counted as run, and the gate is green (exit %d)" % code)
    code, out = gate(files, known=["other"])
    check(code == 1 and "FAIL skipped and not skipped on main: sk" in out, "a skip that main's list does not hold turns the gate red, naming the row (exit %d)" % code)
    code, out = gate(files)
    check(code == 1 and "FAIL skipped and not skipped on main: sk" in out, "with no skip list at all a skipped row fails the gate (exit %d)" % code)

STEP_START, STEP_END = "      - run: |\n", "      - if: always()\n        uses: actions/upload-artifact"


def shard_step(cell="0"):
    """The shard job's run block, with its Actions values filled in; None-safe: the toy fails if it holds any other expression."""
    job = lanes_cli.NARROW.split("\n  shard:")[1].split("\n  affected:")[0]
    block = job.split(STEP_START, 1)[1].split(STEP_END, 1)[0]
    lines = [x[10:] if x.startswith(" " * 10) else x.strip() for x in block.splitlines()]
    text = "\n".join(lines).replace("@BASE@", "main").replace("@LEVELS@", "nightly")
    text = text.replace("${{ runner.temp }}", "$TEMP_DIR").replace("${{ matrix.shard }}", cell)
    if "${{" in text:
        sys.exit("FAIL: the shard step holds an Actions expression this toy does not fill in")
    return text


def run_step(here, cell="0"):
    temp = tempfile.mkdtemp(prefix="cut-complete-temp-")
    done = subprocess.run(["bash", "--noprofile", "--norc", "-e", "-c", shard_step(cell)], cwd=here, capture_output=True, text=True,
                          env=dict(env, TEMP_DIR=temp))
    return done.returncode, done.stdout + done.stderr, os.path.join(temp, "t.tsv")


if case("diff-fails"):
    stub = "skills/workflow-regression/scripts/regression.py"

    def project(with_base, change):
        here = repo({"fast": "exit 0"})
        os.makedirs(os.path.join(here, os.path.dirname(stub)))
        with open(os.path.join(here, stub), "w") as handle:
            handle.write("import sys\nprint('RUNNER-REACHED', ' '.join(sys.argv[1:]))\n")
        git(here, "add", "-A")
        git(here, "commit", "-qm", "stub")
        if with_base:
            git(here, "update-ref", "refs/remotes/origin/main", "HEAD")
        git(here, "checkout", "-q", "-b", "pr")
        with open(os.path.join(here, change), "w") as handle:
            handle.write("x\n")
        git(here, "add", "-A")
        git(here, "commit", "-qm", "change")
        return here

    code, out, times = run_step(project(False, "dev.py"))
    check(code != 0 and "RUNNER-REACHED" not in out and "documents and goal records only" not in out and "diff" in out,
          "a shard that cannot read the diff against the base fails with a message and is not a documents-only change (exit %d)" % code)
    code, out, times = run_step(project(True, "README.md"))
    check(code == 0 and "documents and goal records only" in out and os.path.exists(times), "control: a documents-only diff ends green at once and uploads its file (exit %d)" % code)
    code, out, times = run_step(project(True, "dev.py"))
    check(code == 0 and "RUNNER-REACHED" in out, "control: a code diff reaches the runner (exit %d)" % code)

if case("empty-cache"):  # the times cache keeps the last real record: a run with no rows writes no all.tsv
    for name, files, wrote in (("a documents-only run (every shard file empty)", {"s/shard-0/t.tsv": "", "s/shard-1/t.tsv": ""}, False),
                               ("a run with rows", {"s/shard-0/t.tsv": "a\t3\tRAN\n", "s/shard-1/t.tsv": "a\t0\tSEL\n"}, True)):
        work = tempfile.mkdtemp(prefix="cut-complete-cache-")
        for rel, text in files.items():
            os.makedirs(os.path.dirname(os.path.join(work, rel)), exist_ok=True)
            open(os.path.join(work, rel), "w").write(text)
        done = subprocess.run([sys.executable, GATE, "s/shard-[0-7]/t.tsv"], cwd=work, capture_output=True, text=True)
        check(done.returncode == 0 and os.path.exists(os.path.join(work, "all.tsv")) == wrote, "%s: the times file is %s (exit %d)" % (name, "written" if wrote else "not written", done.returncode))

if case("over-budget"):
    def budgeted(budget, sleep):
        """Four rows of `sleep` seconds, two shards of the generated step run on the real runner with B set to budget; the gate's verdict."""
        names = ["t1", "t2", "t3", "t4"]
        here = repo({n: "bash dev/%s.sh" % n for n in names})
        os.makedirs(os.path.join(here, "dev"))
        for n in names:
            with open(os.path.join(here, "dev", n + ".sh"), "w") as handle:
                handle.write("exit 0  # before the change\n")
        os.makedirs(os.path.join(here, "skills", "workflow-regression"))
        os.symlink(scripts, os.path.join(here, "skills", "workflow-regression", "scripts"))
        git(here, "add", "-A")
        git(here, "commit", "-qm", "scripts")
        git(here, "update-ref", "refs/remotes/origin/main", "HEAD")
        git(here, "checkout", "-q", "-b", "pr")
        for n in names:  # the PR changes each row's own script, so every row is selected
            with open(os.path.join(here, "dev", n + ".sh"), "w") as handle:
                handle.write("sleep %s\n" % sleep)
        git(here, "add", "-A")
        git(here, "commit", "-qm", "change")
        files = {}
        trees = {cell: shutil.copytree(here, here + "-cell" + cell, symlinks=True) for cell in ("0", "1")}  # each shard is its own checkout
        for cell in ("0", "1"):
            temp = tempfile.mkdtemp(prefix="cut-complete-over-")
            step = shard_step(cell).replace("/8 ", "/2 ")
            assert "B=866;" in step or "B=120;" in step, "the step's budget line is not B=<n>"
            step = step.replace("B=866;", "B=%d;" % budget).replace("B=120;", "B=%d;" % budget)
            subprocess.run(["bash", "--noprofile", "--norc", "-e", "-c", step], cwd=trees[cell], capture_output=True, text=True, env=dict(env, TEMP_DIR=temp))
            files["s/shard-%s/t.tsv" % cell] = open(os.path.join(temp, "t.tsv")).read() if os.path.exists(os.path.join(temp, "t.tsv")) else ""
        return gate(files, known=[])

    code, out = budgeted(1, 2)
    check(code == 1 and "FAIL cut or not run: t" in out and "CUT" in out, "a shard whose rows pass its budget B has the rows it had no time for CUT, and the gate fails and names them (exit %d)" % code)
    code, out = budgeted(866, 2)
    check(code == 0 and "FAIL" not in out, "control: the same rows within the budget end green (exit %d)" % code)

if case("tree-budget"):
    here = repo({"fast": "exit 0"})
    os.makedirs(os.path.join(here, "skills", "workflow-regression", "scripts"))
    with open(os.path.join(here, "skills", "workflow-regression", "scripts", "regression.py"), "w") as handle:
        handle.write("import sys\nprint('RUNNER-REACHED', ' '.join(sys.argv[1:]))\n")
    os.symlink(GATE, os.path.join(here, "skills", "workflow-regression", "scripts", "cutgate.py"))
    os.makedirs(os.path.join(here, ".loop"), exist_ok=True)
    open(os.path.join(here, ".loop", "regression-skips.tsv"), "w").write("# id\treason\n")
    git(here, "add", "-A")
    git(here, "commit", "-qm", "stub")
    git(here, "update-ref", "refs/remotes/origin/main", "HEAD")
    git(here, "checkout", "-q", "-b", "pr")
    with open(os.path.join(here, "dev.py"), "w") as handle:
        handle.write("x\n")
    git(here, "add", "-A")
    git(here, "commit", "-qm", "change")
    code, out, times = run_step(here, "tree")
    check(code == 0 and "RUNNER-REACHED" in out and "--tree" in out and "--budget -1" in out,
          "the tree job runs with no budget (--budget -1), so a whole-tree row is not cut by one (exit %d)" % code)
    code, out, times = run_step(here, "3")
    check(code == 0 and "--budget 866" in out and "--tree" not in out, "control: a numbered shard keeps its budget and does not take the tree line (exit %d)" % code)

if case("tree-skip"):  # a whole-tree row that skips goes through the same list rule as a numbered shard's rows
    def tree_project(command_exit):
        here = repo({"ts": "python3 dev/package.py"})
        os.makedirs(os.path.join(here, "dev"))
        with open(os.path.join(here, "dev", "package.py"), "w") as handle:
            handle.write("raise SystemExit(0)  # before the change\n")
        os.makedirs(os.path.join(here, "skills", "workflow-regression"))
        os.symlink(scripts, os.path.join(here, "skills", "workflow-regression", "scripts"))
        os.makedirs(os.path.join(here, ".loop"), exist_ok=True)
        with open(os.path.join(here, ".loop", "regression-skips.tsv"), "w") as handle:
            handle.write("# id\treason\n")
        git(here, "add", "-A")
        git(here, "commit", "-qm", "tree row")
        git(here, "update-ref", "refs/remotes/origin/main", "HEAD")
        git(here, "checkout", "-q", "-b", "pr")
        with open(os.path.join(here, "dev", "package.py"), "w") as handle:  # the PR changes the whole-tree row's own script
            handle.write("raise SystemExit(%d)\n" % command_exit)
        git(here, "add", "-A")
        git(here, "commit", "-qm", "change")
        return here

    code, out, times = run_step(tree_project(77), "tree")
    check(code != 0 and "FAIL skipped and not skipped on main: ts" in out, "a whole-tree row that skips and is not on main's skip list fails the tree job by name (exit %d)" % code)
    code, out, times = run_step(tree_project(0), "tree")
    check(code == 0 and "FAIL" not in out, "control: a whole-tree row that passes ends the tree job green (exit %d)" % code)
    here = tree_project(1)
    code, out, times = run_step(here, "tree")
    check(code != 0 and not os.path.exists(os.path.join(here, "tree.tsv")), "a whole-tree row that fails ends the tree job red before the gate runs (exit %d)" % code)
    here = tree_project(77)
    with open(os.path.join(here, ".loop", "regression-skips.tsv"), "w") as handle:
        handle.write("# id\treason\nts\tskips by design\n")
    code, out, times = run_step(here, "tree")
    check(code == 0 and "SKIPPED ts: skips by design" in out, "control: a whole-tree row on main's skip list is SKIPPED and the tree job is green (exit %d)" % code)

if case("notrun"):
    notrun = {"s/shard-0/t.tsv": "fast\t1\tRAN\nnr\t0\tNOTRUN\n", "s/shard-1/t.tsv": "fast\t0\tSEL\nnr\t0\tSEL\n"}
    code, out = gate(notrun, known=["nr"])
    check(code == 1 and "FAIL could not run: nr" in out, "a row that could not start fails even when its id is on the skip list (exit %d)" % code)
    code, out = gate(notrun, known=["nr\tcould not start here\tnotrun"])
    check(code == 0 and "SKIPPED nr" in out and "FAIL" not in out, "a skip-list row carrying the notrun flag and its reason passes a row that could not start (exit %d)" % code)
    two = {"s/shard-0/t.tsv": "fast\t1\tRAN\nsk\t0\tSKIP\n", "s/shard-1/t.tsv": "fast\t0\tSEL\nsk\t0\tSEL\n"}
    code, out = gate(two, known=["sk"])
    check("skipped, never counted as run: sk (1 of 2 selected rows)" in out, "the gate prints how many of the selected rows were skipped (exit %d)" % code)
    from completion import state  # noqa: E402
    check(state("", "x", [], ["x"], [{"id": "x", "state": "SKIPPED", "notrun": True}]) == "NOTRUN"
          and state("", "x", [], ["x"], [{"id": "x", "state": "SKIPPED", "notrun": False}]) == "SKIP", "the writer tells a skip the row asked for from a row that could not start")

if case("validate"):
    work = tempfile.mkdtemp(prefix="cut-complete-validate-")
    os.makedirs(os.path.join(work, "s", "shard-0"))
    good = "a\t3\tRAN\n"
    open(os.path.join(work, "s", "shard-0", "t.tsv"), "w").write(good)
    open(os.path.join(work, "all.tsv"), "w").write("keep\t1\t\n")

    def call(*args, files=None):
        if files is not None:
            open(os.path.join(work, "s", "shard-0", "t.tsv"), "w").write(files)
        done = subprocess.run([sys.executable, GATE, *args], cwd=work, capture_output=True, text=True)
        return done.returncode, done.stdout + done.stderr

    code, out = call("s/shard-[0-7]/t.tsv", "all.tsv", "no-such-list.tsv")
    check(code == 1 and "FAIL cannot read the skip list no-such-list.tsv" in out and "not skipped on main" not in out, "an unreadable skip list is named as such, not blamed on the rows (exit %d)" % code)
    for bad, why in (("a\tx\tRAN\n", "seconds"), ("a\t-3\tRAN\n", "seconds"), ("a\t3\tWHAT\n", "status"), ("a\n", "fields"), ("a\tnan\tRAN\n", "seconds")):
        before = open(os.path.join(work, "all.tsv")).read()
        code, out = call("s/shard-[0-7]/t.tsv", "all.tsv", files=bad)
        check(code == 1 and "FAIL malformed times line: s/shard-0/t.tsv:1" in out and why in out and open(os.path.join(work, "all.tsv")).read() == before,
              "a malformed times line (%s) fails with its file and line, and the times cache is left as it was (exit %d)" % (why, code))
    code, out = call("s/shard-[0-7]/t.tsv", "all.tsv", files="old\t9\t\na\t3\tRAN\n")
    check(code == 0, "control: a historical line with an empty status is not malformed (exit %d)" % code)
    done = subprocess.run([sys.executable, GATE], cwd=work, capture_output=True, text=True)
    check(done.returncode == 2 and "usage:" in done.stderr, "no arguments: exit 2 with a usage line on stderr (exit %d)" % done.returncode)
    os.chmod(work, 0o500)
    try:
        code, out = call("s/shard-[0-7]/t.tsv", "new.tsv", files=None)
    except OSError:
        code, out = 99, ""
    os.chmod(work, 0o700)
    check(code == 1 and "FAIL cannot write the times file new.tsv" in out, "a times file that cannot be written is named, with exit 1 (exit %d)" % code)

print("ALL PASS" if not failed else "FAILED: %d" % len(failed))
sys.exit(1 if failed else 0)
