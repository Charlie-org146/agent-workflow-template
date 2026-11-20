#!/usr/bin/env python3
"""Ask lanes.py which regression rows a change can affect, what a row depends on, and whether test headers hold.

usage: lanes_cli.py affected [--root DIR] [--level land|nightly|all] PATH...
       lanes_cli.py deps [--root DIR] COMMAND [--why PATH]
       lanes_cli.py check [--root DIR] [SCRIPT...]
       lanes_cli.py merge-runs [--root DIR]
       lanes_cli.py fold [--root DIR]

affected: `AFFECTED n of m rows (ids)`, `ALWAYS <id>: <reason>`, `UNMAPPED` or `DELETED <path>`. deps: a command's dependency paths.
check: every `# reads:` problem, `<CODE> <file>:<line>: <what>` and a `fix:` line each; exit 1 on problems.
merge-runs: the lane record's PASS and FAIL rows (flaky flag too) into the fragment .loop/lane-results/<slug>.tsv (DX-19).
fold: the release step; every fragment into .loop/regression-runs.tsv (per row the later date, then line, wins), then deleted.
Usage errors exit 2; LANES_DEBUG=1 shows a trace. The root is the git top level unless --root is given.
"""
import argparse
import datetime
import glob
import json
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tiers
import lanes  # noqa: E402
import narrow  # noqa: E402

os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")

FIX = {
    "LANES-DECL-NONE": "add '# reads: <the skill files it runs>' to the comment block at the top of {file}",
    "LANES-DECL-PLACE": "move the # reads: line into the comment block at the top of {file}",
    "LANES-DECL-PATTERN": "declare each file, or the skill folder the script globs (e.g. skills/x/scripts/)",
    "LANES-DECL-ESCAPE": "declare repo-relative paths only",
    "LANES-DECL-MISSING": "fix the path or remove it from # reads: in {file}",
    "LANES-DECL-FOLDER-UNBACKED": "declare the files {file} runs instead of the folder",
    "LANES-DECL-GLOB": "declare the globbed folder itself in {file}'s # reads: line (a new file there must rerun it)",
    "LANES-DECL-FOLDER": "add the files {file} runs from that folder to its # reads: line",
    "LANES-DECL-TREE": "add skills/ to the # reads: line of {file} (it stays wide: it reads every skill)",
}
TEST = re.compile(r"(?<![\w./-])(dev/toy/test-[\w-]+\.sh)")


def usage(message):
    sys.stderr.write("lanes_cli.py: %s\n" % message)
    sys.exit(2)


def top(given):
    if given:
        return os.path.abspath(given)
    done = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if done.returncode:
        usage("not inside a git repo; run from the repo or pass --root DIR")
    return done.stdout.strip()


def rows_of(root, level):
    path = os.path.join(root, ".loop", "regression.tsv")
    if not os.path.isfile(path):
        usage("no .loop/regression.tsv under %s; run from the repo or pass --root" % root)
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
    base = here if (here + "/").startswith(os.path.realpath(root) + "/") else root
    full = os.path.realpath(os.path.join(base, path))
    rel = os.path.relpath(full, os.path.realpath(root))
    if rel.startswith(".."):
        usage("path outside the repo: %s" % path)
    return rel


def picked(root, rows, path, cache):
    return {r["id"] for r in rows if lanes.names_any(root, r["command"], [path], cache)
            or lanes.hits(lanes.RUNNER, lanes.closure(root, r["command"], cache)[0])}


def table_changed(root, name):
    base = tiers.config(root).get("base") or "main"
    ats = [at for at in (tiers.merge_base(root, base), *[(lanes.git(root, "rev-parse", "--verify", "-q", ref) or "").strip()
                                                       for ref in ("origin/" + base, base)]) if at][:2]
    if not ats:
        return None
    now, memo = tiers.current(root, name), {}
    return {rid for at in ats for rid in set(now) | set(lanes.table(root, at, name, memo))
            if lanes.table(root, at, name, memo).get(rid) != now.get(rid)}


def affected(root, rows, paths, cache):
    ids, notes, real = set(), [], False
    known = table_changed(root, "regression-known.tsv") if ".loop/regression-known.tsv" in paths else None
    edited = table_changed(root, "regression.tsv") if lanes.TABLE in paths else None
    for row in rows:
        lanes.closure(root, row["command"], cache)
        if cache.get(("why", row["command"])):
            notes.append("ALWAYS %s: %s" % (row["id"], cache["why", row["command"]]))
    for path in [p.replace("\\", "/") for p in paths]:
        if not os.path.exists(os.path.join(root, path)) and not any(
                path == n or (n.endswith("/") and path.startswith(n)) for n in lanes.NO_EFFECT):
            ids |= picked(root, rows, path, cache)
            notes.append("DELETED %s: the rows that name it and the runners" % path)
            real = True
            continue
        if path == ".loop/regression-known.tsv" and known is not None:
            hit = {r["id"] for r in rows} & known
        elif path == lanes.TABLE and edited is not None:
            hit = ({r["id"] for r in rows} & edited) | {r["id"] for r in rows if lanes.names_table(root, r["command"], cache)
                                                        or lanes.closure(root, r["command"], cache)[1]}
        elif path in (lanes.TABLE, ".loop/regression-known.tsv"):
            hit = {r["id"] for r in rows if lanes.reads_table(root, r["command"], cache)}
        else:
            hit = {r["id"] for r in rows if lanes.touches(root, r["command"], path, cache)}
        no_effect = path in (lanes.TABLE, ".loop/regression-known.tsv") or any(
            path == n or (n.endswith("/") and path.startswith(n)) for n in lanes.NO_EFFECT)
        if not hit and not no_effect and not any(lanes.hits(path, lanes.closure(root, r["command"], cache)[0])
                                                 for r in rows):
            ids |= picked(root, rows, path, cache)
            notes.append("UNMAPPED %s: the rows that name it and the runners; no row reads it (add it to a script's "
                         "# reads: if one should)" % path)
            real = real or not no_effect
            continue
        ids, real = ids | hit, real or not no_effect
    if real:
        ids |= {r["id"] for r in rows if lanes.closure(root, r["command"], cache)[1]}
    return sorted(ids), notes


def check(root, scripts, cache):
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


LANE = os.path.join(".loop", "lane-results")


def _read(path):
    try:
        with open(path) as fh:
            return {r[0]: r for r in (x.split("\t") for x in fh.read().splitlines() if x[:1] != "#" and x.count("\t") > 2)}
    except OSError:
        return {}


def _put(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="\n") as fh:
        fh.write("# id\tstatus\tdate\trun\tflaky\n" + "".join("\t".join(rows[k]) + "\n" for k in sorted(rows)))


def merge_runs(root):
    """The lane record's PASS and FAIL rows (and any flaky flag, tiers.py flaky_apply) into .loop/lane-results/<slug>.tsv."""
    import runs
    record, _ = lanes.load(lanes.record_path(root), root.replace(chr(92), "/"))
    git = lambda *a: subprocess.run(["git", *a], cwd=root, capture_output=True, text=True).stdout.strip()
    name = git("rev-parse", "--abbrev-ref", "HEAD")
    name = git("rev-parse", "--short", "HEAD") if name in ("", "HEAD") else name.replace("loop/", "", 1)
    path, old = os.path.join(root, LANE, re.sub(r"[^\w.-]", "-", name) + ".tsv"), _read(os.path.join(root, ".loop", "regression-runs.tsv"))
    mine, day = _read(path), datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    for key, value in sorted(((record or {}).get("rows") or {}).items()):
        if value.get("status") in ("PASS", "FAIL"):
            flag = str(value["flaky"] if "flaky" in value else (old.get(key, []) + [""] * 5)[4])[:12]
            mine[key] = [key, value["status"], day, runs.where()] + [flag] * bool(flag)
    if mine:
        _put(path, mine)
    return 0


def fold(root):
    """The release step: fold every fragment into regression-runs.tsv (per row the later date, then line, wins) and delete it."""
    files, path = sorted(glob.glob(os.path.join(root, LANE, "*.tsv"))), os.path.join(root, ".loop", "regression-runs.tsv")
    best = _read(path)
    for name in files:
        for key, row in _read(name).items():
            best[key] = max(best.get(key, row), row, key=lambda r: (r[2], r))
        os.remove(name)
    if files:
        _put(path, best)
    return 0


NARROW = """# Written by workflow-regression (regression.py workflow). The rows a change reaches; the full suite runs on the schedule only.
name: regression-pr
on:
  pull_request:
  merge_group:
    types: [checks_requested]
  push:
    branches-ignore:
      - "@BASE@"
permissions:
  contents: read
concurrency:
  group: regression-pr-${{ github.ref }}
  cancel-in-progress: true
jobs:
  affected:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          persist-credentials: false
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python3 skills/workflow-regression/scripts/regression.py run @LEVELS@ --reuse --tier goal --timeout 900
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


def workflow(root, given, write_main):
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
            if where == "private" and os.path.exists(os.path.join(base, name)) and open(os.path.join(base, name)).read().startswith(OURS):
                print("REMOVABLE: .github/workflows/%s is ours and a private repo's regression runs on the Mac; git rm it when you choose" % name)
        return 0
    code = write_main()
    main_path = os.path.join(base, "regression.yml")
    if os.path.exists(main_path) and open(main_path).read().startswith(OURS) and "  matrix-smoke:" not in open(main_path).read():
        open(main_path, "a").write(MATRIX_JOB)
    path = os.path.join(base, "regression-pr.yml")
    if not os.path.exists(os.path.join(root, "skills", "workflow-regression", "scripts", "regression.py")):
        print("NOT WRITTEN: regression-pr.yml needs skills/workflow-regression/ in this repo (an adopting repo without it keeps the embedded runner)")
    elif os.path.exists(path) and not open(path).read().startswith(OURS):
        sys.exit("REFUSED: %s exists, and this tool didn't write it. Fix: merge by hand." % path)
    else:
        os.makedirs(base, exist_ok=True)
        open(path, "w").write(NARROW.replace("@BASE@", str(cfg.get("base") or "main")).replace("@LEVELS@", str(cfg.get("ci_levels") or "nightly")))
        print("WROTE " + path)
    return code


def main():
    parser = argparse.ArgumentParser(prog="lanes_cli.py")
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ("affected", "deps", "check", "merge-runs", "fold"):
        item = sub.add_parser(name)
        item.add_argument("--root")
    sub.choices["affected"].add_argument("--level", default="land", choices=("land", "nightly", "all"))
    sub.choices["affected"].add_argument("paths", nargs="+", metavar="PATH")
    sub.choices["deps"].add_argument("command")
    sub.choices["deps"].add_argument("--why", metavar="PATH")
    sub.choices["check"].add_argument("scripts", nargs="*", metavar="SCRIPT")
    args = parser.parse_args()
    root, cache = top(args.root), {}
    if args.cmd in ("merge-runs", "fold"):
        return (merge_runs if args.cmd == "merge-runs" else fold)(root)
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
            line = "LANE_MEMORY: %.1f GB free, min_free_memory_gb is %g; this lane waits and starts when memory frees (a lane already running is not stopped)" % (free, need)
            print(line, flush=True)
            try:
                done = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=root, capture_output=True, text=True)
                with open(os.path.join(os.path.abspath(os.path.join(root, done.stdout.strip())), "loop", "memory-waits.log"), "a") as log:
                    log.write("%s %s\n" % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), line))
            except OSError:
                pass
        if time.time() - began > cap:
            _slots().note("MEMORY_WAIT: waited %ds for memory (%.1f GB free, min_free_memory_gb %g); nothing ran, no try used. Fix: run the same command again when memory frees" % (time.time() - began, free, need))
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
