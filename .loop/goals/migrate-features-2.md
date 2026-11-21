# Migrate every live template requirement into the feature format in place (goal G1 of the v1.1.0 brief, owner o700 typed 23:18; Operation TD658, TD659): each keeps its ID, page and every word, no page is rebuilt, nothing is lost, every old Reviewed mark is cleared and listed, missing metrics, tests and references are marked, features over five requirements are listed to split, with a report and a safe re-run. Re-frozen as migrate-features-2 (owner o711) to add ls-narrow-triggers to the known-to-fail list, citing #4061

- Slug: migrate-features-2
- Touches: docs/wiki, README.md, docs, .loop/regression-known.tsv
- ETA: 325 active minutes (estimate 259m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given every live requirement (27 on main), then it becomes a feature on the page where it already is, keeping its ID, its page and every word, proven by a hash of each requirement's text before and after listed in the report
2. Given every page outside those 27 entries, then it is byte-identical before and after; no page is rebuilt and the How-to-use pages and figures stay
3. Given the counts of test links, revision rows and references, then they are the same before and after, each requirement shows its metric from its page's Success metrics or 'metric missing' and its test or 'test missing', and each feature shows its references or 'reference missing'
4. Given the old Reviewed marks, then every one is cleared and listed in the report with its date and record, and features with more than five requirements are listed 'to split'
5. Given a second run of the migration, then it leaves an empty diff, and the goal stops at the PR
6. Given .loop/regression-known.tsv, then it gains one row for ls-narrow-triggers citing #4061 (macOS-only, red on main; owner o711), no other row changes, and the qa lane at the final head shows no FAIL

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
