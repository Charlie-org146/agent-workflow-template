"""The one way to reach the shared steps.py (skills/ in the repo, shared/ in a pack)."""
import importlib
import os
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
    """(DEL-19 step name, its place in the eight) for a run record: the step the clock follows, else the old label."""
    one = steps()
    name = one.name_of(one.eff(run) or old)
    return name, (one.STEPS.index(name) + 1 if name in one.STEPS else 0)


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
