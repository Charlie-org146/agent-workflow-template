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


def app_only(cfg, state, slug):
    """With `workers: app`, the refusal for a headless step on a goal no app session is bound to (#4184); '' otherwise."""
    if cfg.get("workers") == "app" and state.get("worker") != "session":
        return "REFUSED: workers is app and %s has no bound app session, so no headless agent starts. Fix: sessions.py bind %s SESSION (NO_SESSION)" % (slug, slug)
    return ""


def lane_checks(top, contexts):
    """The required checks whose job the lane really performs (#3840): a job of .github/workflows whose steps only run regression.py.
    Each other check is printed as BLOCKS and gets no status."""
    import glob
    import os
    import re
    jobs = {}
    for path in glob.glob(os.path.join(top, ".github", "workflows", "*.y*ml")):
        with open(path, encoding="utf-8", errors="replace") as handle:
            for job, body in re.findall(r"^  ([\w-]+):\n((?:    .*\n|\n)*)", handle.read() + "\n", re.M):
                name = re.search(r"^    name:\s*(.+?)\s*$", body, re.M)
                runs = re.findall(r"^\s*-?\s*run:\s*(.+)$", body, re.M)
                held = bool(runs) and all("regression.py" in line for line in runs) and not re.search(r"uses:\s*(?!actions/(?:checkout|setup-))", body)
                jobs.update({job: held, name[1].strip("'\"") if name else job: held})
    ours = [name for name in contexts if jobs.get(name)]
    for name in set(contexts) - set(ours):
        print("BLOCKS: %s is a check the lane does not run, so it posts no status for it; its own job must report it (BLOCKS)" % name)
    return ours
