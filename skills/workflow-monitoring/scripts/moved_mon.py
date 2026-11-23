"""The one way to reach the shared steps.py (skills/ in the repo, shared/ in a pack)."""
import importlib
import os
import re
import sys


def steps():
    """The shared steps.py by name, found in skills/ (repo) or shared/ (pack); a named refusal when it is missing."""
    if "steps" not in sys.modules:
        sys.dont_write_bytecode = True  # the one shared file sits where a cache folder would break the package check
        here = os.path.dirname(os.path.abspath(__file__))
        for path in (os.path.join(here, "..", ".."), os.path.join(here, "..", "..", "..", "shared")):
            if os.path.exists(os.path.join(path, "steps.py")):
                sys.path.insert(0, os.path.normpath(path))
                break
    try:
        return importlib.import_module("steps")
    except ImportError:
        sys.exit("REFUSED: steps.py is missing. Fix: reinstall the workflow package (SC_MISSING).")


def cmd_owner_words(args):
    import auto
    import proctree
    ids = [item.strip() for item in args.ids.split(",") if item.strip()]
    if os.environ.get("LOOP_ROLE") == "worker":
        sys.exit("REFUSED: only the operation session records the owner's words; a worker never does. Nothing was written.")
    if not args.text.strip() or not ids:
        sys.exit("REFUSED: give the owner's exact message and --ids (requirement IDs or page names it covers). Nothing was written.")
    import layers
    ok, why = layers.relay(args.via, args.text)
    if not ok:
        sys.exit("REFUSED: %s. Nothing was written." % why)
    if args.delegated:
        proctree.require_operation(".", "a delegated approval")
    count = auto.add_owner_words(args, ids)
    import unattended; unattended.reset()
    print("OWNER-WORDS o%d covers %s" % (count, ",".join(ids)))
    return 0


def shown(run, old):
    """(DEL-19 step name, its place in the list, the list's length) for a run record: the step the clock follows, else the old label."""
    one = steps()
    label = one.eff(run)
    name = one.name_of(label if label in one.STEPS or label in one.LEGACY else old)  # an off-list label keeps the last known step
    return name, (one.STEPS.index(name) + 1 if name in one.STEPS else 0), len(one.STEPS)


def stall_lines(runs, at, root=None, held=()):
    """The Issues lines for stalled goals."""
    import board_model as bm
    out = []
    for run in runs:
        found = bm.stalled(run, runs, at, root, held)
        if found:
            out += ["- %s is stalled: %s has run %s (estimate %s)" % (run["slug"], steps().name_of(found[0]), bm.span(found[1]), bm.span(found[2])),
                    "    fix: look at its worker session; stop and resume the goal if it is stuck"]
    return out


def depth_of(run, setting):
    """Each recorded step's depth, in flow order, and the current review_depth setting."""
    from board_log import FLOW
    one, got, by = steps(), run.get("depth") if isinstance(run.get("depth"), dict) else {}, {}
    for step in FLOW:
        if step in got:
            by.setdefault(one.name_of(step), [])
            got[step] in by[one.name_of(step)] or by[one.name_of(step)].append(got[step])
    done = ", ".join("%s %s" % (name, "/".join(by[name])) for name in one.STEPS if name in by)
    return "%s (setting %s)" % (done or "none recorded yet", setting)


def started(run):
    from board_log import stamp
    for entry in run.get("log") or []:
        found = stamp(str(entry).split(" ", 1)[0])
        if found:
            return found
    return stamp(run.get("updated"))


def chain(items):
    """(seconds, path, cycles): the longest chain of what is left, the goals on it, and the goals where a cycle was cut."""
    by, memo, cut = {node["slug"]: node for node in items}, {}, []

    def walk(slug, stack):
        if slug in memo:
            return memo[slug]
        if slug in stack:
            cut.append(slug)
            return 0, []
        node = by[slug]
        best = max([walk(dep, stack + (slug,)) for dep in node["depends"] if dep in by] + [(0, [])], key=lambda found: found[0])
        memo[slug] = (best[0] + (node["left"] or 0), best[1] + [slug])
        return memo[slug]

    found = max([walk(node["slug"], ()) for node in items] + [(0, [])], key=lambda found: found[0])
    return found[0], found[1], sorted(set(cut))


def over_budget(states):
    """monitor.py's, moved whole: (slug, line) for each step or test run that reached its time budget, with what it left (the run file's budget_hits)."""
    return [(state["slug"], "%s %s hit its %s-minute budget; left: %s" % (
        steps().name_of(hit.get("step")), {"step": "step", "prep": "preparation"}.get(hit.get("kind"), "tests"), hit.get("minutes"), hit.get("left")))
        for state in states for hit in state.get("budget_hits") or [] if isinstance(hit, dict)]


def parse_reply(text):
    """layers.py's, moved whole: the A, I and R lists of a red-team reply; exactly one R line."""
    lists = {"A": [], "I": [], "R": []}
    for line in str(text or "").splitlines():
        found = re.match(r"^\W*([AIR])\s*[:.)]\s*(\S.*)$", line)
        if found:
            lists[found.group(1)].append(found.group(2).strip())
    if len(lists["R"]) != 1:
        sys.exit("REFUSED: the reply has %d R: lines, and a red-team pass names exactly one biggest risk. Fix: send one `R: <risk>` line; nothing was recorded." % len(lists["R"]))
    return lists
