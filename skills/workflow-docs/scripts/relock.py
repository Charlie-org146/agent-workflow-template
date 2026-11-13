#!/usr/bin/env python3
"""Relock (DOC-2): a reviewed page's lock hashes its whole Requirements section, so another goal's reviewed line moves
it. When every requirement line is owner-reviewed text, `relock.py` re-stamps the lock itself and logs why in reviews.tsv
(auto-relock: all lines owner-reviewed). A line nobody reviewed leaves the page LOCKED, for the owner.

usage: relock.py"""
import os
import sys

import criteria
from prd import KEYS, REVIEW, prints, review_of, set_review


def owned(root, rel, body, rule):
    """True when every requirement line is owner-reviewed text: its seal holds, and it is main's own line or its id is in
    the reviews log; no line main has was dropped. A line nobody reviewed is not owned, so the page stays LOCKED."""
    name = rule["sections"][1]
    shown = criteria.git("show", "origin/main:" + rel, check=False)
    main = [(line, tuple(below), m.group(1)) for line, m, below in criteria.blocks(dict(criteria.sections(shown)).get(name) or []) if m]
    try:
        with open(os.path.join(os.path.abspath(criteria.git("rev-parse", "--git-common-dir")), "loop", "reviews.tsv")) as handle:
            logged = {key for row in handle for item in row.split("\t")[2:3] for key in item.split(",") if row.split("\t")[1:2] == ["review"]}
    except OSError:
        logged = set()
    have = set()
    for line, m, below in criteria.blocks(body.get(name) or []):
        if not m or m.group(2) == "Unreviewed" or m.group(5) != criteria.seal_of(m.group(4), below):
            return False
        if (line, tuple(below), m.group(1)) not in main and m.group(1) not in logged:
            return False
        have.add(m.group(1))
    return {key for _, _, key in main} <= have


def relock(root):
    """Re-stamp each reviewed page whose only change is another goal's owner-reviewed line (R moved, all lines owned)."""
    rule, done = criteria.rules(), []
    for rel in criteria.pages(root):
        with open(os.path.join(root, rel)) as handle:
            text = handle.read()
        line, why = review_of(text, rule)
        match = REVIEW.match(line or "")
        parts = criteria.sections(text)
        if why or not match or not match.group(2):
            continue
        now = prints(parts, rule)
        if [k for k in KEYS[:4] if match.group(3 + KEYS.index(k)) != now[k]] == ["R"] and owned(root, rel, dict(parts), rule):
            fresh = set_review(text, "Review: **Reviewed %s** <!-- prd %s -->" % (match.group(2), " ".join("%s=%s" % (k, now[k]) for k in KEYS)))
            with open(os.path.join(root, rel), "w") as handle:
                handle.write(fresh)
            done.append(os.path.basename(rel)[:-3])
    if done:
        log = os.path.join(os.path.abspath(criteria.git("rev-parse", "--git-common-dir")), "loop")
        os.makedirs(log, exist_ok=True)
        with open(os.path.join(log, "reviews.tsv"), "a") as handle:
            handle.write("%s\trelock\t%s\tauto-relock: all lines owner-reviewed\n" % (criteria.datetime.datetime.now(
                criteria.datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), ",".join(done)))
    return done



def main():
    done = relock(criteria.git("rev-parse", "--show-toplevel"))
    print("RELOCKED " + ", ".join(done) if done else "RELOCKED nothing: no reviewed page moved only by owner-reviewed lines")
    return 0


if __name__ == "__main__":
    sys.exit(main())
