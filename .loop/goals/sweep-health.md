# Sweep the auto-filed health issues on main: close each whose finding no longer appears, with the passing line as proof, and group the rest by cause on one tracking issue

- Slug: sweep-health
- Touches: docs, .loop

## Done lines

Frozen. A wrong done line needs a new goal.

1. Health's own check runs on current main, and every health issue whose finding no longer appears is closed through health's own re-check or close path with the passing line as proof
2. Each finding that still appears is grouped by cause in one summary comment on a new tracking issue, naming which are expected to close with scripts-b and scripts-c
3. Nothing is mailed, no digest is posted, no finding is fixed, and the Regression: issues are left alone
4. The report gives the counts: closed, still open by group, and expected to close with scripts-b and scripts-c

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
