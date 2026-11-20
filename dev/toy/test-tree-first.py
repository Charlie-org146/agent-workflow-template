#!/usr/bin/env python3
# windows: skip
# reads: skills/workflow-regression/scripts/tiers.py skills/workflow-regression/scripts/lanes.py skills/workflow-regression/scripts/regression.py
# reads: skills/workflow-regression/scripts/lanes_cli.py skills/workflow-regression/scripts/runs.py
"""tree-rules-first (TD494, TD497): the rows that run a whole-tree checker (dev/package.py or test-tree.sh, straight or through a wrapper
such as tree-once.sh) run first in every PR's budget, ahead of the rows that name a changed file; a row the last run cut for its budget
goes first in its shard on the next run; the merge queue's small job runs `dev/package.py --static`.

1. A fixture repo changes one doc. Its tree row (wrapper -> package.py) and a changed-file row are both selected: the tree row comes first
   and, in a budget that fits one of them, is the one kept. Negative control: with lanes.whole always false the changed-file row is first
   and the tree row is left (the order TD494 fixes).
2. regression.py with a times file: a row marked CUT runs first; unmarked, the file order stands. A run cut by `--budget` marks the
   rows it cut CUT, and the next run puts them first.
3. The queue's small job runs `python3 dev/package.py --static` (skipped where an adopting repo has no dev/package.py), in the rendered
   workflow and in the committed .github/workflows/regression-pr.yml."""
import os
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
import runs  # noqa: E402
import tiers  # noqa: E402

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
    git(tmp, "init", "-q", "-b", "main")
    write(tmp, ".loop/config.json", '{"base": "main"}\n')
    write(tmp, "dev/package.py", "print('static rules hold')\n")
    write(tmp, "dev/toy/wrap.sh", "#!/bin/bash\n# reads: dev/package.py docs/\npython3 dev/package.py --static\n")
    write(tmp, "dev/toy/doc.sh", "#!/bin/bash\n# reads: docs/x.md\ngrep -q . docs/x.md\n")
    write(tmp, "dev/toy/plain.sh", "#!/bin/bash\n# reads: README.md\ntrue\n")
    write(tmp, "docs/x.md", "one\n")
    write(tmp, "README.md", "r\n")
    git(tmp, "add", ".")
    git(tmp, "commit", "-q", "-m", "base")
    git(tmp, "switch", "-q", "-c", "feat")
    write(tmp, "docs/x.md", "two\n")  # the one changed file
    git(tmp, "commit", "-q", "-am", "change a doc")
    rows = [{"id": "doc-row", "level": "land", "command": "bash dev/toy/doc.sh", "goal": "", "category": "criterion"},
            {"id": "tree-row", "level": "land", "command": "bash dev/toy/wrap.sh", "goal": "", "category": "criterion"},
            {"id": "plain-row", "level": "land", "command": "bash dev/toy/plain.sh", "goal": "", "category": "criterion"}]
    cache = {}
    check([r["id"] for r in rows if lanes.whole(tmp, r, cache)] == ["tree-row"], "only the row whose script runs package.py is a whole-tree row")
    todo, _, _, _ = tiers.plan(tmp, rows, None)
    check(todo[0] == "tree-row" and "doc-row" in todo and "plain-row" not in todo, "the whole-tree row runs first, ahead of the row naming the changed file: %s" % todo)
    est = {"doc-row": 5, "tree-row": 30, "pad": 10}
    keep, left = runs.fit([todo[0], "pad"] + todo[1:], est, 40)  # pad: another row near the change
    check("tree-row" in keep and "doc-row" in left, "in a 40 s budget the tree row is kept; a changed-file row is the one left (kept %s, left %s)" % (keep, left))
    real = lanes.whole
    lanes.whole = lambda *a, **k: False  # negative control: no whole-tree ranking
    plain, _, _, _ = tiers.plan(tmp, rows, None)
    lanes.whole = real
    keep2, left2 = runs.fit([plain[0], "pad"] + plain[1:], est, 40)
    check(plain[0] == "doc-row", "negative control: without the ranking the changed-file row is first (%s)" % plain)
    check("tree-row" in left2, "negative control: that order and the same 40 s budget leave the tree row LEFT (left %s)" % left2)

with tempfile.TemporaryDirectory() as tmp:
    repo = os.path.join(tmp, "repo")
    os.makedirs(os.path.join(repo, ".loop"))
    git(repo, "init", "-q", "-b", "main")
    write(repo, ".loop/config.json", '{"base": "main"}\n')
    order = os.path.join(tmp, "order.log")
    with open(os.path.join(repo, ".loop", "regression.tsv"), "w") as handle:
        handle.write("# id\tlevel\tcommand\tgoal\tseen_red\tdescription\tcategory\tlink\n")
        for rid, extra in (("r1", "sleep 2; "), ("r2", ""), ("r3", "")):
            handle.write("%s\tland\t%secho %s >> %s\t\t2026-01-01\tx\tcriterion\t\n" % (rid, extra, rid, order))
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "rows")
    env = dict(os.environ, LOOP_FREE_GB="100", LOOP_ROLE="", LOOP_ROW_TIMES=os.path.join(tmp, "t.tsv"))
    env.pop("LOOP_PR_SHARD", None)

    def run(*extra):
        if os.path.exists(order):
            os.remove(order)
        done = subprocess.run([sys.executable, os.path.join(scripts, "regression.py"), "run", "land"] + list(extra), cwd=repo, env=env, capture_output=True, text=True)
        return (open(order).read().split() if os.path.exists(order) else []), done.stdout + done.stderr

    check(run()[0] == ["r1", "r2", "r3"], "no mark: the file order stands")
    with open(env["LOOP_ROW_TIMES"], "w") as handle:
        handle.write("r3\t5\tCUT\n")
    got, _ = run()
    check(got[0] == "r3", "a row marked CUT (cut for its budget in the last run) runs first (%s)" % got)
    os.remove(env["LOOP_ROW_TIMES"])
    got, out = run("--reuse", "--budget", "3")
    marks = {line.split("\t")[0]: line.split("\t")[2] for line in open(env["LOOP_ROW_TIMES"]).read().splitlines()} if os.path.exists(env["LOOP_ROW_TIMES"]) else {}
    cut = sorted(k for k, v in marks.items() if v == "CUT")
    check(got == ["r1"] and cut == ["r2", "r3"], "a run cut by --budget marks the rows it cut CUT (ran %s, CUT %s)" % (got, cut))
    got, _ = run()
    check(got[:2] == ["r2", "r3"], "the next run puts the rows that were cut first (%s)" % got)

flow = lanes_cli.NARROW.replace("@BASE@", "main").replace("@LEVELS@", "nightly")
small = flow.split("  small:")[1]
check("python3 dev/package.py --static" in small and "test ! -f dev/package.py ||" in small, "the merge queue's small job runs package.py --static (not where a repo has no dev/package.py)")
committed = os.path.join(root, ".github", "workflows", "regression-pr.yml")
check(not os.path.exists(committed) or open(committed).read() == flow, ".github/workflows/regression-pr.yml is the rendered workflow, small job included")
sys.exit(1 if failed else 0)
