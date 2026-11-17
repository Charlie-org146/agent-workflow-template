# REG-1: A real change still reaches the root runners while a change only to NO_EFFECT files reaches none; the 7 affected-lane rows pass (#4554)

- Slug: ci-affected-rows
- Touches: not declared
- ETA: 210 active minutes (estimate 166m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given the 7 rows in #4554, when they run on CI, then each passes
2. Given a change to a file that isn't NO_EFFECT, when lanes pick rows, then the root runners still run, and a change only to NO_EFFECT files still reaches none

## Verify by hand

1. Run `python3 dev/toy/test-affected-deleted.py`.
   Expect: four PASS lines, including "a deleted real file reaches the rows that name it and the root runner (['tb', 'tc'])" and "negative control: a deleted VERSION (NO_EFFECT) still reaches no row ([])"; exit 0.
2. Open the pull request's `affected` check (regression-pr.yml) on GitHub, or the next full regression run.
   Expect: the 7 rows from #4554 (affected-quiet-release, merge-wiki-head, merge-wiki-rename-refused, merge-wiki-skill-refused, pass3-symlink-page, merge-reach-fail-closed, merge-base-undiffable) are PASS.
