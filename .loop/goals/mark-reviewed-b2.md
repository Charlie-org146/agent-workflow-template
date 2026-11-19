# The Setup and Documentation requirements the owner reviewed for v2.0 are marked Reviewed through the revision tooling, citing the owner's words that name them

- Slug: mark-reviewed-b2
- Touches: not declared
- ETA: 290 active minutes (estimate 231m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. The 16 Setup and 18 Documentation requirements are marked Reviewed through criteria.py review citing the owner's record of "reviewed Setup and Documentation; approve GRD-1 r3 and MCH-5 r2", which names every ID
2. Review marks and seals only: no requirement text changes, zero net test rows, docs check prints DOCS OK, and review.py gate v2 --no-suite shows the reviews refusal count dropped by exactly the number marked
3. Nothing else changes

## Verify by hand

1. Run `python3 skills/workflow-docs/scripts/docs.py check`.
   Expect: it prints DOCS OK: 16 pages.
2. Run `python3 skills/workflow-release/scripts/review.py gate v2 --no-suite --ref HEAD` and count its GATE REFUSED lines.
   Expect: 122 lines, none naming a Setup or Documentation requirement (156 before).
3. Run `git diff main -- docs/wiki` and read it.
   Expect: 34 lines changed in Setup.md and Documentation.md, each only swapping Unreviewed for Reviewed 2026-11-19 plus its seal; no wording changes.
