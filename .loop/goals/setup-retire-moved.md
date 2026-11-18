# Setup holds only its own requirements again: the rows regroup-delivery moved to other pages are retired on Setup as moved, and criteria_max goes back from the temporary 21 to 19

- Slug: setup-retire-moved
- Touches: not declared
- ETA: 290 active minutes (estimate 232m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Every Setup requirement that regroup-delivery moved to another page is retired on Setup through the revision tooling as moved to its new ID, with test rows, issue links and How-to items already pointing at the new IDs; no requirement wording changes
2. criteria_max in .loop/config.json is exactly 19 (from the temporary 21 under o48), and the docs and health checks pass with every page at 19 or fewer live requirements on the main it merges into, three-level-ops included; if any page would exceed 19, the goal stops and reports instead of keeping 21
3. Nothing else changes, and the net test-row count is zero

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
