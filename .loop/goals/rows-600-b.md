# Second slice of the regression-row cleanup (owner words 03:24: merge the test rows down to 600; Operation TD356, TD370). It merges the remaining safe groups by the pilot's method (rows-600-a, PR 5461: one row per test-script invocation and requirement, run once, every old PASS line checked, any FAIL line fails, POSIX commands that run under dash, descriptions of 400 characters or fewer), with the dash-run step in dev/check-row-merge.py as its first commit. In the same pull request it re-points every live mention of each removed id (dev/toy scripts, the How-to-use pages, README, Home and Principles), checking each hit by hand; history files (CHANGELOG, Roadmap, the triage notes, the readme gap table, designs, DECISIONS, sweeps) keep old ids. Rows on regression-known.tsv and regression-red.tsv stay their own rows, unmerged. The cap max_regression_rows stays 1300 unless this slice reaches 600 or fewer, in which case it drops to 600 in this pull request. It builds now and merges main once after 5456 and 5455 have landed, then pushes; lane prep and the caps guard before the push; no local lane

- Slug: rows-600-b
- Touches: .loop/regression.tsv, docs/wiki, dev
- ETA: 645 active minutes (estimate 513m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given .loop/regression.tsv on this branch, then every merged row covers one script invocation and one requirement, runs it once under dash, checks every PASS line its old rows checked, fails on any FAIL line, and has a description of 400 characters or fewer, and no row on the known or red lists was merged
2. Given the PASS lines checked by all rows on main and on this branch, then the two sets are identical (dev/check-row-merge.py, which also runs every merged row under dash, exits 0)
3. Given every removed id, then no dev/toy script, How-to-use page, README, Home or Principles still names it (each live mention re-pointed to its surviving row), history files keep old ids, the Tests pages re-render, and the docs check passes
4. Given .loop/config.json, then max_regression_rows is 1300, or 600 if this slice brings the count to 600 or fewer, and the pull request states the row count

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
