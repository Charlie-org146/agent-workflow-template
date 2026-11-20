# Every row that fails in main's per-release regression run 44680897573 (v1.0.111, 79 rows) is on .loop/regression-known.tsv with its open regression issue and, where known, the release where it first failed, so no lane or CI run fails on a red row of main (TD274: known-red-9 would likely fail its own CI, because the CI job runs the same selection on Linux and reaches rows such as no-usage-passes, set1-docs-format and plan-cache-key that fail there and were not among its nine). The goal changes only .loop/regression-known.tsv besides its own record files: no test, script or regression row is added, changed or removed, no existing known line is removed, and health keeps counting every one of the rows. Rows with a fix goal in flight (kept-fragments-reds, kept-reds-5, kept-reds-2, principle-8-readme) say so in their reason, and each of those goals removes its own lines in its own pull request when it fixes them. It replaces known-red-9 and known-red-sync, whose commits stay on their branches

- Slug: known-red-all
- Touches: .loop/regression-known.tsv
- ETA: 345 active minutes (estimate 275m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given .loop/regression-known.tsv on this branch, when the ids it adds are compared with the ids that print #### FAIL in the log of run 44680897573, then the two sets are equal: all 79 are added and none other, each line names its open regression issue, and the 38 old lines are unchanged
2. Given this goal's diff, then only .loop/regression-known.tsv and the goal's own record files change, so no test, script, requirement or regression row is added, changed or removed, no existing known line is removed, and net regression rows are 0
3. Given the nine rows with a fix goal in flight, then each line says which goal fixes it

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
