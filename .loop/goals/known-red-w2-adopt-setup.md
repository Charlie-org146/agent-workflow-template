# The adopt and setup regression rows that are red on main in the full run 44463859531 pass again: adopt-fixture-bare-agent adopt-fixture-ci-gitignore adopt-fixture-existing-checks adopt-fixture-feature-milestones entry-adopt setup-fit agent-routing set1-docs-format settings-reference-fresh. Each is fixed, or removed with evidence that the behaviour it tests is gone; none is moved to the known list (owner: "No waivers u can do it").

- Slug: known-red-w2-adopt-setup
- Touches: not declared
- ETA: 280 active minutes (estimate 221m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Each of these rows passes on the PR head in the CI full-suite shards, or is removed from .loop/regression.tsv with evidence in the PR that the behaviour it tests no longer exists: adopt-fixture-bare-agent adopt-fixture-ci-gitignore adopt-fixture-existing-checks adopt-fixture-feature-milestones entry-adopt setup-fit agent-routing set1-docs-format settings-reference-fresh
2. No row is added to .loop/regression-known.tsv, and net regression rows are 0 or fewer against main

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
