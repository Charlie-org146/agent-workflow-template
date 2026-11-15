# Design: merge-from-main-checkout (#4020, and #4004's moved exits)

## Problem
merge.py has been run from a goal's own worktree, so the goal's own checker judged the goal, and from a main checkout 7
commits behind origin, which refused a clean goal. HEAD_MOVED and BASE_MOVED exits leave the goal `done`, so its queue
ticket is dropped.

## Approaches
1. One guard `release.where(script)` in release.py (no new file, merge.py has 134 bytes free): it compares the script's
   git common dir with the repo being merged. Same repo and the script is under `<common>/loop/worktrees`: refuse. Same
   repo otherwise: fetch the base and refuse when the checkout is behind. A different repo (a toy, installed skills): no
   check. merge.py calls it; wiki.py calls it for `publish`. A helper in autorelease.py puts a goal refused by a moved
   head or base back to `running` at step `pr`.
2. Refuse by path name alone. Breaks toys that run merge.py from a worktree against a throwaway repo.

## Chosen
Approach 1. docs.py is not guarded: `check` is read-only and workers run it in their worktrees all day; the release
guard on merge.py and wiki.py publish covers the release path.

## Each done line
1. Toy: merge.py (copied into a fake `<common>/loop/worktrees/x/` of a throwaway repo) refuses with RUN_FROM_WORKTREE;
   wiki.py publish likewise.
2. Toy: a throwaway main checkout one commit behind its origin refuses CHECKOUT_BEHIND, printing 1 commit and the
   `git merge --ff-only` command; once fast-forwarded it passes the guard; a script outside the repo is not checked.
3. Toy: HEAD_MOVED and BASE_MOVED leave status running at step pr.
No reviewed wording changes: REL requirements already say the merge runs from the main checkout? Nothing is added to them.
