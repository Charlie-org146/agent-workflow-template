"""What a PR shard writes for a selected row (DEL-26.4): RAN only when the row finished on this shard.

.loop/regression-limits.tsv (`id TAB limit TAB reason`) holds the owner's per-row exceptions: a number is that row's own row limit in
seconds; the word `nightly` keeps a nightly row out of the PR shards (it still runs in the nightly run). A row not on it keeps the
run's own limit. Whole-tree rows run in the tree job only (TD504)."""
import glob
import os
import re
import statistics
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
    """The table holds lvl-armed and the pull request workflow is this tool's: goal-tier runs follow the levels."""
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


# -- the miss report (v110-lvl-l1): L1 over its time goal says why; the cut gate beside it still fails an unfinished row
def span(path):
    """(start, end or None) of one leg's span.txt; (None, None) when there is none."""
    marks = {}
    try:
        for line in open(path):
            cells = line.split()
            if len(cells) >= 2 and cells[1].isdigit():
                marks[cells[0]] = int(cells[1])
    except OSError:
        pass
    return marks.get("start"), marks.get("end")


def miss(pattern, tree_leg, goal, rows_of):
    """The lines for a run over `goal` minutes, else []. pattern names the numbered legs' times files (its [0-7]),
    tree_leg the tree job's; rows_of reads a times file into [id, seconds, status] rows."""
    legs, lines = {}, []
    for name in sorted(glob.glob(pattern)) + [tree_leg]:
        if not os.path.exists(name):
            continue
        leg = os.path.basename(os.path.dirname(name))
        start, end = span(os.path.join(os.path.dirname(name), "span.txt"))
        if start is None or end is None:
            lines.append("note: leg %s has no end (killed or cancelled); it is left out of the turnaround" % leg)
            continue
        legs[leg] = (start, end, [(r[0], float(r[1])) for r in rows_of([name])[0] if r[2] == "RAN"])
    if not legs:
        return lines
    took = (max(v[1] for v in legs.values()) - min(v[0] for v in legs.values())) / 60.0
    if took <= goal:
        return lines
    ran = sorted((r for v in legs.values() for r in v[2]), key=lambda r: -r[1])
    sums = sorted(sum(s for _, s in v[2]) / 60.0 for v in legs.values())
    top, apart = sum(s for _, s in ran[:3]) / 60.0, (max(v[0] for v in legs.values()) - min(v[0] for v in legs.values())) / 60.0
    longest, middle = sums[-1], statistics.median(sums)
    if longest and top >= longest / 2:
        cause = "the three slowest rows took %.1f of the %.1f minutes" % (top, took)
    elif longest > 2 * middle:
        most = max(legs.values(), key=lambda v: sum(s for _, s in v[2]))
        cause = "one leg ran %d rows past the others" % len(most[2])
    elif apart > took / 4:
        cause = "the legs started %.0f minutes apart: runner queue wait" % apart
    else:
        cause = "no single cause: the rows add up"
    return lines + ["missed: %s" % cause,
                    "slowest rows: %s" % ", ".join("%s %.0fs" % r for r in ran[:3]),
                    "l1_minutes is %d; the legs took %.1f minutes (rows %.1f); queue waits between legs are in it, the wait "
                    "before the first leg is not measured" % (goal, took, sum(sums)),
                    "fix: move the slowest row to L2 with regression.py level <id> --test-level L2, or raise l1_minutes in "
                    ".loop/config.json (owner)"]
