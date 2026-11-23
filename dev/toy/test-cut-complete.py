#!/usr/bin/env python3
# reads: skills/workflow-regression/scripts/regression.py skills/workflow-regression/scripts/runs.py skills/workflow-regression/scripts/lanes_cli.py skills/workflow-regression/scripts/cutgate.py
"""cut-complete (DEL-26.4, TD1202): a row counts as run only when it finished, and a shard that cannot read its diff fails.

Each case uses the real runner (regression.py run, as a PR shard) on a temp repo, and the real cutgate.py or the generated shard step:
  known-timeout  a row on the known list that passes its row limit is LEFT, so the cut gate fails it by name;
  skipped        a row that cannot run is written SKIP, never RAN; the gate names it as skipped and does not count it as run;
  empty-cache    a run that has no rows leaves the times cache's last record alone, a run with rows writes it;
  diff-fails     the shard step stops with a message when it cannot read the diff against the base, and does not call it
                 a documents-only change; controls: a documents-only diff ends green at once, a code diff reaches the runner.
LOOP_TOY_ONLY=<case> runs one case (red proofs)."""
import os
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


def gate(files):
    work = tempfile.mkdtemp(prefix="cut-complete-gate-")
    for name, text in files.items():
        os.makedirs(os.path.dirname(os.path.join(work, name)), exist_ok=True)
        with open(os.path.join(work, name), "w") as handle:
            handle.write(text)
    done = subprocess.run([sys.executable, GATE, "s/shard-[0-7]/t.tsv"], cwd=work, capture_output=True, text=True)
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
    code, out = gate(files)
    check("skipped: sk" in out and "FAIL" not in out and code == 0, "the cut gate names the skipped row and does not count it as run (exit %d)" % code)

STEP_START, STEP_END = "      - run: |\n", "      - if: always()\n        uses: actions/upload-artifact"


def shard_step():
    """The shard job's run block, with its Actions values filled in; None-safe: the toy fails if it holds any other expression."""
    job = lanes_cli.NARROW.split("\n  shard:")[1].split("\n  affected:")[0]
    block = job.split(STEP_START, 1)[1].split(STEP_END, 1)[0]
    lines = [x[10:] if x.startswith(" " * 10) else x.strip() for x in block.splitlines()]
    text = "\n".join(lines).replace("@BASE@", "main").replace("@LEVELS@", "nightly")
    text = text.replace("${{ runner.temp }}", "$TEMP_DIR").replace("${{ matrix.shard }}", "0")
    if "${{" in text:
        sys.exit("FAIL: the shard step holds an Actions expression this toy does not fill in")
    return text


def run_step(here):
    temp = tempfile.mkdtemp(prefix="cut-complete-temp-")
    done = subprocess.run(["bash", "--noprofile", "--norc", "-e", "-c", shard_step()], cwd=here, capture_output=True, text=True,
                          env=dict(env, TEMP_DIR=temp))
    return done.returncode, done.stdout + done.stderr, os.path.join(temp, "t.tsv")


if case("diff-fails"):
    stub = "skills/workflow-regression/scripts/regression.py"

    def project(with_base, change):
        here = repo({"fast": "exit 0"})
        os.makedirs(os.path.join(here, os.path.dirname(stub)))
        with open(os.path.join(here, stub), "w") as handle:
            handle.write("print('RUNNER-REACHED')\n")
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

print("ALL PASS" if not failed else "FAILED: %d" % len(failed))
sys.exit(1 if failed else 0)
