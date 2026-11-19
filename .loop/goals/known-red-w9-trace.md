# The nightly row lanes-trace (bash dev/toy/check-reads.sh), red on main since 2026-11-10 because one serial replay of every land command runs past the 900-second row limit, passes again by sharding the replay (owner: "No waivers u can do it"; operation-top: shard, no timeout raise).

- Slug: known-red-w9-trace
- Touches: not declared
- ETA: 275 active minutes (estimate 218m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. check-reads replays every land command of .loop/regression.tsv across shards, and a count check proves the union of the shards equals the full land list, with a negative control that a dropped command fails the count
2. Each shard finishes under the existing 900-second row limit in the CI full-suite run, with no per-row timeout raised; if sharding can't get under 900 seconds, the measured numbers go to the operation and nothing is merged
3. lanes-trace passes on the PR head in CI once the other land rows are green; no row is added to .loop/regression-known.tsv, and net regression rows are 0 or fewer against main

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
