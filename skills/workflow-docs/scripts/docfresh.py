#!/usr/bin/env python3
"""What leaves a Reviewed page fresh without the owner's words (#3867, #3122): a code change that keeps the syntax tree
(comments and docstrings only) stales nothing (same_code), and a page stale only through mapped code, its reviewed text
untouched, is re-stamped at merge with the goal's slug, logged in the reviews log (restamp)."""
import ast
import datetime
import os
import re
import subprocess

import criteria
import prd

KEPT = re.compile(r" <!-- kept [\w.-]+ -->$")


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
        now = prd.prints(criteria.sections(text), rule)
        if why or not match or not match.group(3) or [k for k, g in zip(prd.KEYS, match.group(3, 4, 5, 6)) if now[k] != g]:
            continue
        with open(os.path.join(root, rel), "w", newline="") as handle:
            handle.write(prd.set_review(text, KEPT.sub("", line) + " <!-- kept %s -->" % slug))
        done.append(page)
    if done:
        log = os.path.join(os.path.abspath(criteria.git("rev-parse", "--git-common-dir")), "loop")
        os.makedirs(log, exist_ok=True)
        with open(os.path.join(log, "reviews.tsv"), "a") as handle:
            handle.write("%s\trestamp\t%s\t%s: stale only through mapped code, reviewed text unchanged\n" % (
                datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), ",".join(done), slug))
    return done


if __name__ == "__main__":
    import sys
    if sys.argv[1:2] == ["restamp"] and len(sys.argv) > 3:
        print("".join("RESTAMPED %s\n" % page for page in restamp(os.getcwd(), sys.argv[3:], sys.argv[2])), end="")
    else:
        sys.exit("usage: docfresh.py restamp SLUG PAGE...")
