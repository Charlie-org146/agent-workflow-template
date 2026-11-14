# wiki-current: plan

Design: `.loop/goals/wiki-current.design.md`, approach A (owner-recorded un-review, edit, review).

## Build steps, in order

1. Add the DECISIONS.md section "wiki-current: DOC-1 sync pointer and Regression re-stamp (2026-11-14)": the owner's
   words, record o13, the sub-bullet verbatim, and that Regression is un-reviewed and reviewed with no text change.
   Commit it first: `.loop/docs.tsv` maps DECISIONS.md to Home, so this commit stales Home and Home is brought current in
   step 6.
2. `criteria.py unreview Documentation DOC-1 --user --owner-record o13` (exists: `criteria.py`, SKILL.md "The PRD is the
   owner's"; a record covers one unreview and one review).
3. Add the DOC-1 sub-bullet (below) as DOC-1's last sub-bullet in `docs/wiki/Documentation.md`, nothing else.
4. `criteria.py review Documentation DOC-1 --user --owner-record o13` (restamps the page and DOC-1's seal).
5. Regression: `criteria.py unreview Regression --user --owner-record o14`, then `criteria.py review Regression --user
   --owner-record o14`: no text change; the Review line's date moves, which git keeps as a commit to the page.
   (o14 covers Documentation and Regression; o13 is used up on Documentation by step 4, and covers REG-1 only if the
   requirement needs it, which it does not.)
6. `criteria.py render`, `entry.py write`, then bring Home current with its own true edit if `docs.py check` prints
   `STALE Home`; commit.
7. Add the regression row `doc1-sync-pointer` (below) and render the Tests page.

DOC-1 sub-bullet, verbatim:

```
  - A feature whose PRD lives outside the repo, in Notion or behind a link, keeps the repo's copy in step through `docs.py sync`, which reports each drifted requirement and rewrites only the repo's copy (External PRDs, EXT-1).
```

## Tests (each seen red before the change)

- Done line 1: the existing `settings-render-fresh` row (`! docs.py check --own | grep '^STALE'`) is red now (both pages
  stale) and green after step 5; plain `docs.py check` printing `DOCS OK` is checked by hand too, because publish uses it.
- Done line 2: new land row `doc1-sync-pointer`: `grep -A12 'DOC-1:' docs/wiki/Documentation.md | grep -q 'docs.py sync'`
  and `grep -q 'wiki-current: DOC-1 sync pointer' DECISIONS.md`; seen red with `regression.py red` against the
  unchanged HEAD.

## What could break

- A reviewed lock: the unreview and review go through `criteria.py` only, so no hand-edited stamp, no forged review.
- A record used twice is refused with nothing changed; if o13 or o14 is refused, stop and tell the operation session.
- DOC-1's headline is untouched, so the SCRIPT rule (it reads the headline only) is not tripped.
- Editing DECISIONS.md stales Home; step 6 handles it.

## Out of scope

Any other stale page, rows re-linked, edit-and-revert, and reviewed text other than the one sub-bullet.

PENDING: none
