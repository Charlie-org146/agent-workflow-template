#!/usr/bin/env python3
# windows: skip
# reads: skills/workflow-regression/scripts/lanes.py skills/workflow-regression/scripts/regression.py skills/workflow-regression/scripts/lanes_cli.py
# reads: skills/workflow-regression/scripts/tiers.py
"""tree-rules-first (TD494, TD497, TD504): the rows that run a whole-repo script (dev/package.py, test-tree.sh, test-portable.sh,
size-check.py, straight or through a wrapper such as tree-once.sh) run once, in the PR workflow's ninth cell `tree`, not in the 8 shards;
a red whole-tree row fails the tree cell and so the required `affected` job; a row a run cut for its budget goes first next time.

1. lanes.whole picks the rows that run a whole-repo script and no others.
2. regression.py in a fixture repo: with LOOP_PR_SHARD set and no --tree the whole-tree row is left out (the shards); with --tree only it
   runs; a failing whole-tree row makes the --tree run exit 1 while a shard run exits 0 (negative control); with no shard and no --tree
   every row runs (a local run is unchanged).
3. CUT first: a row marked CUT runs first; a run cut by --budget marks the rows it cut CUT, and the next run puts one of them first.
4. The rendered workflow: `tree` is a cell of the shard matrix that runs four parallel --tree runs and exits with the OR of theirs, `affected`
   needs the matrix and fails unless it is success (so a red tree fails it), and the committed regression-pr.yml is the rendered one."""
import os
import shutil
import subprocess
import sys
import tempfile

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(here, "..", ".."))
scripts = os.path.join(root, "skills", "workflow-regression", "scripts")
sys.path.insert(0, scripts)
sys.dont_write_bytecode = True
import lanes  # noqa: E402
import lanes_cli  # noqa: E402

failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def git(cwd, *args):
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t"] + list(args), cwd=cwd, check=True, capture_output=True)


def write(base, rel, text):
    os.makedirs(os.path.dirname(os.path.join(base, rel)), exist_ok=True)
    with open(os.path.join(base, rel), "w") as handle:
        handle.write(text)


with tempfile.TemporaryDirectory() as tmp:
    repo = os.path.join(tmp, "repo")
    os.makedirs(repo)
    git(repo, "init", "-q", "-b", "main")
    write(repo, ".loop/config.json", '{"base": "main"}\n')
    order = os.path.join(tmp, "order.log")
    write(repo, "dev/package.py", "import os, sys\nopen(os.environ['ORDER'], 'a').write('tree\\n')\nsys.exit(1 if os.environ.get('TREE_RED') else 0)\n")
    write(repo, "dev/toy/wrap.sh", "#!/bin/bash\npython3 dev/package.py --static\n")
    write(repo, "dev/toy/plain.sh", "#!/bin/bash\necho \"$1\" >> \"$ORDER\"\n")
    write(repo, "dev/toy/size-check.py", "print('ok')\n")
    write(repo, "dev/toy/test-portable.sh", "echo ALL PASS\n")
    with open(os.path.join(repo, ".loop", "regression.tsv"), "w") as handle:
        handle.write("# id\tlevel\tcommand\tgoal\tseen_red\tdescription\tcategory\tlink\n")
        for rid, cmd in (("r1", "sleep 2; bash dev/toy/plain.sh r1"), ("tree-row", "bash dev/toy/wrap.sh"), ("r3", "bash dev/toy/plain.sh r3"),
                         ("size-row", "python3 dev/toy/size-check.py --control x"), ("portable-row", "bash dev/toy/test-portable.sh")):
            handle.write("%s\tland\t%s\t\t2026-01-01\tx\tcriterion\t\n" % (rid, cmd))
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "rows")
    rows = lanes_cli.rows_of(repo, "land")
    check(sorted(r["id"] for r in rows if lanes.whole(repo, r, {})) == ["portable-row", "size-row", "tree-row"],
          "the rows that run package.py (through a wrapper), size-check.py or test-portable.sh are whole-tree; the others are not")
    env = dict(os.environ, LOOP_FREE_GB="100", LOOP_ROLE="", ORDER=order, LOOP_ROW_TIMES=os.path.join(tmp, "t.tsv"))
    env.pop("TREE_RED", None)

    def run(*extra, **more):
        if os.path.exists(order):
            os.remove(order)
        done = subprocess.run([sys.executable, os.path.join(scripts, "regression.py"), "run", "land"] + list(extra), cwd=repo,
                              env=dict(env, **more), capture_output=True, text=True)
        return (open(order).read().split() if os.path.exists(order) else []), done.returncode

    got, code = run()
    check(sorted(got) == ["r1", "r3", "tree"] and code == 0, "no shard and no --tree: every row runs, as before (%s)" % got)
    a, _ = run(LOOP_PR_SHARD="0/2")
    b, _ = run(LOOP_PR_SHARD="1/2")
    check("tree" not in a + b and sorted(a + b) == ["r1", "r3"], "a PR shard leaves the whole-tree rows out: the two shards run r1 and r3 only (%s + %s)" % (a, b))
    got, code = run("--tree", LOOP_PR_SHARD="0/1")
    check(got == ["tree"] and code == 0, "--tree runs only the whole-tree rows, and green it passes (%s)" % got)
    got, code = run("--tree", LOOP_PR_SHARD="0/1", TREE_RED="1")
    check(got == ["tree"] and code == 1, "a red whole-tree row fails the --tree run (exit %d): the tree cell goes red" % code)
    _, c0 = run(LOOP_PR_SHARD="0/2", TREE_RED="1")
    _, c1 = run(LOOP_PR_SHARD="1/2", TREE_RED="1")
    check(c0 == 0 and c1 == 0, "negative control: the same red row fails no shard, it is not run there (exits %d, %d)" % (c0, c1))
    with open(env["LOOP_ROW_TIMES"], "w") as handle:
        handle.write("r3\t5\tCUT\n")
    got, _ = run()
    check(got[0] == "r3", "a row marked CUT (cut for its budget last run) runs first (%s)" % got)
    os.remove(env["LOOP_ROW_TIMES"])
    shutil.rmtree(os.path.join(repo, ".git", "loop", "tests"), ignore_errors=True)  # no lane record: the --reuse run plans every row
    run("--reuse", "--budget", "3", LOOP_PR_SHARD="0/1")
    marks = dict(line.split("\t")[::2] for line in open(env["LOOP_ROW_TIMES"]).read().splitlines())
    cut = sorted(k for k, v in marks.items() if v == "CUT")
    check(bool(cut), "a run cut by --budget marks the rows it cut CUT (%s)" % cut)
    got, _ = run(LOOP_PR_SHARD="0/1")
    check(got and got[0] in ("r3", "tree") and {"r3", "tree-row"} <= set(cut), "the next run puts a row that was cut first (%s, cut %s)" % (got, cut))

flow = lanes_cli.NARROW.replace("@BASE@", "main").replace("@LEVELS@", "nightly")
job = flow.split("\n  shard:")[1].split("\n  affected:")[0]
tree_part = job.split('if [ "${{ matrix.shard }}" = tree ]; then')[1].split("fi\n")[0]
check("shard: [0, 1, 2, 3, 4, 5, 6, 7, tree]" in job and "--tree" in tree_part and "for k in 0 1 2 3" in tree_part and "wait $i || r=1" in tree_part and "exit $r" in tree_part,
      "tree is a cell of the shard matrix: four parallel --tree runs, exit status the OR of theirs")
affected = flow.split("\n  affected:")[1].split("\n  small:")[0]
check("needs: shard" in affected and 'test "${{ needs.shard.result }}" = success' in affected, "affected needs the matrix and fails unless it is success, so a red tree cell fails it")
committed = os.path.join(root, ".github", "workflows", "regression-pr.yml")
check(not os.path.exists(committed) or open(committed).read() == flow, ".github/workflows/regression-pr.yml is the rendered workflow, tree cell included")
sys.exit(1 if failed else 0)
