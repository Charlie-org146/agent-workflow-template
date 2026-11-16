# A generated Home that docs.tsv maps to code no longer stays STALE and blocks merge when its fresh render is unchanged (#4608)

- Slug: home-stale
- Touches: not declared
- ETA: 210 active minutes (estimate 166m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. A goal that changes a path mapped to Home in .loop/docs.tsv, with Home's fresh render unchanged, passes docs.py check and merge.py; a negative control shows a Home that differs from its fresh render still fails.
2. A toy runs a fixture repo whose fully generated Home maps README.md and .loop/config.json, changes one of them, and shows check clears, with DOC-4 still passing on that Home.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
