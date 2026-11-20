# kept-fragments: plan

Checked: `audit.relock`, `audit.restamp_own`, `docs.problems`, `prd.REVIEW` (accepts the old marker) exist; `lanekit.prep` calls
`audit.py restamp-own` and then commits dirty pages (so `keep` committing its own file keeps the tree clean).

## Build steps
1. audit.py: add `keep(root, slug, pages)`; replace the three marker writes in `relock` with it; delete the old text.
2. docs.py: in `problems`, extend `seen` with the `git log -G "^<page>\t" -- .loop/kept/` shas.
3. dev/toy/test-docs.sh: cases `kept-order` (three branches, six orders, no conflict, equal check output) and `kept-fresh`
   (fragment makes the page fresh; without it STALE), folded into an existing docs row, seen red.
4. Trim comments in audit.py, docs.py to end each no larger than on main.

## What could break
Pages stamped by the old marker stay fresh (their commit exists). `restamp_own` on a branch with a dirty tree: `commit --only`
takes just the fragment. A merge of two fragment commits is clean (separate files).

## Out of scope
Tests tables, run results, release render, guard, migration, the `Review:` hash line, requirement text.

## Size
Two scripts, one fixture. If audit.py cannot be trimmed enough, the How-to branch moves into the helper that `relock` shares.

PENDING: none
