# lane-control-all comes off the known list now that it passes on main (TD449, TD457). Full run 44793505054 on 9cb6d767 passed it, the first pass since v1.0.72 or earlier (known row 50, #4115). Removing a known row only makes the gate stricter; listed for the owner. Close #4115 with the run link once merged.

- Slug: known-lane-control-all
- Touches: .loop
- ETA: 405 active minutes (estimate 321m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given .loop/regression-known.tsv on this branch, then it has no lane-control-all row and every other row is unchanged
2. Given the pull request body, then it links run 44793505054 with lane-control-all PASS, names #4115 and #5561 (the open lane-slot flake), and says removing a known row only makes the gate stricter
3. Given this goal's diff, then only .loop/regression-known.tsv and the goal's record files change, and docs.py check and criteria.py render --check pass

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
