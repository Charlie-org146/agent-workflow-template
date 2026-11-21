# A PR that changes .loop/regression.tsv or .loop/regression-known.tsv runs every row its changes reach with no --budget, so nothing is LEFT (TD512): rows-600-c (#5607) changed regression.tsv and left docs-import-rows-pass broken, and main stayed red about an hour with 9 releases on top. Rows PRs are rare, so the extra minutes land only on them; every other PR keeps the shard budget

- Slug: rows-pr-full
- Touches: .github, skills, dev/toy
- ETA: 350 active minutes (estimate 278m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a PR whose diff touches .loop/regression.tsv or the known list, then its PR shards run every reached row with no budget and print no LEFT rows; given a normal PR, the budget and LEFT behaviour are unchanged (toy with both cases, negative control)
2. Given the pull request, then its toy row is SEEN RED with the change reverted, the committed regression-pr.yml equals the rendered one, and docs.py check and criteria.py render --check pass
3. Given this goal's diff, then no file is added to the package (100 files), no script newly crosses 19,000 bytes, every script stays under 20,480, and the private scan is clean

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
