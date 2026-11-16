#!/usr/bin/env python3
"""The review hold (DEL-13, issue 3803): with "review_hold": true in .loop/config.json, merge.py merges a goal only after
the operation session has recorded that it read the diff.

usage: review.py record SLUG

record stores the pull request's head as the reviewed one; a later push moves the head, so the hold applies again. Only
the operation role records: LOOP_ROLE=worker, or a path inside a goal worktree, is refused and nothing is written.
Until a review of the current head is recorded merge.py refuses with REVIEW_HOLD; the goal stays done and `review_wait`
puts "merge waiting on review" on the board and in the check-in. It runs git and gh and nothing else.
"""
import glob
import json
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import release  # noqa: E402
os.environ.setdefault("GIT_TERMINAL_PROMPT", "0")


def worker():
    """True for a worker or a path inside a goal worktree, where a goal could record its own review."""
    common = release.git("rev-parse", "--path-format=absolute", "--git-common-dir", check=False)
    inside = os.path.join(os.path.normcase(os.path.realpath(common)), "loop", "worktrees") + os.sep
    return os.environ.get("LOOP_ROLE") == "worker" or os.path.normcase(os.path.realpath(os.getcwd())).startswith(inside)


def held(cfg, state, head):
    """"" when merging may go ahead, else the REVIEW_HOLD refusal: the setting is on and HEAD has no recorded review."""
    if cfg.get("review_hold") is not True:
        return ""
    if head and (state.get("review") or {}).get("head") == head:
        state.pop("review_wait", None)
        return ""
    return ("REFUSED (REVIEW_HOLD): review_hold is on and no review of the pull request head %s is recorded; nothing was merged. "
            "Fix: the operation session reads the diff, then review.py record %s, then merge.py %s." % (
                (head or "unknown")[:12], state["slug"], state["slug"]))


def wait(state):
    """Mark the goal as a merge waiting on review (exit 5)."""
    state["review_wait"] = True
    release.save(state, "merge waiting on review (REVIEW_HOLD)")
    return 5


def record(slug):
    if worker():
        sys.exit("REFUSED: only the operation session records a review; a worker or a goal worktree cannot. Nothing was recorded. "
                 "Fix: from the main checkout, as the operation session, run review.py record %s. (REVIEW_ROLE)" % slug)
    state = release.load(slug)
    seen = release.run(["gh", "pr", "view", state.get("pr") or "", "--json", "headRefOid"])
    head = json.loads(seen.stdout or "{}").get("headRefOid") if seen.returncode == 0 else None
    if not state.get("pr") or not head:
        sys.exit("REFUSED: %s has no open pull request to review. Fix: goal.py pr %s first." % (slug, slug))
    state["review"] = {"head": head, "at": release.now()}
    state.pop("review_wait", None)
    release.save(state, "review recorded for pull request head %s by the operation session" % head[:12])
    print("REVIEW RECORDED %s at %s" % (slug, head[:12]))
    return 0


def main():
    if sys.argv[1:2] in (["-h"], ["--help"]):
        print(__doc__)
        return 0
    if sys.argv[1:2] != ["record"] or len(sys.argv) != 3:
        sys.exit(__doc__)
    return record(sys.argv[2])


def proven(top):
    """Row ids with a PASS on the current commit in any lane record of this repo (loop/tests/*.json in the git common folder).
    regression-runs.tsv holds no commit, so a PASS there is not trusted: a row that passed on an older commit runs again."""
    head = release.git("rev-parse", "HEAD", cwd=top, check=False)
    common = release.git("rev-parse", "--path-format=absolute", "--git-common-dir", cwd=top, check=False)
    found = set()
    for path in glob.glob(os.path.join(common, "loop", "tests", "*.json")):
        try:
            rows = json.load(open(path)).get("rows") or {}
        except (OSError, ValueError, AttributeError):
            continue
        found |= {key for key, item in rows.items() if isinstance(item, dict) and item.get("status") == "PASS" and item.get("commit") == head}
    return found


def left_text(left):
    """The LEFT section of the cut's output and release notes: the count and the ids, or '' when nothing was left."""
    return "\n## LEFT\n\nLEFT %d rows were not run before the cut's stop: %s\n" % (len(left), ", ".join(left)) if left else ""


def criteria(top, cfg, doc_rows, fails):
    """(unmet, left): requirements with no passing row, and the rows the cut did not run before its stop (900 seconds, or
    LOOP_CUT_SECONDS). A row is skipped when it is known failing or has a PASS on the current commit; the rest run until the stop."""
    seconds = float(os.environ.get("LOOP_CUT_SECONDS") or 900)
    try:
        rows = [line.rstrip("\n").split("\t") + [""] * 5 for line in open(os.path.join(top, ".loop", "regression.tsv")) if line[0] != "#"]
    except OSError:
        rows = []
    out, left, stop, skip = [], [], time.time() + seconds, proven(top)
    try:
        skip |= {line.split("\t")[0] for line in open(os.path.join(top, ".loop", "regression-known.tsv")) if line[0] != "#"}
    except OSError:
        pass
    for page in doc_rows(top):
        try:
            part = (re.split(r"\n## (?:Requirements|Criteria)[ \t]*\n", re.sub(r"(?ms)^```.*?^```[^\n]*$", "", open(os.path.join(
                top, cfg.get("wiki_dir") or "docs/wiki", page + ".md")).read()), maxsplit=1) + [""])[1].split("\n## ")[0]
        except OSError:
            continue
        for key in re.findall(r"^- ([A-Z]{2,5}-\d+): \S", part, re.M):
            found = [r for r in rows if key in (r[0], r[3])]
            out += ["%s (no regression row)" % key] * (not found)
            for row in found:
                if row[1] == "covered" or row[0] in skip:
                    continue
                if row[1] != "draft" and time.time() >= stop:
                    left.append(row[0])
                elif row[1] == "draft" or fails(row[2], top):
                    out.append("%s (row %s is a draft or failing)" % (key, row[0]))
                else:
                    skip.add(row[0])
    return out, left


if __name__ == "__main__":
    sys.exit(main())
