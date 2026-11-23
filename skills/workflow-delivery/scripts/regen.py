#!/usr/bin/env python3
"""DEL-25.4, shipped with the skills. check(): the generated files that are stale, as (name, needs an agent) pairs, writing nothing.
regen(): at goal.py pr they are checked, never rewritten."""
import os
import sys

ENTRY = ("START.md", "CLAUDE.md", "AGENTS.md")
SKILLS = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))


def check(g, slug):
    """The generated files that are stale, as (name, needs an agent) pairs. Writes nothing."""
    py, found = sys.executable, []
    if g.git("ls-files", ".loop/START.md"):
        done = g.run([py, os.path.join(SKILLS, "workflow-docs", "scripts", "entry.py"), "check"])
        found += [(l.split()[1].rstrip(":").replace("\\", "/"), False) for l in done.stdout.splitlines() if l.startswith(("STALE ", "MISSING "))]
    done = g.run([py, os.path.join(SKILLS, "workflow-release", "scripts", "wiki.py"), "prepare", slug])
    found += [(l.split()[1].rstrip(":"), True) for l in done.stdout.splitlines() if l.startswith("REWRITE ")]
    if done.returncode and not found:
        found.append(((done.stdout.strip().splitlines() or ["wiki.py prepare exit %d" % done.returncode])[-1][:120], False))
    return found


def regen(g, slug):
    """goal.py pr: names the stale generated files with the ordered Fix. Writes and commits nothing (DEL-25.4): the files are made before the tested commit."""
    found = check(g, slug)
    fix = ("Fix, in order: 1. python3 skills/workflow-docs/scripts/entry.py write 2. python3 skills/workflow-release/scripts/wiki.py "
           "prepare %s --commit 3. git commit any change 4. re-run the lane at the new head, then goal.py pr" % slug)
    entry = [n for n, agent in found if not agent and n.endswith(ENTRY)]
    if entry:
        raise SystemExit("REFUSED: REGEN_STALE: %s; not rewritten at PR time, the head is unchanged. %s" % (", ".join(entry), fix))
    if found:
        names = ", ".join(n + (" (needs an agent to rewrite)" if agent else "") for n, agent in found)
        print("NOTE: REGEN_STALE: %s; not rewritten here. %s" % (names, fix))
    return g.git("rev-parse", "HEAD")
