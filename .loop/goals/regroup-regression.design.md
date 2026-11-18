# regroup-regression: design

## Problem
The v2 rewrite draft (prd-rewrite-to-10.md) rewords the Regression (16), Automation (9), Documentation (19) and Integrations (8)
requirements and moves some between pages. The pages are Reviewed, so every change must go through the revision tooling of
prd-revisions (`criteria.py revise|retire|migrate`, owner record o155) and keep each old text as a numbered revision.

## Mapping (draft ID -> action on the repo)
- Regression: REG-1..REG-10 are revised in place (same meaning). REG-11, REG-12, REG-13, REG-14, REG-15, REG-16 are new IDs on
  the page, free numbers. REG-14 and the second source of REG-10 come from GRD-13 and GRD-11, which sit on Guardrails, outside
  these four features: they are retired there by the guardrails goal, not here.
- Automation: AUT-1..AUT-7 and AUT-9 revised in place; AUT-8 (runbooks) retired as moved to DOC-16, which already carries the
  runbook rule; AUT-10 is new.
- Documentation: DOC-1, 2, 3, 4, 6, 9, 10, 11, 12, 13, 14, 16, 19 revised; DOC-20 and DOC-22 already exist (added by
  prd-revisions) with the draft's meaning, so they are revised, not renumbered; DOC-21 is new; DOC-7 retired as merged into DOC-1;
  DOC-17 retired as moved to INT-3 (its tests follow). DOC-15, DOC-18 and DOC-23 are left alone for prd-principles.
- Integrations: new page with INT-1..INT-8, a How-to-use-Integrations page, and a Home row.
- Rows: regression.tsv rows whose goal column cites DOC-7 (4), DOC-17 (43) or AUT-8 (3) are re-pointed to DOC-1, INT-3 and
  DOC-16, and the Tests tables re-render. How-to items for moved IDs move to the new page or ID.

## Approaches
1. Script the draft: parse the four tables and call the tooling per requirement, then hand-fix placement and how-to items.
   Cost: one script and a review of its output. Risk: low, each call is the tooling's own and refuses wrongly.
2. Hand-edit the pages. Risk: hand edits bypass the guard and the seals.
Chosen: 1, a throwaway script outside the repo.

## What each done line needs
- a: every draft requirement present as a new revision, Integrations page added, moves retired; guard OK.
- b: rows, How-to items, Home updated; docs check and health still pass; old IDs resolve through moved-to markers.
- c: Tests re-render, zero rows added net, rows for new rules seen failing and passing, wiki.py prepare clean, ENTRY OK.
- d: no shipped file added, no script grows, only the four pages (with their How-to pages), Home and Tests change.

## Open questions
- Detail cut from long bullets stays in each requirement's r1 row; it is not copied to How-to here (follow-up).
- REL-13 is not on main's Release page yet, so the DOC-10 release-note rows cannot be linked to it by this goal.
- A new page needs a `.loop/docs.tsv` row if the check demands one; that file is outside the declared touches.
