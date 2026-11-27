"""What a PR shard writes for a selected row (DEL-26.4): RAN only when the row finished on this shard.

.loop/regression-limits.tsv (`id TAB limit TAB reason`) holds the owner's per-row exceptions: a number is that row's own row limit in
seconds; the word `nightly` keeps a nightly row out of the PR shards (it still runs in the nightly run). A row not on it keeps the
run's own limit. Whole-tree rows run in the tree job only (TD504)."""
import glob
import os
import re
import sys
import time


def limits(root):
    got = {}
    try:
        for line in open(os.path.join(root, ".loop", "regression-limits.tsv")):
            cells = line.rstrip("\n").split("\t")
            if len(cells) == 3 and cells[0][:1] != "#" and (cells[1] == "nightly" or cells[1].isdigit()):
                got[cells[0]] = cells[1]
    except OSError:
        pass
    return got


def limit(root, key, default):
    got = limits(root).get(key, "")
    return int(got) if got.isdigit() else default


SAID = set()  # NOTE lines already printed in this run


def off_pr(root):
    """Rows listed nightly stay off the pull request, except a protected (security or private) one."""
    listed = {k for k, v in limits(root).items() if v == "nightly"}
    for key in sorted(listed & protected(root) - SAID):
        print("NOTE %s: listed nightly in regression-limits.tsv but tagged %s; it runs on L1" % (key, entries(root)[key][1]))
        SAID.add(key)
    return listed - protected(root)


def state(old, key, cut, todo, results):
    """The times-file status of a selected row: LEFT stays, CUT when the budget ran out, SEL on another shard's rows, SKIP when
    the row asked to be skipped and NOTRUN when the runner could not start it (neither counts as run), else RAN."""
    if old == "LEFT":
        return old
    if key in cut:
        return "CUT"
    if key not in todo:
        return "SEL"
    for r in results:
        if r["id"] == key:
            return ("NOTRUN" if r.get("notrun") else "SKIP") if r["state"] == "SKIPPED" else "RAN"
    return "CUT"  # selected here with no result: never counted as run


def tree_timeouts(results):
    """The tree job has no other shard to carry a cut row: a known whole-tree row past its row limit fails the job."""
    for r in results:
        if r["state"] == "KNOWN" and r["rc"] == 124:
            r["state"] = "FAIL"


def split(ids, times, n):
    """n shards of ids: longest time first to the least-loaded shard; no time weighs the median."""
    seen = sorted(times[k] for k in ids if k in times)
    weight, load, shards = {k: times.get(k, seen[len(seen) // 2] if seen else 1) for k in ids}, [0] * n, [[] for _ in range(n)]
    for key in sorted(ids, key=lambda k: (-weight[k], k)):
        j = min(range(n), key=lambda x: (load[x], x))
        shards[j].append(key)
        load[j] += weight[key]
    return shards


def merge_runs(root):
    """The lane record's row results, with any flaky flag (tiers.py), into regression-runs.tsv."""
    import lanes, runs, slots
    record, _ = lanes.load(lanes.record_path(root), root)
    rows = (record or {}).get("rows") or {}
    done = [dict(id=key, state=value.get("status"), **{k: value[k] for k in ("flaky",) if k in value})
            for key, value in sorted(rows.items()) if value.get("status") in ("PASS", "FAIL")]
    if done:
        day = time.strftime("%Y-%m-%d", time.gmtime())
        head = (lanes.git(root, "rev-parse", "HEAD") or "").strip()
        slots.edit(root, "regression-runs.tsv", lambda: runs.write(root, done, day, head))
    return 0


# -- levels at run time (v110-lvl-l1): L1 on the pull request, L0 in a goal lane
def armed(root):
    """The table holds lvl-armed and the pull request workflow is this tool's: the pull request run is L1."""
    try:
        with open(os.path.join(root, ".loop", "regression.tsv"), encoding="utf-8") as table:
            marked = any(line.split("\t")[0] == "lvl-armed" for line in table)
        with open(os.path.join(root, ".github", "workflows", "regression-pr.yml"), encoding="utf-8") as flow:
            return marked and flow.readline().startswith("# Written by workflow-regression")
    except OSError:
        return False


def entries(root):
    """{row id: (level, risk tag)} from the levels record."""
    got = {}
    try:
        with open(os.path.join(root, ".loop", "regression-relevel.tsv"), encoding="utf-8") as record:
            for line in record:
                cells = line.rstrip("\n").split("\t")
                if len(cells) > 3 and cells[0][:1] != "#":
                    got.setdefault(cells[0], (cells[2], cells[3]))
    except OSError:
        pass
    return got


def pick(rows, level, record):
    """The rows a level runs by their recorded stage: L0; L1 is L0 and L1; L2 is every row. A row with no entry is L1."""
    stages = {"L0": ("L0",), "L1": ("L0", "L1"), "L2": ("L0", "L1", "L2")}[level]
    return [row for row in rows if record.get(row["id"], ("L1",))[0] in stages]


def eligible(rows, record):
    """Every security or private row, flagged mandatory: L1 considers it whatever its stage."""
    return [dict(row, mandatory=record[row["id"]][1]) for row in rows
            if record.get(row["id"], ("", ""))[1] in ("security", "private")]


def at_level(rows, level, record):
    """runs.chosen for a level word: pick() in table order, and for L1 only the mandatory rows added and flagged."""
    kept = {row["id"]: row for row in pick(rows, level, record)}
    if level == "L1":
        kept.update((row["id"], row) for row in eligible(rows, record))
    return [kept[row["id"]] for row in rows if row["id"] in kept]


def protected(root):
    """Ids tagged security or private, on an armed table."""
    return {k for k, v in entries(root).items() if v[1] in ("security", "private")} if armed(root) else set()


def all_private(picked, why):
    """A change that reaches no private row runs every private row (a reached one narrows them as any row)."""
    private = [row["id"] for row in picked if row.get("mandatory") == "private"]
    if private and not any(why[key] for key in private):
        why.update((key, "private: the change reaches no private row, so every one runs") for key in private)


def pr_select(changed):
    """"docs" when every changed file is a document or a goal record (the shard's shell test), else "code"."""
    return "code" if any(not re.search(r"[.]md$|^[.]loop/(goals|kept)/", name) for name in changed) else "docs"


def l1_minutes(config):
    """L1's time goal in minutes: 10 when the key is absent; anything but a whole number of at least 1 is refused."""
    value = config.get("l1_minutes", 10)
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError("L1_MINUTES_BAD l1_minutes: %r is not a whole number of at least 1. Fix: set l1_minutes to a whole "
                         "number such as 10 in .loop/config.json" % (value,))
    return value


# -- moved whole from tiers.py (plan lines and run order)
def notes(loose, gone):
    """The advisory UNMAPPED lines (DX-15, DX-18): such a path picks the rows that name it and the runners (REG-7)."""
    return ["UNMAPPED %s: no row declares it. Note: the rows that name it and the runners run; declare it in the "
            "# reads: header of the row that tests it to map it" % p for p in loose] + [
            "UNMAPPED %s: deleted. Note: the rows that name it and the runners run" % p for p in gone]


def rank(because):
    """Run order (#531): new or changed rows, reruns, rows that reach a changed file, then root runners and picks."""
    return 0 if because.startswith("new row") else 1 if because.startswith(("failure", "skipped")) else 3 if because.startswith(
        ("root runner", "names")) else 2


# -- moved whole from runs.py (the time budget)
def minutes(cfg, key, default=None):
    import sys
    from runs import DEFAULT, FLOOR
    default = DEFAULT if default is None else default
    value = cfg.get(key, default)
    if isinstance(value, bool) or not isinstance(value, int) or value < FLOOR:
        sys.exit("REFUSED: %s is %r in .loop/config.json, under the %d-minute floor. Fix: set it to %d or more." % (
            key, value, FLOOR, FLOOR))
    return value


def budget(root):
    import json
    from runs import path_of
    try:
        with open(path_of(root, "config.json")) as handle:
            cfg = json.load(handle)
    except (OSError, ValueError):
        cfg = {}
    return minutes(cfg if isinstance(cfg, dict) else {}, "test_budget_minutes") * 60


def fit(todo, est, limit):
    keep, left, used = [], [], 0.0
    for key in todo:
        if used + est.get(key, 0) <= limit:
            keep.append(key)
            used += est.get(key, 0)
        else:
            left.append(key)
    return keep, left


# -- moved whole from lanes_cli.py
def table_changed(root, name):
    """Ids whose line in .loop/<name> differs from the merge-base or base tip; None if neither."""
    import lanes
    import tiers
    base = tiers.config(root).get("base") or "main"
    ats = [at for at in (tiers.merge_base(root, base), *[(lanes.git(root, "rev-parse", "--verify", "-q", ref) or "").strip()
            for ref in ("origin/" + base, base)]) if at][:2]
    if not ats:
        return None
    now, memo = tiers.current(root, name), {}
    return {rid for at in ats for rid in set(now) | set(lanes.table(root, at, name, memo))
            if lanes.table(root, at, name, memo).get(rid) != now.get(rid)}


# -- security rows that flip (v110-lvl-l1): the row stays FAIL; one issue is filed from the default branch
FLIP = ("FLAKY %s: failed then passed (rerun once in a fresh HOME). Fix: find the first failure in the shard log, then fix "
        "the row or the cause; a flip is a failure until then")
FLIP_HEAD = "FLAKY: failed then passed on rerun (same commit)"
FLIP_BYTES, FLIP_ROWS, WITHHELD = 100000, 20, "[tail withheld: private scan hit; see the job log of the pull request run]"


def passes_again(root, command, cap):
    """The commit when a failed row passes one rerun in a fresh HOME, else "". The first result is kept as it was."""
    import shutil
    import tempfile
    import actions
    import lanes
    home = tempfile.mkdtemp(prefix="loop-rerun-")
    try:
        env = dict(actions.row_env(), HOME=home, TOY_SKIP_FILE=os.path.join(home, "skip"))
        code = lanes.run_row(command, root, env, cap)[0]
    finally:
        shutil.rmtree(home, ignore_errors=True)
    return (lanes.git(root, "rev-parse", "HEAD") or "").strip() if code == 0 else ""


def flaky_write(path, item):
    """Append `id TAB seconds TAB tail` for one flip: the first failure's last 20 lines, each cut to 200, escaped."""
    if not path:
        return
    tail = "\n".join([FLIP_HEAD] + [line[:200] for line in str(item.get("tail") or "").splitlines()[-20:]])
    with open(path, "a", encoding="utf-8") as out:
        out.write("%s\t%s\t%s\n" % (item["id"], item.get("seconds") or 0,
                                    tail.encode("unicode_escape").decode("ascii")))


SECRET = re.compile(r"AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----")


def delivery_scan():
    """The delivery skill's private-name scan, loaded by path (its folder goes on the path for what it imports)."""
    import importlib.util
    folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "workflow-delivery", "scripts")
    sys.path.append(folder)
    spec = importlib.util.spec_from_file_location("private", os.path.join(folder, "private.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def safe_tail(root, tail):
    """The tail for an issue body: withheld on a private or secret-shaped hit; no fence, comment mark or control byte."""
    private = delivery_scan()
    found = private.scan(root, None, texts={"tail": tail})["state"]
    if found not in ("clean", "off", "none") or SECRET.search(tail) or private.HOME_DIR.search(tail):
        return WITHHELD
    tail = "".join(c for c in tail if c == "\n" or c >= " " and c != "\x7f")
    return tail.replace("```", "\'\'\'").replace("<!--", "<!- -")


def flaky_results(root, paths):
    """(items for runs.sync_issues, refusals) from the uploaded flip files, read as data. The root is the default
    branch's checkout: a row it does not tag security, or a malformed or oversize file, is refused."""
    record, rows = entries(root), set()
    with open(os.path.join(root, ".loop", "regression.tsv"), encoding="utf-8") as table:
        rows = {line.split("\t")[0] for line in table}
    items, refused = {}, []
    for path in paths:
        if os.path.getsize(path) > FLIP_BYTES:
            refused.append("%s: over %d bytes" % (os.path.basename(path), FLIP_BYTES))
            continue
        lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
        found, why = [], "more than %d rows" % FLIP_ROWS if len(lines) > FLIP_ROWS else ""
        for line in lines if not why else []:
            cells = line.split("\t")
            if len(cells) != 3 or not re.fullmatch(r"\d+(\.\d+)?", cells[1]):
                why = "a line is not `id, seconds, tail`"
            elif cells[0] not in rows or record.get(cells[0], ("", ""))[1] != "security":
                why = "%r is not a security row of the default branch" % cells[0][:80]
            else:
                try:
                    tail = cells[2].encode("ascii").decode("unicode_escape")
                except (UnicodeError, ValueError):
                    why = "a tail is not escaped text"
                    continue
                found.append({"id": cells[0], "state": "FAIL", "tail": safe_tail(root, tail), "seconds": float(cells[1])})
            if why:
                break
        if why:
            refused.append("%s: %s" % (os.path.basename(path), why))
        else:
            items.update((item["id"], item) for item in found)
    return list(items.values()), refused


def file_flaky(argv):
    """file-flaky DIR [--pr N] [--sha SHA] [--live]: file one issue for each flipped security row in DIR's flip files."""
    import runs
    root = os.getcwd()
    paths = sorted(glob.glob(os.path.join(argv[0], "**", "flaky.tsv"), recursive=True))
    items, refused = flaky_results(root, paths)
    for why in refused:
        print("REFUSED %s; nothing from it is filed" % why)
    pr, sha = (argv[argv.index(flag) + 1] if flag in argv else "" for flag in ("--pr", "--sha"))
    if re.fullmatch(r"\d+", pr) and re.fullmatch(r"[0-9a-f]{40}", sha):
        for item in items:
            item["tail"] = "pull request %s at %s\n%s" % (pr, sha, item["tail"])
    if items:
        runs.sync_issues(items, "--live" in argv, time.strftime("%Y-%m-%d", time.gmtime()))
    print("FLIPS %d rows from %d files, %d files refused" % (len(items), len(paths), len(refused)))
    return 1 if refused else 0


FLAKY_FLOW = """# Written by workflow-regression (regression.py workflow). One issue for each security row that flipped on a pull request.
name: regression-flaky
on:
  workflow_run:
    workflows: [regression-pr]
    types: [completed]
permissions: {}
jobs:
  file:
    permissions:
      contents: read
      actions: read
      issues: write
    if: github.event.workflow_run.event == 'pull_request' && github.event.workflow_run.conclusion == 'failure' && github.event.workflow_run.head_repository.full_name == github.repository
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - id: list
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          n=$(gh api "repos/${{ github.repository }}/actions/runs/${{ github.event.workflow_run.id }}/artifacts?per_page=100" --jq '[.artifacts[] | select(.name | startswith("flaky-"))] | length')
          echo "flaky=$n" >> "$GITHUB_OUTPUT"
      - if: steps.list.outputs.flaky != '0'
        uses: actions/checkout@v4
        with:
          ref: ${{ github.event.repository.default_branch }}
          persist-credentials: false
      - if: steps.list.outputs.flaky != '0'
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - if: steps.list.outputs.flaky != '0'
        uses: actions/download-artifact@v4
        with:
          pattern: flaky-*
          path: ${{ runner.temp }}/flaky
          run-id: ${{ github.event.workflow_run.id }}
          github-token: ${{ github.token }}
      - if: steps.list.outputs.flaky != '0'
        env:
          GH_TOKEN: ${{ github.token }}
          PR: ${{ github.event.workflow_run.pull_requests[0].number }}
          SHA: ${{ github.event.workflow_run.head_sha }}
        run: python3 skills/workflow-regression/scripts/completion.py file-flaky "${{ runner.temp }}/flaky" --pr "$PR" --sha "$SHA" --live
"""


def write_flaky_workflow(base, ours):
    """regression.py workflow's third file, written beside regression-pr.yml; one this tool did not write is kept."""
    path = os.path.join(base, "regression-flaky.yml")
    if os.path.exists(path) and not ours(path):
        sys.exit("REFUSED: %s exists, and this tool didn\'t write it. Fix: merge by hand." % path)
    with open(path, "w") as out:
        out.write(FLAKY_FLOW)
    print("WROTE " + path)


if __name__ == "__main__":
    usage = "usage: completion.py file-flaky DIR [--pr N] [--sha SHA] [--live]"
    if sys.argv[1:2] in (["-h"], ["--help"]):
        print(usage)
        sys.exit(0)
    if sys.argv[1:2] != ["file-flaky"] or len(sys.argv) < 3:
        print(usage, file=sys.stderr)
        sys.exit(2)
    sys.exit(file_flaky(sys.argv[2:]))
