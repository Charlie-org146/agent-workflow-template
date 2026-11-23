"""What a PR shard writes for a selected row (DEL-26.4): RAN only when the row finished on this shard."""


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
        if r["id"] == key and r["state"] == "SKIPPED":
            return "NOTRUN" if r.get("notrun") else "SKIP"
    return "RAN"
