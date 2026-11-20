# Known-red-zero group F (TD493, #5304): dev/toy/test-criteria.sh fails 3 checks (conforming page, rendered table, reviewed page), which hides 57 asserts behind rows no-usage-passes, refused-unmet, tests-row-shape and tests-table-columns. Find the one fixture or format cause and fix it at the cause, without weakening any assert, then take the 4 rows off the known list

- Slug: criteria-toy-fix
- Touches: dev/toy, skills, .loop
- ETA: 445 active minutes (estimate 355m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given test-criteria.sh on this branch, then it prints ALL PASS, and the pull request names the cause with evidence
2. Given .loop/regression-known.tsv on this branch, then the 4 rows are off it, each passing, and nothing is added
3. Given this goal's diff, then the package stays at 100 files, no script newly crosses 19,000 bytes, package.py --static, docs.py check and render --check pass, and each fixed row has a red proof

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
