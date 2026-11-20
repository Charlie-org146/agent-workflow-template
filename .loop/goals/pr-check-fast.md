# The pull-request check catches what the merge queue catches, and runs in about half the time (TD402/TD403/TD417; owner words about 05:15 'cut merge time by half'; DEL-17 one clock, HLT-2). First: the PR check's affected job also runs docs.py check on the merged ref with no review log present (the way the merge queue's small step and a CI checkout see it), so a page-level LOCKED line, a FORMAT line or any docs failure fails the pull request, not the queue (tonight this gap dropped #5470, #5374 and #5499 from the queue). Second: 8 PR shards with a 120-second per-shard budget instead of 6 with 240, so the check takes about 2.3 minutes; the rows left over are LEFT and named, as shard-balance made them, and run in the full suite. Edit lanes_cli.py's NARROW and regenerate regression-pr.yml; lanes_cli.py is at 20,475 of 20,480 bytes, so real trims only, no reformatting

- Slug: pr-check-fast
- Touches: skills/workflow-regression/scripts/lanes_cli.py, .github/workflows/regression-pr.yml, dev/toy
- ETA: 425 active minutes (estimate 338m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a pull request whose merged result fails docs.py check (a page whose reviewed Requirements changed with no review log, as #5499's first queue run showed), when the PR check runs, then the affected job fails with the docs check's own line; and given a pull request whose docs pass, then that step passes (both proved by a toy or workflow check)
2. Given the regenerated regression-pr.yml, then it runs 8 shard jobs with a 120-second budget each plus the docs step, the LEFT rows are listed in the affected job, and the first three pull requests after it lands are measured from last commit to main and sent to operation-top
3. Given this goal's diff, then only lanes_cli.py, regression-pr.yml, at most one toy and the goal's record files change, lanes_cli.py stays under 20,480 bytes with real trims, and docs.py check and criteria.py render --check pass

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
1. Run `python3 dev/toy/test-shard-balance.py | tail -6`.
   Expect: PASS for 8 shards with a 120-second budget, PASS for the docs step on a clean clone (exit 0), and PASS for the negative control: a changed reviewed requirement with no review log fails the step with its own LOCKED line.
2. Open the next pull request's regression-pr run.
   Expect: 8 shard jobs, and an affected job whose first step is `docs.py check`.
