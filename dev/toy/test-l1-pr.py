#!/usr/bin/env python3
# reads: skills/workflow-regression/scripts/lanes_cli.py skills/workflow-regression/scripts/completion.py
# reads: skills/workflow-regression/scripts/cutgate.py dev/toy/lvl_fixture.py
"""v110-lvl-l1: the pull request workflow runs L1 and the merge queue is unchanged (line 3), and the miss report (line 6).
usage: test-l1-pr.py [queue|missed]"""
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.dont_write_bytecode = True
from lvl_fixture import REG, check, done  # noqa: E402

sys.path.insert(0, REG)
import lanes_cli  # noqa: E402
import completion  # noqa: E402

# the merge queue's job and the permissions, as main had them before this goal
SMALL = """  small:
    if: github.event_name == 'merge_group'
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          persist-credentials: false
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python3 skills/workflow-docs/scripts/docs.py check
      - run: test ! -f dev/package.py || python3 dev/package.py --static
      - run: find skills -name '*.py' -exec python3 -m py_compile {} +
      - run: python3 skills/workflow-docs/scripts/criteria.py render --check
"""
PERMISSIONS = "permissions:\n  contents: read\n"
DOCS_LINE = ("""printf %s "$D" | grep -qvE '[.]md$|^[.]loop/(goals|kept)/' || { echo "documents and goal records only: no """
             """rows to run"; >>$T; exit 0; }""")


def part(flow, start, end):
    return flow[flow.index(start):flow.index(end) if end else len(flow)]


def queue_ok(flow):
    """The queue's job and the workflow's permissions equal main's, and no other job gained permissions or runs in the queue."""
    return part(flow, "  small:", "") == SMALL and part(flow, "permissions:", "concurrency:") == PERMISSIONS and \
        flow.count("permissions:") == 1 and "regression.py run" not in part(flow, "  small:", "") and \
        all("github.event_name != 'merge_group'" in part(flow, a, b).split("steps:")[0]
            for a, b in (("  shard:", "  affected:"), ("  affected:", "  small:"))) and flow.count("\n  small:") == 1


def queue():
    flow = lanes_cli.NARROW
    check(queue_ok(flow), "line 3: the merge queue runs no test row and its job and the permissions are as before")
    check(not queue_ok(flow.replace("docs.py check", "docs.py check\n      - run: python3 x/regression.py run land")),
          "control: a row run added to the queue job is caught")
    check(not queue_ok(flow.replace("  contents: read\n", "  contents: read\n  issues: write\n")), "control: a new permission is caught")
    check(not queue_ok(flow.replace("always() && github.event_name != 'merge_group'", "always()")),
          "control: the affected job running in the queue is caught")
    shard = part(flow, "  shard:", "  affected:")
    check('R="python3 skills/workflow-regression/scripts/regression.py run @LEVELS@ --reuse --tier goal"' in shard and
          "B=866;" in shard and "cutgate.py $T tree.tsv" in shard and DOCS_LINE in shard,
          "the shard keeps its command, its 866 s budget, its cut gate and its documents-only exit")
    check("always() && github.event_name != 'merge_group'" in part(flow, "  affected:", "  small:"), "affected keeps always()")
    check("trap 'c=$?; echo \"end $(date +%s) $c\" >> \"$S\"' EXIT" in shard and 'echo "start $(date +%s)" > $S' in shard,
          "every leg writes its span, its end even when a row fails or it exits early")
    check("            ${{ runner.temp }}/t.tsv\n            ${{ runner.temp }}/span.txt\n" in shard and
          "name: flaky-${{ matrix.shard }}\n          path: ${{ runner.temp }}/flaky.tsv\n          if-no-files-found: ignore" in shard
          and "export LOOP_FLAKY_FILE=${{ runner.temp }}/flaky.tsv" in shard,
          "the times, span and flip files are uploaded from explicit paths; a flip file only exists after a flip")
    for names, want in (([], "docs"), (["README.md"], "docs"), ([".loop/goals/x.txt", "docs/a.md"], "docs"),
                        ([".loop/kept/x.tsv"], "docs"), (["a.py"], "code"), (["docs/a.md", ".loop/regression.tsv"], "code")):
        shell = subprocess.run(["bash", "-c", 'D=$1; T=/dev/null; ' + DOCS_LINE + '; echo code', "x", "\n".join(names)],
                               capture_output=True, text=True).stdout.strip().split("\n")[-1]
        shell = "code" if shell == "code" else "docs"
        check(completion.pr_select(names) == want == shell, "pr_select and the shard's shell test agree on %s" % (names,),
              "%s %s" % (completion.pr_select(names), shell))


def legs(spans, rows, config=None):
    """Run the cut gate over shard files in a temporary folder. spans: leg -> (start, end or None) in minutes; rows: leg ->
    [(id, seconds, status)]."""
    top = tempfile.mkdtemp(prefix="l1-legs-")
    os.makedirs(os.path.join(top, ".loop"))
    if config is not None:
        with open(os.path.join(top, ".loop", "config.json"), "w") as out:
            out.write(config)
    for leg in [str(i) for i in range(8)] + ["tree"]:
        folder = os.path.join(top, "s", "shard-" + leg)
        os.makedirs(folder)
        with open(os.path.join(folder, "t.tsv"), "w") as out:
            out.write("".join("%s\t%s\t%s\n" % r for r in rows.get(leg, [])))
        start, end = spans.get(leg, (0, 1))
        with open(os.path.join(folder, "span.txt"), "w") as out:
            out.write("start %d\n" % (1000 + start * 60) + ("end %d 0\n" % (1000 + end * 60) if end is not None else ""))
    got = subprocess.run([sys.executable, os.path.join(REG, "cutgate.py"), "s/shard-[0-7]/t.tsv", "all.tsv", "skips.tsv", "8"],
                         cwd=top, capture_output=True, text=True)
    return got.returncode, got.stdout + got.stderr


def ran(*specs):
    return [(k, s, "RAN") for k, s in specs]


def missed():
    even = {str(i): ran(("r%d" % i, 60)) for i in range(8)}
    slow = dict(even, tree=ran(("big1", 250), ("big2", 200), ("big3", 150)))
    status, said = legs({"tree": (0, 11)}, slow)
    check(status == 0 and "missed: the three slowest rows took 10.0 of the 11.0 minutes" in said and
          "slowest rows: big1 250s, big2 200s, big3 150s" in said and "l1_minutes is 10; the legs took 11.0 minutes" in said and
          "fix: move the slowest row to L2 with regression.py level <id> --test-level L2" in said,
          "line 6: 11 minutes shows missed: with the three slowest rows, the tree leg's among them, and every chosen row ran", said)
    status, said = legs({"tree": (0, 9)}, slow)
    check(status == 0 and "missed:" not in said, "control: 9 minutes prints no missed:", said)
    status, said = legs({"tree": (0, 11)}, dict(slow, **{"0": [("r0", 60, "RAN"), ("cached", 900, "")]}))
    check("cached 900s" not in said and "(rows 18.0)" in said, "a cached time that did not run is not counted", said)
    many = {str(i): ran(*[("l%dr%d" % (i, n), 20) for n in range(6)]) for i in range(8)}
    _, said = legs({"0": (0, 11)}, dict(many, **{"0": ran(*[("x%d" % n, 20) for n in range(20)])}))
    check("missed: one leg ran 20 rows past the others" in said, "cause: one leg ran far past the others", said)
    flat = {str(i): ran(*[("l%dr%d" % (i, n), 20) for n in range(12)]) for i in range(8)}
    _, said = legs({"0": (0, 4), "1": (8, 12)}, flat)
    check("missed: the legs started 8 minutes apart: runner queue wait" in said, "cause: the legs started far apart", said)
    _, said = legs({"0": (0, 11)}, flat)
    check("missed: no single cause: the rows add up" in said, "cause: no single one", said)
    status, said = legs({"tree": (0, None), "0": (0, 9)}, slow)
    check("note: leg shard-tree has no end" in said and "missed:" not in said,
          "a leg with no end is named as killed and left out of the turnaround", said)
    status, said = legs({"tree": (0, 11)}, dict(slow, **{"1": [("r1", 60, "RAN"), ("gone", 5, "CUT")], "2": [("r2", 60, "RAN"), ("gone", 5, "SEL")]}))
    check(status == 1 and "FAIL cut or not run: gone" in said, "the cut gate still fails a row that was cut", said)
    status, said = legs({"tree": (0, 11)}, slow, '{"l1_minutes": 12}')
    check(status == 0 and "missed:" not in said, "l1_minutes from the config is the goal", said)
    for text in ('{"l1_minutes": true}', '{"l1_minutes": 0}', '{"l1_minutes": "abc"}', '{"l1_minutes": null}'):
        status, said = legs({}, even, text)
        check(status != 0 and "L1_MINUTES_BAD" in said and "run twice" not in said,
              "a bad l1_minutes is refused before any work: %s" % text, said)
    check(completion.l1_minutes({}) == 10, "an absent key means 10")


if __name__ == "__main__":
    for name in sys.argv[1:] or ["queue", "missed"]:
        {"queue": queue, "missed": missed}[name]()
    sys.exit(done())
