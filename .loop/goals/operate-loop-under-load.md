# The operate loop is tested under load (TD442; follow-up to #5521; issue 5478 stays open until this lands). #5521 made the load row run only the timing groups (waits, status, reports, follow-up, worker guard) under the busy loops; the operate-loop section (about 32 s of the 57 s script, unloaded) runs only unloaded in operate-all. Add one row, operate-loop-under-load: the operate-loop section only, run 2 or 3 times under one busy loop per CPU, each a hard ALL PASS, no retry, measured. If it fits the 200-second row limit it ships; if it does not fit even at 2 runs, it does not ship and the pull request instead files an issue 'operate loop not tested under load' with the measured time, linked from 5478. Also, in the same pull request as a separate listed fix: docs/wiki/Regression.md's regression-round Schedule line still says 'on every release tag' (stale since e7478a40 dropped the tag trigger); it becomes 'every 4 hours (...) and by hand'

- Slug: operate-loop-under-load
- Touches: dev/toy, .loop/regression.tsv, docs/wiki/Regression.md
- ETA: 425 active minutes (estimate 338m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given the new row in CI, then it runs the operate-loop section 2 or 3 times under the busy loops with a hard ALL PASS each, finishes within 200 s with its measured time in the pull request, and a negative control (a slowed operate loop) fails it; or, if it cannot fit, the pull request files the issue with the measured time and adds no row
2. Given docs/wiki/Regression.md, then the regression-round Schedule line no longer names a release tag and matches regression.yml (the cron and by hand), and no Reviewed requirement text changes
3. Given this goal's diff, then only the toy, at most one new row, the Regression page's Schedule line and the goal's record files change, and docs.py check, criteria.py render --check and role.py over_caps pass

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
1. Run `bash dev/toy/test-operate-loop-load.sh`.
   Expect: `operate loop under load (N busy loops): 2 of 2 passed`, the negative control line (an agent slower than the patience fails the operate loop), and ALL PASS, in about two minutes.
2. Run `grep -c "on every release tag" docs/wiki/Regression.md`.
   Expect: 0.
