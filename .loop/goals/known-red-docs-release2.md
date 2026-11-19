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

1. Run `python3 dev/toy/test-release-criteria.py` and `bash dev/toy/test-autorelease.sh`.
   Expect: the first prints six PASS lines and exits 0; the second ends with ALL PASS.
2. Run `bash dev/toy/test-defect.sh categories` and `grep -c "^| Guardrail" docs/wiki/How-to-use-Guardrails.md`.
   Expect: the first exits 0 (on the committed config, not the local memory floor); the second prints 1.
3. Open docs/wiki/Guardrails.md and find GRD-1.
   Expect: its newest revision is r3, saying the guardrail list lives on How-to-use-Guardrails; no other requirement text on the branch changed.
4. Run `python3 dev/toy/test-release-gate.py major`.
   Expect: every check passes, including "the Release page holds REL-1 to REL-14"; the checkin.py size check passes once known-red-size has trimmed checkin.py.
5. Run `grep -cE "^(prd-copy-no-reader|refused-unmet|settings-render-tables|defect-categories|stale-found|publish-refused-stale|stale-page-row|runbook-repo|grd1-guardrail-list|release-criteria-known-skip|auto-release|rel-major-refused|no-token-would|issue-129-docs-published|skill-refusals-in-references)\t" .loop/regression-known.tsv`.
   Expect: 0 once rel-major-refused has left the known list after known-red-size; 1 before that.

