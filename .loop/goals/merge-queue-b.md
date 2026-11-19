# Merge evidence tolerates stamp-only commits: a pass recorded for a tested tree carries over to a landing commit that differs only in the STAMPS paths (VERSION, CHANGELOG.md and the goal.py pr record files), so a release commit or a record commit never needs a fresh CI run (slice B of the merge queue; owner 01:42 o364; TOP-DECISION 99).

- Slug: merge-queue-b
- Touches: not declared
- ETA: 270 active minutes (estimate 213m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. carried() generalises to the STAMPS constant from slice A, and a tree-equal-modulo-stamps (TEMS) compare treats two commits as equal only when their diff is a subset of STAMPS, each a regular file, never a symlink or a rename into one; any other path breaks equality
2. merge.py, operate.py wiki-only and the release path use the one TEMS compare; negative controls show a code change, a symlink and a rename into a stamp path each break equality, and a stamp-only commit carries the exact sha's CI evidence
3. No new file, every script stays under its size cap, net regression rows 0 or fewer, the Release and Delivery pages state the rule, and a new requirement ID, if any, is reserved with operation-mac first and lands Unreviewed

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
