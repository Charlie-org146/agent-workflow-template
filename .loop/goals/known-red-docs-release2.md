# One PR carries known-red-docs and known-red-release (re-frozen from known-red-docs-release, whose done line wrongly forbade the owner-approved GRD-1 r3), folded under TOP-DECISION 72's rule (owner: "No waivers u can do it").

- Slug: known-red-docs-release2
- Touches: not declared
- ETA: 270 active minutes (estimate 216m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Rows prd-copy-no-reader, refused-unmet, settings-render-tables, defect-categories, stale-found, publish-refused-stale, stale-page-row, runbook-repo and grd1-guardrail-list pass
2. Rows release-criteria-known-skip, auto-release, rel-major-refused, no-token-would, issue-129-docs-published and skill-refusals-in-references pass on today's main (rel-major-refused after known-red-size lands)
3. The only requirement text change is GRD-1 r3 (the generated guardrail list lives on How-to-use-Guardrails), approved by the owner (records o119 and o123, TOP-DECISION 44); every row this goal fixes leaves .loop/regression-known.tsv; net test rows grow by at most 0

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
