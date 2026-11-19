# GRD-21's package-limits table exists on How-to-use-Guardrails, with each package limit's Agensi figure, ours and the date Agensi's page was read, and a regression row keeps ours never looser than Agensi's (TOP-DECISION 60).

- Slug: grd21-limits-table
- Touches: not declared
- ETA: 290 active minutes (estimate 230m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. How-to-use-Guardrails holds one package-limits table giving, for each limit, Agensi's figure, ours and the date Agensi's packaging page was read (2026-11-18): at least files 100/100 and size 5 MB per file, plus every other limit agensi.io/docs/packaging states
2. A regression row, folded into an existing guardrail row so net rows are 0 or fewer and the total stays at 1300 or fewer, fails when the table is missing or any of ours is looser than Agensi's, with a negative control
3. A draft GRD-21 r2 that changes only the location clause to How-to-use-Guardrails is sent to the operation for the owner's review, and GRD-21 is not marked Reviewed by this goal

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
