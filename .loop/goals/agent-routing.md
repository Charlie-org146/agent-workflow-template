# The agent-routing regression row passes on main again (#4943; known row 43, failing since v1.0.72 or earlier). Find why its behaviour assert fails, fix it at the cause, and take the row off the known list. This also lets del-16-on-page's wording check retire (TD437)

- Slug: agent-routing
- Touches: skills, dev/toy, .loop
- ETA: 385 active minutes (estimate 307m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given this branch, then the agent-routing row passes, and the pull request says why it failed, with evidence
2. Given .loop/regression-known.tsv on this branch, then it has no agent-routing row, and del-16-on-page's wording check is retired as TD437 says
3. Given this goal's diff, then every script stays under 20,480 bytes, docs.py check and criteria.py render --check pass, and any new regression row has a red proof (regression.py red)

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
