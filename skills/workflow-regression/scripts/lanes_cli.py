#!/usr/bin/env python3
"""Ask lanes.py which regression rows a change can affect, what a row depends on, and whether test headers hold.

usage: lanes_cli.py affected [--root DIR] [--level land|nightly|all] PATH...
       lanes_cli.py deps [--root DIR] COMMAND [--why PATH]
       lanes_cli.py check [--root DIR] [SCRIPT...]
       lanes_cli.py merge-runs [--root DIR]

affected  `AFFECTED n of m rows (ids)` for a change to PATH, plus `ALWAYS <id>: <reason>` for rows that run on every change and
          `UNMAPPED`/`DELETED <path>` when no row maps the file (the rows naming it and the runners run). No record is read;
          the known list picks changed lines' rows.
deps      a row command's dependency paths, then `ALWAYS <command>: <reason>`; --why PATH prints the chain.
check     every `# reads:` problem of the test scripts (default: each dev/toy/test-*.sh a row names) as `<CODE> <file>:<line>: <what>`
          plus a `fix:` line. Exit 0 clean, 1 problems.
merge-runs  merge the lane record's row results into .loop/regression-runs.tsv under slots.py's row lock (goal.py pr). Exit 1 on error.
The root is the git top level unless --root. Usage errors exit 2; LANES_DEBUG=1 shows the trace.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tiers, lanes, narrow  # noqa: E401,E402

os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")

FIX = {
    "LANES-DECL-NONE": "add '# reads: <the files it runs>' at the top of {file}",
    "LANES-DECL-PLACE": "move # reads: into {file}'s top comment block",
    "LANES-DECL-PATTERN": "declare each file or the globbed folder",
    "LANES-DECL-ESCAPE": "declare repo-relative paths",
    "LANES-DECL-MISSING": "fix or remove that path in {file}'s # reads:",
    "LANES-DECL-FOLDER-UNBACKED": "declare the files {file} runs, not the folder",
    "LANES-DECL-GLOB": "declare the globbed folder in {file}'s # reads:",
    "LANES-DECL-FOLDER": "list the files {file} runs from that folder in # reads:",
    "LANES-DECL-TREE": "add skills/ to the # reads: line of {file}",
}
TEST = re.compile(r"(?<![\w./-])(dev/toy/test-[\w-]+\.sh)")


def usage(message):
    sys.stderr.write("lanes_cli.py: %s\n" % message)
    sys.exit(2)


def top(given):
    if given:
        return os.path.abspath(given)
    done = lanes.git(os.getcwd(), "rev-parse", "--show-toplevel")
    return done.strip() if done else usage("not in a git repo; run from the repo or pass --root DIR")


def rows_of(root, level):
    path = os.path.join(root, ".loop", "regression.tsv")
    if not os.path.isfile(path):
        usage("no .loop/regression.tsv under %s; use --root" % root)
    rows = []
    with open(path) as handle:
        for number, line in enumerate(handle, 1):
            cells = line.rstrip("\n").split("\t")
            if not line.strip() or line.startswith("#"):
                continue
            if len(cells) < 3:
                raise ValueError(".loop/regression.tsv:%d has fewer than 3 columns" % number)
            if level == "all" or cells[1] == level:
                rows.append({"id": cells[0], "level": cells[1], "command": cells[2]})
    return rows


def relative(root, path):
    here = os.path.realpath(os.getcwd())
    base = here if (here + "/").startswith(os.path.realpath(root) + "/") else root  # relative to --root
    full = os.path.realpath(os.path.join(base, path))
    rel = os.path.relpath(full, os.path.realpath(root))
    if rel.startswith(".."):
        usage("path outside the repo: %s" % path)
    return rel


def picked(root, rows, path, cache):
    return {r["id"] for r in rows if lanes.names_any(root, r["command"], [path], cache)
            or lanes.hits(lanes.RUNNER, lanes.closure(root, r["command"], cache)[0])}


def table_changed(root, name):
    """Ids whose line in .loop/<name> differs from the merge-base or base tip; None if neither."""
    base = tiers.config(root).get("base") or "main"
    ats = [at for at in (tiers.merge_base(root, base), *[(lanes.git(root, "rev-parse", "--verify", "-q", ref) or "").strip()
            for ref in ("origin/" + base, base)]) if at][:2]
    if not ats:
        return None
    now, memo = tiers.current(root, name), {}
    return {rid for at in ats for rid in set(now) | set(lanes.table(root, at, name, memo))
            if lanes.table(root, at, name, memo).get(rid) != now.get(rid)}


def affected(root, rows, paths, cache):
    """(rerun ids, notes) for a change to paths: plan()'s rules, no record."""
    ids, notes, real = set(), [], False
    known = table_changed(root, "regression-known.tsv") if ".loop/regression-known.tsv" in paths else None
    edited = table_changed(root, "regression.tsv") if lanes.TABLE in paths else None
    for row in rows:
        lanes.closure(root, row["command"], cache)
        if cache.get(("why", row["command"])):
            notes.append("ALWAYS %s: %s" % (row["id"], cache["why", row["command"]]))
    for path in [p.replace("\\", "/") for p in paths]:  # NO_EFFECT names use / on Windows too
        if not os.path.exists(os.path.join(root, path)) and not lanes.no_effect(path):
            ids |= picked(root, rows, path, cache)
            notes.append("DELETED %s: the rows that name it and the runners" % path)
            real = True  # a deleted non-NO_EFFECT file is a real change: root runners run (#4554)
            continue
        if path == ".loop/regression-known.tsv" and known is not None:
            hit = {r["id"] for r in rows} & known
        elif path == lanes.TABLE and edited is not None:
            hit = ({r["id"] for r in rows} & edited) | {r["id"] for r in rows if lanes.names_table(root, r["command"], cache)
            or lanes.closure(root, r["command"], cache)[1]}
        elif path in (lanes.TABLE, ".loop/regression-known.tsv"):  # never unmapped
            hit = {r["id"] for r in rows if lanes.reads_table(root, r["command"], cache)}
        else:
            hit = {r["id"] for r in rows if lanes.touches(root, r["command"], path, cache)}
        no_effect = path in (lanes.TABLE, ".loop/regression-known.tsv") or lanes.no_effect(path)
        if not hit and not no_effect and not any(lanes.hits(path, lanes.closure(root, r["command"], cache)[0])
            for r in rows):
            ids |= picked(root, rows, path, cache)
            notes.append("UNMAPPED %s: the rows that name it and the runners; no row reads it (add it to a script's "
                         "# reads: if one should)" % path)
            real = real or not no_effect
            continue
        ids, real = ids | hit, real or not no_effect
    if real:  # root runners rerun on a real change, not on NO_EFFECT files only
        ids |= {r["id"] for r in rows if lanes.closure(root, r["command"], cache)[1]}
    return sorted(ids), notes


def check(root, scripts, cache):
    """Every header problem of the test scripts as (code, file, line, what); LANES-DECL-NONE for no header."""
    out = []
    for rel in scripts:
        paths, problems = narrow.header(root, rel, cache)
        if paths is None and not problems:
            out.append(("LANES-DECL-NONE", rel, 1, "test script has no # reads: header"))
            continue
        out += problems + narrow.narrow(root, [rel], cache)[1]
    return sorted(set(out), key=lambda p: (p[1], p[2], p[0], p[3]))


def chain(parent, path):
    links = [path]
    while parent.get(links[-1]) and parent[links[-1]] not in links:
        links.append(parent[links[-1]])
    return " -> ".join(reversed(links))


def merge_runs(root):
    """The lane record's row results, with any flaky flag (tiers.py), into regression-runs.tsv."""
    import runs, slots
    record, _ = lanes.load(lanes.record_path(root), root)
    rows = (record or {}).get("rows") or {}
    done = [dict(id=key, state=value.get("status"), **{k: value[k] for k in ("flaky",) if k in value})
            for key, value in sorted(rows.items()) if value.get("status") in ("PASS", "FAIL")]
    if done:
        day = time.strftime("%Y-%m-%d", time.gmtime())
        head = (lanes.git(root, "rev-parse", "HEAD") or "").strip()
        slots.edit(root, "regression-runs.tsv", lambda: runs.write(root, done, day, head))
    return 0


NARROW = """# Written by workflow-regression (regression.py workflow). The rows a change reaches; the full suite runs on the schedule only.
name: regression-pr
on:
  pull_request:
  merge_group:
    types: [checks_requested]
permissions:
  contents: read
concurrency:
  group: regression-pr-${{ github.ref }}
  cancel-in-progress: true
jobs:
  shard:
    if: github.event_name != 'merge_group'
    runs-on: ubuntu-latest
    timeout-minutes: 20
    strategy:
      fail-fast: false
      matrix:
        shard: [0, 1, 2, 3, 4, 5, 6, 7, tree]
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          persist-credentials: false
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - uses: actions/cache/restore@v4
        with:
          path: ${{ runner.temp }}/t.tsv
          key: row-times-${{ github.sha }}
          restore-keys: row-times-
      - run: |
          git diff --name-only origin/@BASE@...HEAD | grep -qvE '[.]md$|^[.]loop/(goals|kept)/' || { echo "documents and goal records only: no rows to run"; exit 0; }
          R="python3 skills/workflow-regression/scripts/regression.py run @LEVELS@ --reuse --tier goal"
          B=120; git diff --name-only origin/@BASE@...HEAD | grep -qE '^[.]loop/regression(-known)?[.]tsv$' && B=-1  # rows changed: no budget, nothing LEFT
          [ "${{ matrix.shard }}" != tree ] || exec $R --tree --timeout 200
          LOOP_ROW_TIMES=${{ runner.temp }}/t.tsv LOOP_PR_SHARD=${{ matrix.shard }}/8 $R --budget $B --timeout 200
      - if: always()
        uses: actions/upload-artifact@v4
        with:
          name: shard-${{ matrix.shard }}
          path: ${{ runner.temp }}/t.tsv
          if-no-files-found: ignore
  affected:
    needs: shard
    if: always() && github.event_name != 'merge_group'
    runs-on: ubuntu-latest
    timeout-minutes: 8
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          persist-credentials: false
      - run: test ! -f dev/package.py || python3 dev/package.py --static
      - uses: actions/download-artifact@v4
        continue-on-error: true
        with:
          pattern: shard-*
          path: s
      - run: |
          awk '$3 != "SEL"' s/*/t.tsv | sort -k1,1 -k3,3r | awk '!k[$1]++' > all.tsv
          echo "LEFT (row limit or budget), not failed: $(awk '$3 == "LEFT" || $3 == "CUT" {print $1}' all.tsv | paste -sd, -)"
          awk '$3 ~ /^(RAN|LEFT|CUT)$/ {print $1}' s/*/t.tsv | sort > ran.txt
          echo "run twice: $(uniq -d ran.txt | paste -sd, -)"
          for id in $(awk '$3 != ""' s/*/t.tsv | cut -f1 | sort -u | comm -23 - <(uniq ran.txt)); do python3 skills/workflow-regression/scripts/regression.py run "$id" --timeout 200 || bad=1; done
          test -z "$bad"
      - if: needs.shard.result == 'success'
        uses: actions/cache/save@v4
        with:
          path: all.tsv
          key: row-times-${{ github.sha }}
      - run: test "${{ needs.shard.result }}" = success
  small:
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
OURS = "# Written by workflow-regression"


MATRIX_JOB = """
  matrix-smoke:
    if: github.event_name != 'workflow_dispatch' || inputs.target == ''
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Smoke set on Linux
        run: |
          if [ -f dev/toy/matrix-smoke.py ]; then python3 dev/toy/matrix-smoke.py --agent ci; else echo "no dev/toy/matrix-smoke.py in this repo; nothing to prove"; fi
      - name: Keep the matrix record
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: matrix-runs
          path: .loop/matrix-runs.tsv
          if-no-files-found: ignore
"""


def ours(path):
    return os.path.exists(path) and open(path).read().startswith(OURS)


def workflow(root, given, write_main):
    """regression.py workflow: a public repo gets regression.yml and regression-pr.yml (the rows a change reaches on a pull
    request, a fixed smoke in the merge queue); a private or unreadable repo gets nothing."""
    cfg = tiers.config(root)
    where = given or {"mac": "private", "actions": "public"}.get(cfg.get("regression_runs"), "")
    if not where:
        probe = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "workflow-delivery", "scripts", "private.py")
        seen = subprocess.run([sys.executable, probe, "visibility"], cwd=root, capture_output=True, text=True).stdout.strip() if os.path.exists(probe) else ""
        where = seen if seen in ("private", "public") else "unknown"
    base = os.path.join(root, ".github", "workflows")
    if where != "public":
        print("NOT WRITTEN: " + ("this repo is private; its regression runs on the Mac (local schedule)" if where == "private" else
              "the repo's visibility could not be read, so a workflow that could block a private repo is not written. Fix: gh auth login, then run this again"))
        for name in ("regression.yml", "regression-pr.yml"):
            if where == "private" and ours(os.path.join(base, name)):
                print("REMOVABLE: .github/workflows/%s is ours and a private repo's regression runs on the Mac; git rm it when you choose" % name)
        return 0
    code = write_main()
    main_path = os.path.join(base, "regression.yml")
    if ours(main_path) and "  matrix-smoke:" not in open(main_path).read():
        open(main_path, "a").write(MATRIX_JOB)
    path = os.path.join(base, "regression-pr.yml")
    if not os.path.exists(os.path.join(root, "skills", "workflow-regression", "scripts", "regression.py")):
        print("NOT WRITTEN: regression-pr.yml needs skills/workflow-regression/ in this repo (an adopting repo without it keeps the embedded runner)")
    elif os.path.exists(path) and not ours(path):
        sys.exit("REFUSED: %s exists, and this tool didn't write it. Fix: merge by hand." % path)
    else:
        os.makedirs(base, exist_ok=True)
        open(path, "w").write(NARROW.replace("@BASE@", str(cfg.get("base") or "main")).replace("@LEVELS@", str(cfg.get("ci_levels") or "nightly")))
        print("WROTE " + path)
    return code


def main():
    parser = argparse.ArgumentParser(prog="lanes_cli.py")
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ("affected", "deps", "check", "merge-runs"):
        item = sub.add_parser(name)
        item.add_argument("--root")
    sub.choices["affected"].add_argument("--level", default="land", choices=("land", "nightly", "all"))
    sub.choices["affected"].add_argument("paths", nargs="+", metavar="PATH")
    sub.choices["deps"].add_argument("command")
    sub.choices["deps"].add_argument("--why", metavar="PATH")
    sub.choices["check"].add_argument("scripts", nargs="*", metavar="SCRIPT")
    args = parser.parse_args()
    root, cache = top(args.root), {}
    if args.cmd == "merge-runs":
        return merge_runs(root)
    if args.cmd == "affected":
        rows = rows_of(root, args.level)
        ids, notes = affected(root, rows, [relative(root, p) for p in args.paths], cache)
        print("AFFECTED %d of %d rows (%s)" % (len(ids), len(rows), ", ".join(ids)))
        print("\n".join(sorted(set(notes)))) if notes else None
        return 0
    if args.cmd == "deps":
        deps, always = lanes.closure(root, args.command, cache)
        if args.why:
            target = relative(root, args.why)
            parent = cache.get(("chain", args.command), {})
            reached = lanes.hits(target, deps)
            print(chain(parent, target) if reached and target in parent else
                  ("%s (wide mapping)" % target if reached else "NOT REACHED %s" % target))
            return 0
        print("\n".join(sorted(deps)))
        if always:
            print("ALWAYS %s: %s" % (args.command, cache.get(("why", args.command)) or "names no repo path or the "
            "whole repo"))
        return 0
    scripts = [relative(root, s) for s in args.scripts] or sorted(
        {m for r in rows_of(root, "all") for m in TEST.findall(r["command"])})
    problems = check(root, scripts, cache)
    for code, rel, line, what in problems:
        print("%s %s:%d: %s\nfix: %s" % (code, rel, line, what, FIX.get(code, "").format(file=rel)))
    return 1 if problems else 0


def _slots():
    import slots
    return slots


def free_gb():
    """Free memory in GB (LOOP_FREE_GB fakes it); None when unreadable: a lane is then never held."""
    try:
        if os.environ.get("LOOP_FREE_GB"):
            return float(os.environ["LOOP_FREE_GB"])
        if os.name == "nt":
            import ctypes
            class Status(ctypes.Structure):
                _fields_ = [("size", ctypes.c_ulong), ("load", ctypes.c_ulong)] + [(n, ctypes.c_ulonglong) for n in ("tp", "ap", "tpf", "apf", "tv", "av", "ae")]
            held = Status()
            held.size = ctypes.sizeof(held)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(held))
            return held.apf / 2 ** 30
        if sys.platform == "darwin":
            text = subprocess.run(["vm_stat"], capture_output=True, text=True).stdout
            page = int(re.search(r"page size of (\d+)", text).group(1))
            return sum(int(m) for m in re.findall(r"Pages (?:free|inactive|speculative):\s+(\d+)", text)) * page / 2 ** 30
        return int(re.search(r"MemAvailable:\s+(\d+) kB", open("/proc/meminfo").read()).group(1)) / 2 ** 20
    except Exception:
        return None


def wait_memory(root):
    """A lane about to run rows waits while free memory is below min_free_memory_gb (default 3, 0 is off); a running lane is
    never stopped. Waits go to <git common dir>/loop/memory-waits.log; past 4x the lane's limit it exits 6 (EXIT_ENV)."""
    try:
        need = json.load(open(os.path.join(root, ".loop", "config.json"))).get("min_free_memory_gb", 3)
    except (OSError, ValueError, AttributeError):
        need = 3
    need = need if isinstance(need, (int, float)) and not isinstance(need, bool) and need > 0 else 0
    began, told = time.time(), 0.0
    cap = float(os.environ.get("LOOP_MEMORY_WAIT_SECONDS") or 4 * _slots().time_limit(root)[0])
    while need:
        free = free_gb()
        if free is None or free >= need:
            return
        if time.time() - told > 300:
            told = time.time()
            line = "LANE_MEMORY: %.1f GB free, min_free_memory_gb is %g; waiting" % (free, need)
            print(line, flush=True)
            try:
                with open(os.path.join(os.path.abspath(os.path.join(root, (lanes.git(root, "rev-parse", "--git-common-dir") or "").strip())), "loop", "memory-waits.log"), "a") as log:
                    log.write("%s %s\n" % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), line))
            except OSError:
                pass
        if time.time() - began > cap:
            _slots().note("MEMORY_WAIT: waited %ds for memory (%.1f GB free, min_free_memory_gb %g); nothing ran, no try used. Fix: run it again when memory frees" % (time.time() - began, free, need))
            sys.exit(_slots().EXIT_ENV)
        time.sleep(min(_slots().POLL * 5, max(cap / 4, 0.05)))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError) as error:
        if os.environ.get("LANES_DEBUG") == "1":
            raise
        sys.stderr.write("lanes_cli.py: unexpected error: %s (LANES_DEBUG=1 for the trace)\n" % error)
        sys.exit(1)
