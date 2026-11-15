#!/usr/bin/env python3
"""The merge's own moves: wiki_only (a pull request head that moved only by wiki page commits may still merge), apply (a
Reviewed page stale only through mapped code is re-stamped on the goal's branch before the merge, #3867) and forward (the
main checkout is fast-forwarded to the base by merge.py itself, a dirty lane record stashed and put back)."""
import atexit
import json
import os
import subprocess
import sys
import tempfile
import time

FRESH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "workflow-docs", "scripts", "docfresh.py")


def run(args, cwd=None):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)


def wiki_only(top, cfg, old, new):
    """True when NEW descends from OLD (the head the pr lane passed) and every commit between only adds or edits .md pages
    in the base branch's wiki folder (wiki_dir from origin/<base>'s config: the branch can't widen it), no SKILL.md."""
    if run(["git", "merge-base", "--is-ancestor", old, new], cwd=top).returncode:
        return False
    head = run(["git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"], cwd=top).stdout.strip()
    shown = run(["git", "show", "%s:.loop/config.json" % (head or "origin/main")], cwd=top)
    try:
        folder = (json.loads(shown.stdout).get("wiki_dir") if shown.returncode == 0 else None) or "docs/wiki"
    except (ValueError, AttributeError):
        folder = "docs/wiki"
    done = run(["git", "diff", "--raw", "--no-renames", old, new], cwd=top)  # a move shows its source
    rows = [(line.split("\t")[0].split(), line.split("\t")[1:]) for line in done.stdout.split("\n") if line]
    return not done.returncode and bool(rows) and all(
        len(m) == 5 and len(p) == 1 and m[4] in ("A", "M") and m[1] != "120000"  # no symlink
        and p[0].startswith(str(folder).rstrip("/") + "/") and p[0].endswith(".md") and os.path.basename(p[0]) != "SKILL.md"
        for m, p in rows)


def apply(top, cfg, state, slug, wiki):
    """Re-stamp each page wiki.pending calls stale, on the goal's branch, in a temporary worktree: docfresh marks a page
    only while its reviewed text still holds, so a wording change stays refused. A pushed commit moves the head by wiki
    pages only, which merge.py already accepts."""
    branch = state.get("branch")
    if not branch or not wiki.top_of():
        return
    stale = wiki.pending(top, cfg, head="origin/" + branch)
    pages = sorted({l.split()[1].rstrip(":") for l in stale if l.startswith("REWRITE ") and ": STALE " in l})
    tree = tempfile.mkdtemp(prefix="restamp-")
    if not pages or run(["git", "worktree", "add", "-q", "--detach", tree, "origin/" + branch], top).returncode:
        return
    try:
        said = run([sys.executable, FRESH, "restamp", slug] + pages, tree).stdout.strip()
        folder = cfg.get("wiki_dir") or "docs/wiki"
        if said and run(["git", "add", "--", folder], tree).returncode == 0:
            run(["git", "commit", "-q", "-m", "Wiki: re-stamp pages for %s" % slug], tree)
            pushed = run(["git", "push", "-q", "origin", "HEAD:refs/heads/" + branch], tree)
            print(said if not pushed.returncode else "NOTE: the re-stamp of %s could not be pushed: %s" % (", ".join(pages), pushed.stderr.strip()[-120:]))
    finally:
        run(["git", "worktree", "remove", "--force", tree], top)


RUNS = ".loop/regression-runs.tsv"


def forward(main, base):
    """Fast-forward the checkout MAIN to origin/BASE and return True. The only local change allowed is the lane's own
    record RUNS, stashed under a tag and applied back by its sha; a diverged checkout or any other change returns False."""
    git = lambda *a: run(["git", "-C", main] + list(a))  # noqa: E731
    dirty = [l[3:].strip('"') for l in git("status", "--porcelain", "--untracked-files=no").stdout.splitlines()]
    if set(dirty) - {RUNS} or git("merge-base", "--is-ancestor", "HEAD", "origin/" + base).returncode:
        return False
    tag = "merge-forward-%d" % os.getpid()
    sha = ""
    if dirty:
        git("stash", "push", "-m", tag, "--", RUNS)
        sha = git("stash", "list", "--format=%H %gs").stdout
        sha = next((l.split()[0] for l in sha.splitlines() if l.endswith(tag)), "")
        if not sha:
            return False
    moved = git("merge", "--ff-only", "-q", "origin/" + base).returncode == 0
    if sha and git("stash", "apply", sha).returncode:
        print("NOTE: %s could not be put back; it is kept in stash entry %s" % (RUNS, sha[:12]))
        return moved
    if sha:
        names = git("stash", "list", "--format=%gd %gs").stdout.splitlines()
        drop = next((l.split()[0] for l in names if l.endswith(tag)), "")
        drop and git("stash", "drop", "-q", drop)
    return moved


def wait(pods, common, slug):
    """A goal whose pr lane started before this one's holds the merge slot until it merges or fails: wait for it here (this
    goal's own slot stays fresh meanwhile), and give this goal's slot back when merge.py ends."""
    runs = os.path.join(os.path.abspath(common), "loop", "runs")
    atexit.register(lambda: pods.pr_queue("free", runs, slug))
    told = ""
    while ahead := pods.pr_queue("before", runs, slug):
        told == ahead or print("WAITING: %s's pr lane started first and holds the merge slot; waiting for it to merge or fail" % ahead)
        told = ahead
        pods.pr_queue("hold", runs, slug)
        time.sleep(float(os.environ.get("LOOP_SLOT_POLL") or 20))
