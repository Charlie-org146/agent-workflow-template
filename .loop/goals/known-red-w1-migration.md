# The migration regression rows that are red on main in the full run 44463859531 pass again: migration-blocks-inserted migration-clean migration-flags migration-gaps-pr migration-gaps-state migration-major-refused migration-robustness migration-v1 migration-writes-nothing. Each is fixed, or removed with evidence that the behaviour it tests is gone; none is moved to the known list (owner: "No waivers u can do it").

- Slug: known-red-w1-migration
- Touches: not declared
- ETA: 280 active minutes (estimate 221m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Each of these rows passes on the PR head in the CI full-suite shards, or is removed from .loop/regression.tsv with evidence in the PR that the behaviour it tests no longer exists: migration-blocks-inserted migration-clean migration-flags migration-gaps-pr migration-gaps-state migration-major-refused migration-robustness migration-v1 migration-writes-nothing
2. No row is added to .loop/regression-known.tsv, and net regression rows are 0 or fewer against main

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
