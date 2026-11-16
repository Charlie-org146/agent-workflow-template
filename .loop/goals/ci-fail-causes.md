# Every failing row in the full regression run on main is grouped by cause, and each cause is fixed, filed or marked known (#4516, #4515)

- Slug: ci-fail-causes
- Touches: dev/toy, .loop/regression-known.tsv, .loop/regression.tsv

## Done lines

Frozen. A wrong done line needs a new goal.

1. Every failing row in full run 43807419354 (or the next full run on main if that one is cancelled) is in exactly one cause group in a comment on #4516, with the group's shared error lines and its rows.
2. Each cause group is fixed in this goal, filed as an issue on milestone v1.1, or added to .loop/regression-known.tsv with its reason, and #4516 links every group's outcome.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
