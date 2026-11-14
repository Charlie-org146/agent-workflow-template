"""The goal limits that live beside the budget (GRD-2): a session's tokens for a step, and the merge-round cap. goal.py calls both."""


def add_tokens(state, step, given):
    """A session worker's tokens for a step; unknown adds nothing, so the board says tokens unread."""
    if str(given).isdigit():
        held = state.get("tokens") if isinstance(state.get("tokens"), dict) else {}
        old = held.get(step) if isinstance(held.get(step), int) else 0
        state["tokens"] = dict(held, **{step: int(given) + old})


def round_stop(g, state, what):
    """A merge or conflict is one merge-and-rerun round; one past max_merge_rounds (default 3) makes the goal wait."""
    limit, count = g.config().get("max_merge_rounds"), state.get("merge_rounds", 0) + 1
    limit = limit if isinstance(limit, int) and not isinstance(limit, bool) and limit > 0 else 3
    if what not in ("merged", "conflict"):
        return
    over = count > limit
    state["merge_rounds"] = 0 if over else count
    ask = "merge round %d would pass max_merge_rounds (%d). Fix: land it when main is quiet or raise it, then goal.py answer %s (MERGE_ROUNDS)" % (count, limit, state["slug"])
    if over:
        state["status"], state["waiting"] = "waiting", {"ask": ask, "words": ["go on " + state["slug"], "stop " + state["slug"]]}
    g.save(state, ask if over else None)
    if over:
        g.no(ask)
