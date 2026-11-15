#!/usr/bin/env python3
"""What leaves a Reviewed page fresh without the owner's words (#3867, #3122): a code change that keeps the syntax tree
(comments and docstrings only) stales nothing (same_code), and a page stale only through mapped code, its reviewed text
untouched, is re-stamped at merge with the goal's slug, logged in the reviews log (restamp).

usage: docfresh.py restamp SLUG PAGE...   mark each page kept by SLUG (run in a checkout)
       docfresh.py apply SLUG BRANCH       re-stamp the pages stale on origin/BRANCH and push the commit (merge.py)
       docfresh.py forward BASE           fast-forward this main checkout to origin/BASE, a dirty lane record stashed and put back
       docfresh.py wiki-only OLD NEW      exit 0 when NEW follows OLD by wiki page commits only (merge.py)"""
import ast
import datetime
import json
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import criteria  # noqa: E402
import prd  # noqa: E402

KEPT = re.compile(r" <!-- kept [\w.@-]+ -->$")


def tree(text):
    """The syntax tree of Python text without docstrings, as a string; None when it does not parse."""
    try:
        parsed = ast.parse(text)
    except (SyntaxError, ValueError):
        return None
    for node in ast.walk(parsed):
        body = getattr(node, "body", None)
        if isinstance(body, list) and body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0].value, "value", None), str):
            body[:] = body[1:] or [ast.Pass()]
    return ast.dump(parsed)


def same_code(root, sha, files):
    """True when every changed file is Python and reads as the same syntax tree before and after the commit sha."""
    show = lambda ref, rel: subprocess.run(["git", "-C", root, "show", "%s:%s" % (ref, rel)], capture_output=True, text=True)  # noqa: E731
    for rel in files:
        old, new = show(sha + "^", rel), show(sha, rel)
        if not rel.endswith(".py") or old.returncode or new.returncode or tree(old.stdout) is None or tree(old.stdout) != tree(new.stdout):
            return False
    return bool(files)


def restamp(root, pages, slug):
    """Mark each page in pages kept by slug when its reviewed text still matches its lock (P R N M U); a page whose wording
    moved stays LOCKED. Returns the pages marked; one reviews-log row names them and the slug."""
    rule, done = criteria.rules(), []
    for page in pages:
        rel = "%s/%s.md" % (criteria.folder_of(root), page)
        try:
            with open(os.path.join(root, rel), newline="") as handle:
                text = handle.read()
        except OSError:
            continue
        line, why = prd.review_of(text, rule)
        match = prd.REVIEW.match(KEPT.sub("", line or ""))
        parts = criteria.sections(text)
        now = prd.prints(parts, rule)
        moved = [k for k, g in zip(prd.KEYS, match.group(3, 4, 5, 6)) if now[k] != g] if match and match.group(3) else ["?"]
        if why or not match or moved not in ([], ["R"]) or (moved and not __import__("audit").owned(root, rel, dict(parts), rule)):
            continue  # a moved R is another goal's owner-reviewed line, which relock accepts (DOC-2)
        stamp = "Review: **Reviewed %s** <!-- prd %s -->" % (match.group(2), " ".join("%s=%s" % (k, now[k]) for k in prd.KEYS))
        with open(os.path.join(root, rel), "w", newline="") as handle:
            handle.write(prd.set_review(text, stamp + " <!-- kept %s@%s -->" % (slug, subprocess.run(["git", "-C", root, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip() or "0")))
        done.append(page)
    if done:
        log = os.path.join(os.path.abspath(criteria.git("rev-parse", "--git-common-dir")), "loop")
        os.makedirs(log, exist_ok=True)
        with open(os.path.join(log, "reviews.tsv"), "a") as handle:
            handle.write("%s\trestamp\t%s\t%s: stale only through mapped code, reviewed text unchanged\n" % (
                datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), ",".join(done), slug))
    return done



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
        git("checkout", "-q", "--", RUNS)  # a conflict leaves no markers behind
        print("NOTE: %s could not be put back; it is kept in stash entry %s" % (RUNS, sha[:12]))
        return moved
    if sha:
        names = git("stash", "list", "--format=%gd %gs").stdout.splitlines()
        drop = next((l.split()[0] for l in names if l.endswith(tag)), "")
        drop and git("stash", "drop", "-q", drop)
    return moved


def apply(slug, branch):
    """Re-stamp the pages docs.py check --own calls stale on the goal's branch, in a temporary worktree: restamp marks a page
    only while its reviewed text still holds, so a wording change stays refused. The pushed commit moves the head by wiki
    pages only, which merge.py accepts."""
    top = run(["git", "rev-parse", "--show-toplevel"]).stdout.strip()
    tree = tempfile.mkdtemp(prefix="restamp-")
    if run(["git", "fetch", "-q", "origin", branch], top).returncode or run(["git", "worktree", "add", "-q", "--detach", tree, "origin/" + branch], top).returncode:
        return 0
    try:
        with open(os.path.join(tree, ".loop", "config.json")) as handle:
            config = json.load(handle)
        base, folder = config.get("base") or "main", config.get("wiki_dir") or "docs/wiki"
        docs = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs.py")
        pages = sorted({l.split()[1].rstrip(":") for l in run([sys.executable, docs, "check", "--own", "origin/" + base], tree).stdout.splitlines() if l.startswith("STALE ")})
        said = pages and run([sys.executable, os.path.abspath(__file__), "restamp", slug] + pages, tree).stdout.strip()
        if said and run(["git", "add", "-A", "--", folder], tree).returncode == 0:
            run(["git", "commit", "-q", "-m", "Wiki: re-stamp pages for %s" % slug], tree)
            pushed = run(["git", "push", "-q", "origin", "HEAD:refs/heads/" + branch], tree)
            print(said if not pushed.returncode else "NOTE: the re-stamp of %s could not be pushed: %s" % (", ".join(pages), pushed.stderr.strip()[-120:]))
    except (OSError, ValueError):
        pass
    finally:
        run(["git", "worktree", "remove", "--force", tree], top)
    return 0


if __name__ == "__main__":
    if sys.argv[1:2] == ["restamp"] and len(sys.argv) > 3:
        print("".join("RESTAMPED %s\n" % page for page in restamp(os.getcwd(), sys.argv[3:], sys.argv[2])), end="")
    elif sys.argv[1:2] == ["apply"] and len(sys.argv) == 4:
        sys.exit(apply(sys.argv[2], sys.argv[3]))
    elif sys.argv[1:2] == ["forward"] and len(sys.argv) == 3:
        sys.exit(0 if forward(os.getcwd(), sys.argv[2]) else 1)
    elif sys.argv[1:2] == ["wiki-only"] and len(sys.argv) == 4:
        sys.exit(0 if wiki_only(os.getcwd(), None, sys.argv[2], sys.argv[3]) else 1)
    else:
        print(__doc__)
        sys.exit(0 if sys.argv[1:2] in (["-h"], ["--help"]) else "usage: see docfresh.py -h")
