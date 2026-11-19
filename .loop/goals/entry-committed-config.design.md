# Design: entry-committed-config

## Problem
`entry.py` reads `.loop/config.json` from the working tree. A worker's worktree can carry a local skip-worktree edit
(for example `min_free_memory_gb` 2.0 against the committed 3.0), so `entry.py write` renders a START.md that differs from
what CI and `merge.py`'s stale check render from the committed file, and the check fails.

## Approaches
1. Always read the committed file (`git show HEAD:.loop/config.json`). Cost: small. Risk: a config edited but not yet
   committed (setup writing a new setting, then `entry.py write`) renders stale until commit.
2. Read the committed file only when the file is marked skip-worktree (`git ls-files -v` prints `S`); otherwise read the
   working copy as today. Cost: one extra git call. Risk: low; an ordinary edit still renders at once, and only the
   local-override case is ignored, which is the goal.

## Chosen
Approach 2, in `config(root)`. Falls back to the working copy when git is missing, the repo has no commit, or the show fails.
`entry.py` is already over the 19,000-byte cap on main (19,337), so the change must be net-zero bytes: trim comments or
wording elsewhere in `entry.py` by the amount added. No new shipped file; the test row reuses an existing `dev/toy` script.

## Done lines
1. Needs the `config()` change and a toy test: skip-worktree a copy of config.json with 2.0, run `entry.py write`, expect
   3.0 in START.md and `entry.py check` clean.
2. Needs one regression row (seen failing on main's `entry.py`, passing after) and a sentence on the Documentation page
   stating the rule, marked for owner review.

## Open questions
None.
