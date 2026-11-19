# The regression row operate-all (dev/toy/test-operate.sh) passes on main again: its 'OPS-1 carries the v2 wording' check still greps the pre-consolidation OPS-1 line (Unreviewed, 'One command starts the operation session'), which requirements-consolidate (#5268, v1.0.90) reworded and Reviewed; the check follows the page (owner o355 gap scope; regression from v1.0.90).

- Slug: operate-all-fix
- Touches: not declared
- ETA: 275 active minutes (estimate 219m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. operate-all passes on the merged result, locally and in a targeted regression.yml run: the OPS-1 check asserts the consolidated OPS-1 line and its revision as they now stand on the Operation page, never loosened, and a negative control shows a missing or wrong OPS-1 line still fails
2. Every other toy and row that greps a reworded or retired requirement line from before v1.0.90 is checked and fixed the same way, or listed if none; no product code changes, no new file, net regression rows 0 or fewer

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
