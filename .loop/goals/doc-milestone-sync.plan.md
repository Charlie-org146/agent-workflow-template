# Plan: doc-milestone-sync

## Steps
1. `criteria.py unreview Documentation --user --owner-record o85` (done): the page loses its Reviewed mark.
2. Reword the one Non-goals line in `docs/wiki/Documentation.md` to the owner's text (done).
3. Add `dev/toy/test-doc-nongoal-milestone.py` and the row `doc-nongoal-milestone-sync` for DOC-17 (done), seen failing on the old line and passing on the new one.
4. Re-render the Tests tables; run the docs check.

## Tests
- Done line 1: the row above; its red proof is recorded.
- Done line 2: the owner's approval is recorded as o85; the page reads Unreviewed.

## What could break
The page's lock: the only edit is the owner-approved line, made after the un-review. A concurrent goal (howto-per-requirement) also un-reviews this page; whichever merges second merges main and keeps both.

## Out of scope
Any other wording on the page; marking anything Reviewed.
