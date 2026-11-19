# The merge-guard, merge-wiki and statuses regression rows that are red on main in the full run 44463859531 pass again: merge-guard-base-head merge-wiki-head merge-wiki-rename-refused merge-wiki-skill-refused pass3-symlink-page st-merge-wiki-head st-post-fails st-release-pr st-union-contexts restamp-at-merge-3867 package-gate-head. Each is fixed, or removed with evidence that the behaviour it tests is gone; none is moved to the known list (owner: "No waivers u can do it").

- Slug: known-red-w5-merge-st
- Touches: not declared
- ETA: 285 active minutes (estimate 226m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Each of these rows passes on the PR head in the CI full-suite shards, or is removed from .loop/regression.tsv with evidence in the PR that the behaviour it tests no longer exists: merge-guard-base-head merge-wiki-head merge-wiki-rename-refused merge-wiki-skill-refused pass3-symlink-page st-merge-wiki-head st-post-fails st-release-pr st-union-contexts restamp-at-merge-3867 package-gate-head
2. No row is added to .loop/regression-known.tsv, and net regression rows are 0 or fewer against main

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
