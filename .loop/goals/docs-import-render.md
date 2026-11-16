# docs.py imports render with a plain import instead of __import__, so the package safety scan passes (#4652)

- Slug: docs-import-render
- Touches: skills/workflow-docs/scripts/docs.py
- ETA: 180 active minutes (estimate 144m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. docs.py imports render with a plain import, no __import__; the package safety scan passes, as do the package-passes and prd-no-dunder-import-3800 rows.
2. entry-adopt, sync-default-source, sync-propose and sync-template-redirect are each run: each passes, or its real cause is written on #4652.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
