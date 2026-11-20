# Inside each PR shard's time budget, selected rows run closest-to-the-change first (TD476): first rows whose command names a file the PR changed, then rows for requirements the PR touches, then the rest by measured time, shortest first. Nothing is dropped: LEFT rows still go to the full run. Evidence: #5559 changed dev/toy/test-session-workers.sh, and the rows that run it (session-reports, held-all) were selected but LEFT, because each shard ran 19 of 134

- Slug: budget-order
- Touches: skills, dev/toy, .github
- ETA: 435 active minutes (estimate 345m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a toy diff that changes one toy, when shards are planned with a budget that fits only a few rows, then that toy's row runs first, where before it was LEFT, and a toy proves both orders
2. Given #5559's diff replayed against today's rows, then session-reports and held-all are in the run set, not LEFT
3. Given this goal's diff, then every script stays under 20,480 bytes, no selected row is dropped from the LEFT list, docs.py check and criteria.py render --check pass, and each new regression row has a red proof (regression.py red)

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
