# The docs-fixture regression rows pass again on main: their fixtures match today's docs rules

- Slug: known-red-docs
- Touches: not declared
- ETA: 290 active minutes (estimate 232m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Rows prd-copy-no-reader, refused-unmet, settings-render-tables, defect-categories, stale-found, publish-refused-stale and stale-page-row pass: fixtures add the How-to-use page DOC-18 now requires, make a real code change instead of a comment-only one, copy .loop/routines.tsv, and read the automation block from Home.md
2. Row runbook-repo passes by adding the health-round runbook wording Health.md lacks (anthropic_api_key, judge_command, not run on the runner) without changing any requirement text, and row grd1-guardrail-list passes by adding the Guardrail table GRD-1 r2 requires on Guardrails.md, rendered from the existing guardrail list
3. Every row this goal fixes leaves .loop/regression-known.tsv; nothing else changes; net test rows grow by at most 0

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
