# review.py gate accepts a real green health verdict: check_health parses the counted 'HEALTH: green (N pass, N warn, 0 fail, 0 unread)' line instead of requiring the bare string, so the v2.0 gate can pass when health is green (TOP-DECISION 85).

- Slug: gate-health-verdict
- Touches: not declared
- ETA: 275 active minutes (estimate 219m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. check_health accepts a verdict that starts with exactly 'HEALTH: green' and whose counts show 0 fail and 0 unread, and refuses anything else
2. A toy case feeds the real counted verdict format and passes, with negative controls for 'HEALTH: not green (...)' and for a counted verdict with fail > 0; only review.py and that toy change
3. Net regression rows are 0 or fewer, nothing is added to .loop/regression-known.tsv, and review.py stays under its size caps

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
