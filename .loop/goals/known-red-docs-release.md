# One PR carries known-red-docs and known-red-release (file-disjoint apart from regression-known.tsv), folded under TOP-DECISION 72's rule to cut merges (owner: "No waivers u can do it").

- Slug: known-red-docs-release
- Touches: not declared
- ETA: 270 active minutes (estimate 215m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Rows prd-copy-no-reader, refused-unmet, settings-render-tables, defect-categories, stale-found, publish-refused-stale, stale-page-row, runbook-repo and grd1-guardrail-list pass (known-red-docs' fixes; grd1-guardrail-list follows GRD-1's current revision on main)
2. Rows release-criteria-known-skip, auto-release, rel-major-refused, no-token-would, issue-129-docs-published and skill-refusals-in-references pass (known-red-release's fixes, on today's main)
3. Every row this goal fixes leaves .loop/regression-known.tsv; no requirement text changes; net test rows grow by at most 0

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
