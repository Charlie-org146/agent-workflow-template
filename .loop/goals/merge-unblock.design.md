# Design: merge-unblock

## Problem

A goal that only changes code or config a Reviewed page maps stales the page (docs.py `problems`: mapped commits since the page's last commit), and clearing it needs a page edit, which on a Reviewed page needs the owner's words (#3867); a comments-only change stales it too (#3122). Merges also stall: `max_merge_rounds` of 3 is too few when main keeps moving, a goal's merge.py can start while another goal's pr lane is mid-run, a worker's commit can land in the main checkout (0f544a31), and a dirty `.loop/regression-runs.tsv` makes the fast-forward fail.

## Approaches

1. A (#3867, #3122): (a) teach `docs.problems` to ignore a mapped commit whose Python AST is unchanged (comments, docstrings only), in a new small module `docfresh.py`; (b) at merge, `wiki.pending` re-stamps a page whose only trouble is STALE through mapped code, with the page's wording (its fingerprints P R N M U) unchanged, by a commit to the page that carries the goal's slug and a line in the reviews log. Alternative: a new owner-words kind, rejected (the owner asked for no words). A change to the wording keeps `LOCKED`.
2. B: `max_merge_rounds` default 3 to 8 in goal.py, health file.py, settings.py, config.json, START.md, README and the wiki/DECISIONS text that says 3. The pr lane's pool ticket stays held from lane start until merge or failure, and merge.py waits on it (WAITING) for a goal whose touches are disjoint. Alternative: a separate lock file, rejected (the pr queue ticket already exists). BASE_MOVED charging stays with budget-fair (#4261): no change in board_log.py.
3. C: govern_hook.decide refuses a worker's git commit run from the main checkout (not a worktree); merge.py stashes a dirty regression-runs.tsv with `git stash push -u -m TAG`, fast-forwards, and applies and drops by sha. Alternative: refuse the merge on a dirty file, rejected (the owner asked it to be handled).

Chosen: the first of each, with new logic in new small files and the over-size scripts kept net-zero (docs.py, audit.py, merge.py, prd.py, settings.py are already above 19,000).

## What each done line needs

- A: docfresh.py (AST-equal check and the re-stamp); a hook in docs.problems and wiki.pending; toy cases: comments-only change not stale (red before), code change re-stamped at merge with the slug logged (red before), wording change still LOCKED.
- B: the number in every place that says 3, and a toy for default 8 and for a started pr lane holding merge.py of a disjoint goal.
- C: a toy that a worker commit in the main checkout is refused (red before), and a toy that merge.py with a dirty regression-runs.tsv fast-forwards and restores it (red before).

## Open questions

- The exact re-stamp edit: a commit that changes only a page-owned marker, not any section text; decided in the plan after reading prd.REVIEW.
- Requirement sub-bullet for A goes under DOC-2 (Documentation); the operation session approves its text first.
