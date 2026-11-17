# apply-rerender plan

Checked against the code: `operate.apply`, `operate.wiki_only`, `audit.relock`/`restamp` dispatch, `criteria.py render`, `counting.BLOCK`, merge.py's call at line 272 and its wiki-only head check at line 288 all exist as read.

## Build steps
1. audit.py: `regions`, `rerender(root, base)` and the `rerender BASE` command.
2. operate.py: `apply` runs rerender first, re-reads STALE pages, restamps, stages the wiki folder and README.md, commits "Wiki: re-render and re-stamp pages"; `wiki_only` accepts README.md blocks-only via `readme_blocks_only`.
3. Toy `dev/toy/test-apply-rerender.py` and rows apply-rerender-blocks, -hand-edit, -accepted, -tables, each seen red; the How-to-use leg and row after how-to-use-docs merges.
4. Docs: Documentation and Tests re-rendered, the commands and operation references, DECISIONS.

## Tests per done line
1. blocks: pushed commit, wiki-only accepted, no STALE; hand edit: nothing pushed, still STALE; tables.
2. How-to-use: one apply run re-stamps How-to-use-Engine (kept marker), STALE clears, head accepted.

## What could break
A file the render also rewrites outside its generated part is put back, not committed. Scripts: audit 17.5k, operate 19.9k.

## Out of scope
checkin.py, auto.py, replan.py, pool.py (trim-monitoring-4 owns them); the worker-side render in goal.py pr.
