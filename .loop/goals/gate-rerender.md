# merge.py's wiki gate counts a page it re-renders itself (a regenerated Tests table) as untouched, so an adopting repo's goal is refused only for findings on pages its own diff changes (owner o56; extends REL-9 from docs-gate-scope)

- Slug: gate-rerender
- Touches: not declared
- ETA: 300 active minutes (estimate 237m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given an adopting repo whose goal diff changes five wiki pages while other pages carry DOC-19 or DOC-4 findings, when merge.py re-renders those other pages' Tests tables during the merge, then it does not refuse on their findings; it files them per page as REL-9 already does for untouched pages, and the merge goes ahead.
2. Given a page this goal's diff really changes, or a stale generated table merge.py cannot re-render, when merge.py checks the wiki, then it still refuses exactly as before.
3. Given the change, when it merges, then REL-9's text says re-rendered-only pages count as untouched, through the revision tooling; one test row is seen failing and passing with zero rows added net; no shipped file is added and no script crosses a size line it was under on main.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
