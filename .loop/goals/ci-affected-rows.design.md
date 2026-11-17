# ci-affected-rows design

## Problem
The 7 rows in #4554 (`affected-quiet-release`, `merge-wiki-head`, `merge-wiki-rename-refused`, `merge-wiki-skill-refused`,
`pass3-symlink-page`, `merge-reach-fail-closed`, `merge-base-undiffable`) all run `dev/toy/test-merge-guard.sh` and grep it
for their own PASS line. All 7 fail on CI (latest full run: v1.0.31, run 43988894761).

The toy sets `HOME` to an empty temp folder, so git has no identity. A GitHub runner can't guess one, so every `git commit -q`
in the toy fails silently: the toy repo never has a commit, the shas it records are empty, and each check runs against the
wrong state. A trace on this PC with the Windows skip removed shows `HEAD` empty at every step. `src/b.txt` is gone from line 67
on, because the move into the wiki is never committed and `reset --hard "$wiki"` has no sha to go back to. The 2026-11-11 PASS
was probably recorded on the Mac, where git guesses an identity from the hostname.

The same trace found a real gap in `lanes_cli.affected`, which CI's regression-pr.yml and merge.py's reach check use. A
deleted file that isn't NO_EFFECT is handled as DELETED (the rows that name it, plus the runners) and the loop `continue`s
before setting `real`. So a deletion never reaches the root runners, while a modified or unmapped file does. With
`src/b.txt` deleted, `affected src/b.txt` gives `1 of 3 (tb)`, not `(tb, tc)`.

## Approaches
1. **Give this toy a git identity, and count a deletion as a real change.** Export `GIT_AUTHOR_*` and `GIT_COMMITTER_*` in
   test-merge-guard.sh after it moves `HOME`, as `make.sh` and other toys already do with `git config` or `git -c`. Set
   `real = True` in `affected`'s DELETED branch: that branch only takes paths that aren't NO_EFFECT. Add a toy check that
   deleting a real file reaches the root runner and deleting VERSION still reaches none. Cost: a few lines. Risk: none
   outside this toy and this function.
2. **Set the identity once in `dev/toy/reap.sh` for every toy.** This might also fix other CI failures under #4516, but it
   changes 100+ toys at once, including any toy that tests a missing identity. Leave it for a follow-up with its own evidence.

## Chosen
Approach 1, plus a ship-time backlog item for approach 2. 32 toys move HOME without setting an identity, and some may fail on
CI for the same reason.

## What each done line needs
1. The 7 rows pass on CI: the toy commits for real. CI evidence is the PR's affected-rows run (regression-pr.yml), which
   runs the rows the change reaches, test-merge-guard.sh among them. The toy is skipped on Windows (no `# windows: ok`).
   Locally, a temporary copy with the skip marker removed shows the commits landing and line 84 passing.
2. In `lanes_cli.affected`, a deletion that isn't NO_EFFECT is a real change, so the root runners still run, and a
   NO_EFFECT-only change still reaches none. New toy checks cover both, plus the existing line-84 check.

## Open questions
None for the owner.
