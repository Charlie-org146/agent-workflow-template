"""The one way to reach the shared steps.py (skills/ in the repo, shared/ in a pack)."""
import importlib
import os
import sys


def steps():
    """The shared steps.py by name, found in skills/ (repo) or shared/ (pack); a named refusal when it is missing."""
    if "steps" not in sys.modules:
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
