"""What a PR shard writes for a selected row (DEL-26.4): RAN only when the row finished on this shard."""


def state(old, key, cut, todo, results):
    """The times-file status of a selected row: LEFT stays, CUT when the budget ran out, SEL on another shard's rows, SKIP when
    the row could not run here (never counted as run), else RAN."""
    if old == "LEFT":
        return old
    if key in cut:
        return "CUT"
    if key not in todo:
        return "SEL"
    return "SKIP" if any(r["id"] == key and r["state"] == "SKIPPED" for r in results) else "RAN"
