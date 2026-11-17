# apply-rerender design

## Problem
`merge.py` runs `operate.py apply` before it merges: it re-stamps pages stale only through mapped code, in one wiki-only commit it pushes to the goal's branch. Generated blocks (README and Home Settings, Automation and template blocks, the Tests page, each page's Tests table) are not covered, so when the template, main or a regression row moves, each open branch is refused STALE until its worker re-renders by hand (#4632: ci-fail-causes, how-to-use-docs, operator-setup this morning).

## Approaches
1. **Re-render in apply, with a hand-edit guard** (chosen). `audit.py rerender BASE` runs `criteria.py render` in the branch checkout and keeps each changed file only when (1) the branch added no line to its generated part that the fresh render lacks (against the merge-base) and (2) the render touched nothing outside that part. A hand edit fails (1) and the file is put back. `operate.apply` runs it before the re-stamp and commits both in one commit; `operate.wiki_only` also accepts README.md when only its generated blocks changed. Cost: about 45 lines in audit.py, 15 in operate.py. Risk: a branch whose own block line was reworded on main since is left stale.
2. Re-render everything and trust it. A hand edit inside a block would be overwritten silently; the negative control forbids it.
3. Re-render at the lane. Needs a worker step again.

The How-to-use re-stamp is already `audit.py restamp` (goal how-to-use-docs, DOC-18); apply passes it every STALE page, so the same run re-stamps a How-to-use page.

## What each done line needs
1. A fixture branch whose README Settings block is stale because main's was rendered by an older template: apply pushes one commit, operate.py wiki-only accepts it, check --own is clean; a hand edit inside the block is left alone and still STALE; a new regression row's Tests tables are re-rendered (rows apply-rerender-blocks, -hand-edit, -accepted, -tables).
2. The same toy carries a How-to-use-Engine page made stale by a real code change; one apply run re-stamps it (row apply-rerender-howto).

## Open questions
None for the owner. Done line 2 needs how-to-use-docs on main (its audit.py restamp); the leg is added after it merges.
