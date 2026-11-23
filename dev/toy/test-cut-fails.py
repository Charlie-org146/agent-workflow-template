#!/usr/bin/env python3
# reads: skills/workflow-regression/scripts/regression.py skills/workflow-regression/scripts/lanes_cli.py skills/workflow-regression/scripts/cutgate.py .github/workflows/regression-pr.yml
"""cut-fails-checks (DEL-26.4, #5757): a test cut for time, or not run, fails the PR's checks, naming the test and its time.

The affected job of the PR workflow runs scripts/cutgate.py, which reads the shard files `s/shard-[0-7]/t.tsv` (rows `id TAB seconds TAB status`; RAN on the
shard that ran the row, SEL on the others, CUT when the shard's budget ran out, LEFT when the row passed its limit). A row that
is SEL or RAN somewhere and RAN nowhere is unfinished: the step prints `FAIL cut or not run: <id> <STATUS> <seconds>s: ...`
and exits non-zero. Each case runs the step's real command (taken from the generator by text, so the toy fails if the workflow
does not call cutgate.py) on files the
real writer (regression.merged and cmd_run's status rule) made, and has a control that must stay green.
LOOP_TOY_ONLY=<case> runs one case (red proofs); the generator is the tree's own lanes_cli.py."""
import os
import subprocess
import sys
import tempfile
import time

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
scripts = os.path.join(root, "skills", "workflow-regression", "scripts")
sys.path.insert(0, scripts)
sys.dont_write_bytecode = True
import lanes_cli  # noqa: E402
import regression  # noqa: E402

failed, only = [], os.environ.get("LOOP_TOY_ONLY")


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def block():
    """The affected job's step: the one `- run:` line that calls cutgate.py, with the script at its path in this tree."""
    lines = [x.strip()[7:] for x in lanes_cli.NARROW.splitlines() if x.strip().startswith("- run:") and "cutgate.py" in x]
    if len(lines) != 1 or "${{" in lines[0]:
        sys.exit("FAIL: the affected step does not call cutgate.py exactly once, or holds an Actions expression")
    return lines[0].replace("skills/workflow-regression/scripts/cutgate.py", os.path.join(scripts, "cutgate.py"))


def written(rows, path):
    """What one shard writes: regression.merged's states and cmd_run's status rule, from {id: (seconds, how)}.
    how is ran | sel | cut | left."""
    done = [{"id": k, "seconds": v[0]} for k, v in rows.items() if v[1] == "ran"]
    left = [k for k, v in rows.items() if v[1] == "left"]
    table = regression.merged(path, done, left, 200)
    for key, (sec, how) in rows.items():
        row = table.setdefault(key, [0, ""])
        row[1] = row[1] if row[1] == "LEFT" else "CUT" if how == "cut" else "RAN" if how == "ran" else "SEL"
        if how == "cut":
            row[0] = sec
    return "".join("%s\t%s\t%s\n" % (k, *v) for k, v in sorted(table.items()))


def step(files):
    """Run the step's command on {relative path: text} in a fresh tree: (exit code, output)."""
    work = tempfile.mkdtemp(prefix="cut-fails-")
    files = dict({".loop/regression-skips.tsv": "# id\treason\n"}, **files)  # the checkout of the affected job holds main's skip list
    if any(k.startswith("s/shard-") for k in files):  # the job downloads all 8 numbered shard artifacts; a shard with no row uploads an empty file
        files = dict({"s/shard-%d/t.tsv" % i: "" for i in range(8)}, **files)
    for name, text in files.items():
        os.makedirs(os.path.dirname(os.path.join(work, name)), exist_ok=True)
        open(os.path.join(work, name), "w").write(text)
    done = subprocess.run(["bash", "--noprofile", "--norc", "-eo", "pipefail", "-c", block()], cwd=work, capture_output=True, text=True)
    step.last = work
    return done.returncode, done.stdout + done.stderr


def shards(per, n=2):
    """Shard files for rows {id: [(shard of owner, seconds, how)]}: the owner's how, SEL on the others."""
    empty = tempfile.mkdtemp(prefix="cut-fails-")
    files = {}
    for i in range(n):
        mine = {k: (v[1], v[2] if i == v[0] else "sel") for k, v in per.items()}
        files["s/shard-%d/t.tsv" % i] = written(mine, os.path.join(empty, "none"))
    return files


def case(name):
    return not only or only == name


if case("writer"):  # the premise every case rests on, from the real writer
    path = os.path.join(tempfile.mkdtemp(prefix="cut-fails-"), "t.tsv")
    open(path, "w").write("a\t5\tRAN\nb\t9\tLEFT\nc\t3\tCUT\n")
    old = regression.merged(path)
    check(old == {"a": [5.0, ""], "b": [9.0, ""], "c": [3.0, "CUT"]},
          "a restored times file keeps only CUT as a state: its RAN and LEFT lines come back with no state (%s)" % old)
    out = written({"slow": (0, "left"), "fast": (1, "ran")}, path + ".new")
    check("slow\t200\tLEFT" in out and "fast\t1\tRAN" in out, "the real writer stamps a row past its limit LEFT at the limit and a row that ran RAN")

if case("left"):
    code, out = step(shards({"fast": (0, 1, "ran"), "slow": (0, 0, "left")}))
    check(code == 1 and "FAIL cut or not run: slow LEFT 200s" in out and "fast" not in out.replace("run twice", ""),
          "a row LEFT on its shard (SEL on the other) fails the step and is named with its status and the limit (exit %d)" % code)

if case("cut"):
    code, out = step(shards({"fast": (0, 1, "ran"), "slow": (1, 3, "cut")}))
    check(code == 1 and "FAIL cut or not run: slow CUT 3s" in out, "a row CUT by a shard's budget fails the step and is named with its time (exit %d)" % code)

if case("not-run"):
    code, out = step({"s/shard-0/t.tsv": "fast\t1\tRAN\nslow\t0\tSEL\n", "s/shard-1/t.tsv": "fast\t0\tSEL\nslow\t0\tSEL\n"})
    check(code == 1 and "FAIL cut or not run: slow not run" in out, "a row selected everywhere and RAN nowhere fails the step as not run (exit %d)" % code)

if case("two"):
    code, out = step(shards({"a": (0, 4, "cut"), "b": (1, 0, "left"), "c": (0, 1, "ran")}))
    check(code == 1 and "FAIL cut or not run: a CUT 4s" in out and "FAIL cut or not run: b LEFT 200s" in out and ": c " not in out,
          "two unfinished rows are both named and the finished row is not (exit %d)" % code)

if case("green"):
    code, out = step(shards({"a": (0, 1, "ran"), "b": (1, 2, "ran")}))
    check(code == 0 and "FAIL" not in out, "control: every selected row RAN on some shard, the step is green (exit %d)" % code)

if case("stale"):
    files = shards({"a": (0, 1, "ran")})
    files["s/shard-0/t.tsv"] += "old\t9\tCUT\n"
    files["s/shard-1/t.tsv"] += "gone\t9\tRAN\nlate\t9\tLEFT\n"
    code, out = step(files)
    check(code == 0, "control: the gate reads this run's selected rows, so a line left over for a row not selected this run changes nothing (exit %d)" % code)
    docs = {"s/shard-%d/t.tsv" % i: "x\t5\tRAN\ny\t9\tLEFT\nz\t3\tCUT\n" for i in range(8)}
    code, out = step(docs)
    check(code == 0, "control: a documents-only run (every shard uploads the restored previous file, no SEL line) is green (exit %d)" % code)

if case("tree"):
    files = shards({"slow": (0, 0, "left")})
    files["s/shard-tree/t.tsv"] = "slow\t5\tRAN\n"
    code, out = step(files)
    check(code == 1 and "slow LEFT" in out, "the tree artifact's stale RAN line for a row this run LEFT does not hide it (exit %d)" % code)

if case("empty"):
    code, out = step({"s/readme": "x"})
    check(code != 0 and not os.path.exists(os.path.join(step.last, "all.tsv")),
          "no shard file at all is red and leaves no all.tsv, so an empty times file is never saved to the cache (exit %d)" % code)
    code, out = step({"s/shard-%d/t.tsv" % i: "" for i in range(8)})
    check(code == 0, "control: shards that took the documents-only exit upload empty files and the step is green (exit %d)" % code)

if case("generated"):
    flow = lanes_cli.NARROW
    disk = open(os.path.join(root, ".github", "workflows", "regression-pr.yml")).read()
    check(lanes_cli.NARROW in disk or all(x in disk for x in ("cutgate.py", "shard-[0-7]")), "the workflow on disk carries the step")
    call = "      - run: python3 skills/workflow-regression/scripts/cutgate.py 's/shard-[0-7]/t.tsv' all.tsv .loop/regression-skips.tsv 8\n"
    check(call in flow and "FAIL cut or not run" not in flow,
          "the affected step calls the one script on the numbered shard files with the times file and main's skip list, and the template holds no copy of its check")
    check(call not in flow.replace(" .loop/regression-skips.tsv", "") and call not in flow.replace(" 8\n", "\n") and call not in flow.replace(" all.tsv", "") and call not in flow.replace("[0-7]", "0"),
          "negative control: a call without the skip list, the times file or the numbered glob is not the call the step must make")
    check("if: always() && needs.shard.result == 'success'\n        uses: actions/cache/save" in flow,
          "the times cache is saved even when the affected step is red, so cut rows keep their marks")
    check("T=${{ runner.temp }}/t.tsv;" in flow and '>>$T; exit 0' in flow and "> $T; exit 0" not in flow,
          "the documents-only exit creates the shard file with >> and never truncates the restored times")
    last = flow.split("\n  affected:")[1].split("\n  small:")[0].rstrip().splitlines()[-1].strip()
    check(last == '- run: test "${{ needs.shard.result }}" = success', "the last step of the affected job fails it when a shard job failed: %s" % last)
    check("regression.py run \"$id\"" not in flow and "not failed" not in flow,
          "the affected step reruns nothing and no log line says a cut row is not failed")

if case("help"):  # the package check runs every script alone with --help and wants exit 0 (dev/package.py)
    for flag in ("--help", "-h"):
        r = subprocess.run([sys.executable, "-E", "-s", os.path.join(scripts, "cutgate.py"), flag], capture_output=True, text=True, cwd=tempfile.mkdtemp(prefix="cut-fails-help-"))
        check(r.returncode == 0 and "cut gate" in r.stdout, "cutgate.py %s answers with its description and exits 0 (exit %d)" % (flag, r.returncode))

if case("time"):  # job-time measurement: the step on 8 shard files of 240 rows each
    rows = {"row%03d" % i: (i % 8, 1, "ran") for i in range(240)}
    files = shards(rows, 8)
    start = time.time()
    code, out = step(files)
    took = time.time() - start
    check(code == 0 and took < 5, "measure: the affected step takes %.2f s on 8 shard files of 240 rows (limit 5 s)" % took)

print("ALL PASS" if not failed else "%d FAILED" % len(failed))
sys.exit(1 if failed else 0)
