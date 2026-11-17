# operate.py apply also re-renders generated blocks that differ only from a fresh render, so a goal whose only STALE lines are generated passes merge.py with no worker step (#4632)

- Slug: apply-rerender
- Touches: not declared
- ETA: 205 active minutes (estimate 164m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. On a pushed goal branch whose only docs.py check --own STALE lines are generated blocks (README/Home Settings and Automation, the Tests tables) that differ from a fresh render, operate.py apply re-renders them in one wiki-only commit that merge.py accepts; a hand edit inside a generated block is still refused (negative control).
2. The same apply run also re-stamps a How-to-use-<Feature> page made stale only by its feature's code, and a toy covers both, run through merge.py's real call to operate.py apply.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
