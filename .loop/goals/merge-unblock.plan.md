# Plan: merge-unblock

Checked against the code: `docs.problems` (docs.py:164), `audit.relock`/`owned` (audit.py), `prd.REVIEW`/`set_review` (prd.py), `wiki.pending`/`where` (wiki.py), merge.py's stale check, `wiki_only` and `--match-head-commit tested`, `goal.round_stop` (goal.py:442), `pool.pr_turn`/`pr_order` and `graph.merge_lock`, `govern_hook.decide` all exist as named.

## Build steps

1. New `skills/workflow-docs/scripts/docfresh.py`: `same_tree(root, old, new, path)` (Python files parse to the same AST dump, so comments and docstring-only edits count as no change; other file types compare bytes) and `restamp(root, slug)` (a Reviewed page whose fingerprints P R N M U all hold and whose only trouble is STALE gets `<!-- kept SLUG -->` on its Review line, and one `restamp` row in the reviews log with the slug). `prd.REVIEW` accepts the optional kept marker. A: `docs.problems` skips a mapped commit whose changed files are all `same_tree` (#3122), a one-line hook.
2. New `skills/workflow-release/scripts/restamp.py`: `wiki_only` moves here from merge.py, plus `apply(top, cfg, state, head)`: in a temporary worktree of the goal branch run `docfresh.restamp`, commit "Wiki: re-stamp pages for SLUG", push, return the new head; merge.py takes it as `tested` (the existing wiki-only path), so merge.py shrinks. A wording change stays LOCKED (not restampable).
3. B: `max_merge_rounds` 3 to 8 in goal.py `round_stop`, health file.py, settings.py row, `.loop/config.json`, START.md, README, the wiki and reference pages that say 3, DECISIONS.md; test-budget-enforce asserts 8. New `skills/workflow-monitoring/scripts/slot.py`: the pr slot (`<loop>/pr-slot`, the slug and a heartbeat): taken when goal.py pr's lane starts (its turn), freed when merge.py merges or fails or the goal ends, expiring after LOOP_MERGE_LOCK_SECONDS silent; merge.py of another goal prints WAITING and waits while another live slug holds it. No change in board_log.py (budget-fair owns BASE_MOVED charging).
4. C: `govern_hook.decide`: a bound worker session (not operation) running `git commit` with cwd the main checkout (not under loop/worktrees) is refused; `wiki.where` fast-forwards a checkout that is only behind, stashing a dirty `.loop/regression-runs.tsv` (`git stash push -u -m TAG` then apply by sha and drop), and still refuses a checkout with any other local change or commit.
5. Toys (each seen red first, rows in regression.tsv): `dev/toy/test-merge-unblock.py` with cases `comments`, `restamp`, `locked`, `rounds`, `slot`, `hook`, `ff`.
6. The sub-bullet for A under DOC-2 (Documentation) once the operation session OKs its text; Tests tables re-rendered; goal file Verify by hand, Closes #3867, #3122.

## Tests per done line

- A: `comments` (comments-only mapped change leaves the page fresh), `restamp` (code change re-stamped at merge with the slug in the log, no owner words), `locked` (a wording change still LOCKED).
- B: `rounds` (default 8 in config and shipped default), `slot` (a started pr lane makes a disjoint goal's merge wait; freed on merge or failure).
- C: `hook` (worker commit in main refused, in a worktree allowed), `ff` (dirty runs file restored after the fast-forward).

## What could break

Size (docs.py, audit.py, merge.py, prd.py, settings.py already over 19,000: keep each net-zero or smaller), package at 98 files (three new files: 97 total), Windows paths in the toys, the AST compare on non-UTF8 files.

## Out of scope

BASE_MOVED charging (#4261), reviewed requirement wording other than A's sub-bullet and the number 3 to 8.

## PENDING

PENDING: the owner's OK of A's sub-bullet text under DOC-2 (sent to the operation session)
