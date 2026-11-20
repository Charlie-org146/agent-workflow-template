# The template turns on merge batching: .loop/config.json sets merge_batch true (owner o256)

- Slug: merge-batch-on
- Touches: not declared
- ETA: 240 active minutes (estimate 192m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given .loop/config.json on main, when merge.py runs two or three goals with --batch, then it no longer refuses with 'several goals need --batch and merge_batch true'
2. settings.py show lists merge_batch true for this repo, and START.md and the settings reference render it

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
