#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-regression/scripts/lanes_cli.py skills/workflow-regression/scripts/regression.py
# reads: skills/workflow-docs/scripts/criteria.py skills/workflow-docs/scripts/docs.py skills/workflow-docs/scripts/render.py
# Proves part 0b: three PRs that each ran a lane (a fragment in .loop/lane-results/) and edit the same feature page merge in any
# order with no conflict, the docs check passes on each head while fragments wait, and after the release's fold and render the
# tree is byte-identical whichever order they merged in and the docs check passes. No model, no network.
import itertools
import os
import subprocess
import sys
import tempfile

HERE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SK = os.path.join(HERE, "skills")
LANES = os.path.join(SK, "workflow-regression", "scripts", "lanes_cli.py")
REG = os.path.join(SK, "workflow-regression", "scripts", "regression.py")
CRI = os.path.join(SK, "workflow-docs", "scripts", "criteria.py")
DOCS = os.path.join(SK, "workflow-docs", "scripts", "docs.py")
failed = []
env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@e.test", GIT_COMMITTER_NAME="t",
           GIT_COMMITTER_EMAIL="t@e.test")
for key in ("GITHUB_SERVER_URL", "GITHUB_REPOSITORY", "GITHUB_RUN_ID", "GITHUB_ACTIONS"):
    env.pop(key, None)


def run(cwd, *cmd, ok=True):
    done = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env)
    if ok and done.returncode:
        sys.exit("SETUP %s: %s" % (" ".join(cmd[:3]), (done.stderr or done.stdout)[-300:]))
    return done


def git(cwd, *args, ok=True):
    return run(cwd, "git", "-c", "core.autocrlf=false", *args, ok=ok)


def check(name, good, why=""):
    print(("PASS: " if good else "FAIL: ") + name + ("" if good else " | " + why))
    if not good:
        failed.append(name)


def stale(out):
    """The Tests-related trouble in a docs check: STALE or TESTS lines (the fixture's other page-format notes are not the point)."""
    return [x for x in out.splitlines() if x.startswith(("STALE", "TESTS"))]


def py(cwd, script, *args, ok=True):
    return run(cwd, sys.executable, script, *args, ok=ok)


def write(root, rel, text):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="\n") as fh:
        fh.write(text)


def fixture(root):
    git(root, "init", "-q", "-b", "main")
    write(root, "calc.py", "def add(a, b):\n    return a + b\n")
    write(root, ".loop/config.json", '{"base": "main", "criteria": true}\n')
    write(root, "docs/wiki/Calc.md",
          "<!-- workflow-docs -->\n# Calc\n\nReview: **Unreviewed**\n\n## Problem\n\n- I can't add two numbers.\n\n## Requirements\n\n"
          "- CAL-1: **Unreviewed** The calculator adds.\n\n## Non-goals\n\n- No other feature.\n- No second feature.\n- No third feature.\n\n"
          "## Success metrics\n\n- The toy run passes.\n\n## Tests\n\n")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "base")
    py(root, DOCS, "add", "Calc", "--paths", "calc.py")
    py(root, REG, "add", "r1", "--level", "land", "--command", "true", "--goal", "CAL-1",
       "--describe", "Given the calculator, when it adds, then it works.")
    py(root, REG, "add", "r2", "--level", "land", "--command", "true", "--goal", "CAL-1",
       "--describe", "Given the calculator, when it adds twice, then it works.")
    py(root, CRI, "render")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "docs and rows")


def fragment(root, slug, day, status):
    write(root, ".loop/lane-results/%s.tsv" % slug,
          "# id\tstatus\tdate\trun\tflaky\nr1\t%s\t%s\t\nr2\tPASS\t2026-01-01\t\n" % (status, day))


def tree(root):
    out = {}
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d != ".git"]
        for name in files:
            full = os.path.join(base, name)
            with open(full, "rb") as fh:
                out[os.path.relpath(full, root).replace("\\", "/")] = fh.read()
    return out


def main():
    with tempfile.TemporaryDirectory() as tmp:
        root = os.path.join(tmp, "repo")
        os.makedirs(root)
        fixture(root)
        edits = {"b1": ("- I can't add two numbers.", "- I can't add two numbers, first."),
                 "b2": ("- No second feature.", "- No second feature, second."), "b3": ("- The toy run passes.", "- The toy run passes, third.")}
        days = {"b1": "2026-02-01", "b2": "2026-02-02", "b3": "2026-02-03"}
        status = {"b1": "PASS", "b2": "FAIL", "b3": "PASS"}
        for name, (old, new) in edits.items():
            git(root, "switch", "-q", "-c", name, "main")
            page = os.path.join(root, "docs/wiki/Calc.md")
            with open(page, newline="") as fh:
                text = fh.read()
            write(root, "docs/wiki/Calc.md", text.replace(old, new))
            fragment(root, name, days[name], status[name])
            git(root, "add", "-A")
            git(root, "commit", "-q", "-m", name)
            head = py(root, DOCS, "check", ok=False)
            check("%s: docs check passes on a head whose lane fragment waits" % name,
                  not stale(head.stdout), head.stdout[-300:])
        trees, conflicts = {}, []
        for order in itertools.permutations(edits):
            git(root, "switch", "-q", "-f", "main")
            git(root, "reset", "-q", "--hard", "main")
            for name in order:
                done = git(root, "merge", "-q", "--no-edit", name, ok=False)
                if done.returncode:
                    conflicts.append("%s after %s" % (name, order))
                    git(root, "merge", "--abort", ok=False)
            hold = py(root, DOCS, "check", ok=False)
            if stale(hold.stdout):
                conflicts.append("check stale before the release in order %s" % (order,))
            py(root, LANES, "fold", "--root", root)
            py(root, CRI, "render")
            trees[order] = tree(root)
            after = py(root, DOCS, "check", ok=False)
            check("after the release step the docs check passes (order %s)" % "-".join(order), not stale(after.stdout),
                  after.stdout[-300:])
            check("no fragment is left after the fold (order %s)" % "-".join(order), not os.path.isdir(os.path.join(root, ".loop", "lane-results"))
                  or not os.listdir(os.path.join(root, ".loop", "lane-results")))
        check("three PRs touching the same page merge in any of six orders with no conflict", not conflicts, "; ".join(conflicts))
        first = next(iter(trees.values()))
        check("after the fold and render the tree is byte-identical whichever order they merged in", all(t == first for t in trees.values()),
              "orders differ")
        runs = first.get(".loop/regression-runs.tsv", b"").decode()
        check("the fold keeps the latest result per row", "r1\tPASS\t2026-02-03" in runs and "r2\tPASS\t2026-01-01" in runs, runs)
        tests = first.get("docs/wiki/Calc.md", b"").decode()
        check("the page's Tests table carries the folded result", "PASS 2026-02-03" in tests, tests[-400:])
    if failed:
        print("\n%d FAILED" % len(failed))
        return 1
    print("\nALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
