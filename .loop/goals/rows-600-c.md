# Bring .loop/regression.tsv from about 1,125 rows toward 600 under REG-4: one row per test script and requirement, a row running every case of its script for that requirement, nothing dropped

- Slug: rows-600-c
- Touches: .loop/regression.tsv, .loop/regression-known.tsv, .loop/regression-red.tsv, .loop/regression-runs.tsv, .loop/regression-issues.tsv, docs/wiki/Tests.md, dev/toy/
- ETA: 490 active minutes (estimate 391m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given .loop/regression.tsv before and after, then rows that call the same script for the same requirement (same level, type and link) are merged into one row, the row count falls from 1,126 toward 600, and the PR body shows the before and after counts
2. Given every old row, then each case it ran (its script, arguments and checked output) still runs in the merged row, nothing is dropped and nothing goes on the known list; a one-time coverage output in the PR body lists every old row id with the merged row that runs it and counts zero uncovered
3. Given a merged row, then its command runs under dash (no bash-only syntax outside bash -c), runs each distinct script call once and checks every case, and its description is 400 characters or fewer and starts Given, when, then
4. Given the old row ids, then no file still names an id that no longer exists: the wiki Tests tables are re-rendered, the known, red, runs and issues lists and every toy that names an id are updated, and the full docs check prints DOCS OK
5. Given this goal's diff, then it is data only: no file under skills/ is added or changed, no script over 20,480 bytes is added, net regression rows fall by at least 400 and never rise, and no requirement text changes

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
