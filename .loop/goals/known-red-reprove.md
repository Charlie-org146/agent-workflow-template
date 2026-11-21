# Known-red rows that pass on GitHub come off the known list (REG-4; v2.0 part 3, TD524 and TD525): read the next scheduled full regression run on main (cron 17 */4, about 16:17 PST) and, for every row on .loop/regression-known.tsv, the 15 marked fails on main since v1.0.72 or earlier first, take off each row that run prints PASS for with its command unchanged since the run, citing the run id; rows that fail or did not run stay

- Slug: known-red-reprove
- Touches: .loop, docs
- ETA: 295 active minutes (estimate 236m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given the full run's logs, then every known row it printed PASS for, with an unchanged command, is removed and cited, and every other known row stays with the reason
2. Given the pull request, then it removes rows only (nothing added), names the run id and each removed row's PASS line, and docs.py check and criteria.py render --check pass
3. Given this goal's diff, then no file is added to the package (100 files), no script changes, and the private scan is clean

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
