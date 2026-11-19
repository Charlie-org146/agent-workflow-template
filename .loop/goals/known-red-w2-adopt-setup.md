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
1. Run `LOOP_FREE_GB=4.5 python3 skills/workflow-regression/scripts/regression.py run settings-reference-fresh agent-routing set1-docs-format adopt-fixture-bare-agent`.
   Expect: RESULT 4 passed, 0 known, 0 failed.
2. Run `bash dev/toy/test-adopt-fixtures.sh` with no argument.
   Expect: four PASS adopt-fixture lines.
