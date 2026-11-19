# The sync, apply-rerender, listing and stale-code-page regression rows that are red on main in the full runs 44463859531 and 44465229184 pass again: sync-apply-keeps sync-default-source sync-template-redirect docs-import-rows-pass apply-rerender-accepted apply-rerender-blocks apply-rerender-hand-edit listing-names-every-command stale-code-page-unreviewed. Each is fixed, or removed with evidence that the behaviour it tests is gone; none is moved to the known list (owner: "No waivers u can do it").

- Slug: known-red-w10-sync-apply
- Touches: not declared
- ETA: 290 active minutes (estimate 230m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Each of these rows passes on the PR head in the CI full-suite shards, or is removed from .loop/regression.tsv with evidence in the PR that the behaviour it tests no longer exists: sync-apply-keeps sync-default-source sync-template-redirect docs-import-rows-pass apply-rerender-accepted apply-rerender-blocks apply-rerender-hand-edit listing-names-every-command stale-code-page-unreviewed
2. No row is added to .loop/regression-known.tsv, and net regression rows are 0 or fewer against main

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
