# Fixes #5674: every push or GitHub-write site runs the private-name scan before it writes. fit.py pr_open, autorelease.py label_part, merge.py merge_pr, review.py promote and revert, machines.py batch_assemble and batch, and operate.py apply call the same scan the other push sites use, including promote's release notes that carry closed-issue titles. Adds scans only, loosens nothing, reads no private-name list itself (the scan does), and adds no site to an allow-list

- Slug: scan-every-push-site
- Touches: skills, dev/toy, .loop/regression.tsv, docs/wiki
- ETA: 260 active minutes (estimate 205m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given dev/toy/test-scan-sites.sh, then it exits 0 with no FAIL line on this branch and fails on main (a defect row linked to #5674, seen failing then passing)
2. Given a planted private name in each newly scanned site's payload (pull request text, label, merge, release notes, batch and apply), then that write is refused before it reaches GitHub, and a clean payload still goes through (a toy with negative controls)
3. Given this goal's diff, then only the eight sites' scripts, the toy, the row, re-rendered pages and the goal's own records change; no scan or check is weakened, the docs check passes and the private scan is clean

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
