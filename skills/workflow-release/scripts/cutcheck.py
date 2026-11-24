#!/usr/bin/env python3
"""CBS-1.4: run before a cut. `cutcheck.py [SLUG ...] [--release V]` prints one list across goals of every check skipped or run
light, with its form. `--require-full CHECK` also runs that check's full-form `run` command (from the base branch's checks
table only: origin/<base>, then <base>, never a goal branch or the worktree) in the worktree of each listed goal that lists
it, prints `PASS`, `FAIL` or `NO COMMAND` (a check whose run is empty or a flow step, not a real test command) per goal and exits 1 on any; an unknown name prints the table's check names and
exits 2. release.py is not edited: the cut test is a procedure (run this, then cut), not a refusal inside the cut."""
import argparse
import glob
import json
import os
import re
import shlex
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "workflow-delivery", "scripts"))
import sizing  # noqa: E402


def git(*args):
    return subprocess.run(["git"] + list(args), capture_output=True, text=True)


def base_table():
    """(table, why) from the base branch's .loop/config.json only; the key missing takes the shipped defaults."""
    base = sizing.base_cfg()[0]
    for ref in ("origin/" + base, base):
        done = git("show", "%s:.loop/config.json" % ref)
        if done.returncode == 0:
            try:
                return sizing.validate(json.loads(done.stdout).get("checks_by_size", sizing.DEFAULTS))
            except (ValueError, AttributeError):
                return None, "the base branch's config is not readable JSON"
    return None, "the base branch's config can't be read"


def states(slugs, release):
    runs = os.path.join(os.path.abspath(git("rev-parse", "--git-common-dir").stdout.strip()), "loop", "runs")
    out = []
    for path in sorted(glob.glob(os.path.join(runs, "*.json"))):
        try:
            found = json.load(open(path))
        except (OSError, ValueError):
            continue
        if isinstance(found, dict) and (found.get("slug") in slugs if slugs else found.get("sized") or found.get("flow")) and (not release or found.get("release") == release):
            out.append(found)
    return out


def main(argv):
    ap = argparse.ArgumentParser(prog="cutcheck.py")
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--release", default="")
    ap.add_argument("--require-full", metavar="CHECK", default="")
    args = ap.parse_args(argv)
    found = states(args.slugs, args.release)
    lines = sizing.skipped(found)
    print("\n".join(lines) if lines else "no check was skipped or run light")
    if not args.require_full:
        return 0
    table, why = base_table()
    if not table:
        print("REFUSED (no try used): %s. Fix: fix the table on the base branch (SIZING_READ_FAILED)" % why)
        return 2
    forms = table["forms"].get(args.require_full)
    if not forms:
        print("unknown check %s; the table's checks: %s" % (args.require_full, ", ".join(sorted(table["forms"]))))
        return 2
    full = max(forms.values(), key=lambda f: f["passes"])
    bad = 0
    for state in found:
        if args.require_full not in ((state.get("sized") or {}).get("checks") or {}):
            continue
        slug, cwd, run = state["slug"], state.get("worktree") or ".", full["run"].replace("SLUG", state["slug"])
        if not run or "flow.py" in run:  # a flow step starts work and returns; only a real test command gives a result
            print("NO COMMAND %s %s" % (args.require_full, slug))
            bad += 1
            continue
        try:
            done = subprocess.run(shlex.split(run), cwd=cwd, capture_output=True, text=True)
        except (OSError, ValueError):
            done = None
        if done is not None and done.returncode == 0 and not re.search(r"^RUNNING", done.stdout, re.M):
            print("PASS %s %s" % (args.require_full, slug))
        else:
            bad += 1
            print("FAIL %s %s" % (args.require_full, slug))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
