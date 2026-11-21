# Design: template-only (TD554, TD557, TD559; owner records o677, o678, o679)

Status: APPROVED by the owner's typed yes to item 5 (o679). Written in the idea step of attempt 2, over the branch work at 14b01eb9.

## Problem
The loop shipped two ways: a GitHub template repo and a skills package (a zip built by dev/package.py, with a 100-file cap, a 19,000/20,480 script byte limit and listing.json) that came from the Agensi listing. The owner decided the loop ships only as the template. Text, release, gates and rows must follow.

## Premises (all agreed)
1. The template is the only distribution: no zip is built or uploaded; the release is a tag and its notes (SET-10).
2. The byte limit and the file cap came from Agensi and go with it (GRD-20); page size, requirements per page and test-row caps stay.
3. Requirement text is the owner's: item 5 goes in as drafted, on owner records, never reworded.
4. update.py's package path still has fixtures built by dev/package.py, so package.py and listing.json stay until a follow-up retires that path.
5. Rows that only enforced the package or the byte limit are cut, not kept to satisfy a stale done line (done line 2's script-size half is superseded by o678).

## Approaches
A. Minimal: text and the release workflow only; leave every gate and row. Effort S, risk High (rows keep failing on a limit that no longer exists, the package check stays in CI).
B. Recommended: text, tag-only release, package and byte gates and rows cut, health's script-byte rule removed, byte asserts removed from mixed toys, package.py stripped of its file cap/script size/listing checks and kept as a fixture builder. Effort L, risk Medium (many toys touched; checked against a clean main).
C. Ideal: B plus remove update.py's package path, package.py, listing.json and their toys now. Effort XL, risk High (update/adopt/sync toys and SET-3/4/5 rows are rewritten in the same PR).

RECOMMENDATION: B, because it meets every done line and leaves C as the named follow-up `update-package-path`.

## What this reuses
criteria.py revise/review with owner records, regression.py workflow (regenerates the CI files), settings.py reference, render and restamp-own.

## Distribution
GitHub template repository (the setting is on), versioned by release tags; each template release reaches adopters as an automatic pull request (SET-1, future work, text only here).

## Done lines map
1 text + release + retired rows: item 5 text, release.yml, 39 rows cut with reasons in the PR body. 2: listing.json/package.py half holds (kept, listed); script-size half superseded by o678. 3: docs.py check, render --check, private scan; no script-size check remains.

## Assignment
Run plan, review, qa and ship over the branch; fix what they find on the branch; then goal.py pr picks up #5687. The owner's decisions left: none open.
