# merge.py and wiki.py publish refuse to run from a path inside the repo's own goal worktrees, and merge.py refuses from a checkout behind origin/base, naming the fix; a merge refused for HEAD_MOVED or BASE_MOVED leaves the goal live at pr, not done

- Slug: merge-from-main-checkout
- Touches: docs

## Done lines

Frozen. A wrong done line needs a new goal.

1. merge.py run from a path inside a goal worktree refuses, naming the main checkout or the installed skills as the fix; wiki.py publish refuses the same way
2. merge.py run from a checkout behind origin/base refuses, says how many commits behind and prints the fast-forward command; a current checkout and the installed skills run
3. A merge refused for HEAD_MOVED or BASE_MOVED leaves the goal running at step pr, so goal.py pr then merge.py runs it again

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
