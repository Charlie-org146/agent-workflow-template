# Lane prep never moves HEAD or fails on a fresh clone (patch for DEL-17; fixes #5728, #5730, #5735)

- Slug: lane-prep
- Touches: skills/workflow-delivery, skills/workflow-docs, dev/toy, .loop/regression.tsv, docs, skills/workflow-release
- ETA: 265 active minutes (estimate 210m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a lane started on a loop/ branch with nothing stale, then restamp-own commits nothing and HEAD does not move; a stale page is still re-kept (negative control)
2. Given goal.py pr's regen, then README and the wiki are committed together or neither changes, so the pr lane never refuses LANE_DIRTY on the tool's own render; a hand edit still refuses (negative control)
3. Given a fresh clone with no .git/loop/runs, then the first lane start creates it and runs
4. Given the change, then checks green (docs, package, private-name), no existing row turns red, no test loosened, no new file under skills/

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
