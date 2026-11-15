# Design: audit-pr-head

## Problem

merge.py's wiki check (wiki.pending) audits the main checkout's tree, so a pull request that rewrites a page main left stale is refused even though its head passes (#4208). And `goal.py new` in an app worker session leaves the goal unbound until someone runs `sessions.py bind` (#4257).

## Approaches

1. #4208: audit the PR head from a temporary worktree (`git worktree add --detach`), judging stale pages by the head's tree. Cost: one function change in wiki.py; risk: a worktree to clean up. Alternative: `git show` per file, rejected (docs.py needs a tree).
2. #4257: `goal.py new` calls `sessions.py bind SLUG self` when CLAUDE_CODE_HOST_SESSION_ID is set. Alternative: bind in-process by importing sessions.py, rejected (delivery stays standalone).

Chosen: the first of each.

## What each done line needs

- #4208: `wiki.pending(top, cfg, head=origin/branch)` audits and runs `check --own` in the temporary worktree; toy cases for a PR that fixes a stale page (passes) and one that stales a page (refused).
- #4257: `fit.bind_here` (fit.py, room made by trimming two comments in goal.py and a note in fit.py); toy cases inside and outside an app session.

## Open questions

None.
