"""What a PR shard writes for a selected row (DEL-26.4): RAN only when the row finished on this shard.

.loop/regression-limits.tsv (`id TAB limit TAB reason`) holds the owner's per-row exceptions: a number is that row's own row limit in
seconds; the word `nightly` keeps a nightly row out of the PR shards (it still runs in the nightly run). A row not on it keeps the
run's own limit. Whole-tree rows run in the tree job only (TD504)."""
import os


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


def off_pr(root):
    return {k for k, v in limits(root).items() if v == "nightly"}


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
