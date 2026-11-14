# The Documentation and Regression pages are current again, so the wiki publish is no longer refused: the sync pointer is on DOC-1 and Regression is re-stamped, both on the owner's recorded words

- Slug: wiki-current
- Touches: docs/wiki/Documentation.md, docs/wiki/Regression.md, DECISIONS.md

## Done lines

Frozen. A wrong done line needs a new goal.

1. docs.py check --own prints no STALE line for Documentation or Regression
2. DOC-1 carries the docs.py sync pointer as a sub-bullet and DECISIONS.md records it and the Regression re-stamp

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
1. From the repo root run `python3 skills/workflow-docs/scripts/docs.py check` and `docs.py check --own`.
   Expect: `DOCS OK: 10 pages` from both, with no `STALE Documentation` or `STALE Regression` line.
2. Open `docs/wiki/Documentation.md` and read DOC-1.
   Expect: its last sub-bullet says a PRD that lives outside the repo is kept in step through `docs.py sync`, and the Review lines of Documentation and Regression read `Reviewed 2026-11-14`.
