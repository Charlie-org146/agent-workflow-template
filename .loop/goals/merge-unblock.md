# Unblock merges: a goal that stales a Reviewed page only through mapped code is re-stamped at merge (#3867); max_merge_rounds 8 and a started pr lane holds the merge slot; the govern hook refuses a worker commit in the main checkout and merge.py handles a dirty regression-runs.tsv itself

- Slug: merge-unblock
- Touches: skills/workflow-release/scripts, skills/workflow-docs/scripts, skills/workflow-monitoring/scripts, skills/workflow-delivery/scripts, skills/workflow-setup, dev/toy, .loop/config.json, .loop/regression.tsv, docs/wiki, docs/prds

## Done lines

Frozen. A wrong done line needs a new goal.

1. A. When a goal's diff stales a Reviewed page only through mapped code or config, with none of the page's text changed, the page is re-stamped automatically at merge, logged with the goal's slug, and needs no owner words; a change to the page's wording still needs them (#3867) B. The template's max_merge_rounds goes from 3 to 8 in .loop/config.json and the shipped default if registered; a goal whose pr lane has started holds the merge slot until it merges or fails, so a disjoint goal's merge.py waits for it, without duplicating budget-fair (#4261) in board_log.py C. The govern hook refuses a worker's commit in the main checkout, and merge.py stashes and restores a dirty .loop/regression-runs.tsv itself before fast-forwarding Every touched file stays at or under 19,000 bytes and the package at 98 files or fewer; each of A, B and C has a toy case proven red

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->

1. In a scratch repo, map a Reviewed page to a.py, then change only a comment in a.py and run `python3 skills/workflow-docs/scripts/docs.py check`. Expect: the page is not STALE.
2. Change a line of code in a.py instead and run the same check, then `python3 skills/workflow-docs/scripts/audit.py restamp SLUG PAGE`. Expect: RESTAMPED PAGE, the page's Review line ends in `kept SLUG@sha`, and `.git/loop/reviews.tsv` has a restamp row naming SLUG.
3. Run `python3 dev/toy/test-merge-unblock.py`. Expect: every line PASS, ending in `PASS: merge-unblock A`.
4. Read `max_merge_rounds` in `.loop/START.md`. Expect: default 8.

Closes #3867, closes #3122.
