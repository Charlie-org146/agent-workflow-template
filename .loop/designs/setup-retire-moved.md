# Design: setup-retire-moved

Status: APPROVED (unattended, recommended answers taken; owner records o73, o74)

## Problem
Setup (docs/wiki/Setup.md) still holds 21 live requirements. The v2 rewrite (prd-rewrite-to-10, Setup section) keeps 17 there and moves four to other pages: SET-8 and SET-15 are merged into GRD-3 (Guardrails), SET-17 into HLT-10 (Health), SET-13 into OPS-12 (Operation, with MON-12). Until Setup retires them, criteria_max has to stay at the temporary 21 (o48).

## Premises
1. The four moves are the whole job; no requirement wording changes, no other page changes (Setup page, test-row goal columns if they still cite the old IDs, How-to items, issue links, criteria_max).
2. The new IDs exist only after the two pre-merges (regroup-regression, regroup-guardrails): GRD-3 and HLT-10 and OPS-12 are on regroup-guardrails (and GRD-3 on regroup-regression).
3. The result must have every page at 19 or fewer live requirements on the main it merges into; if any page would exceed 19 the goal stops and reports.

## Approaches
- A (recommended): merge both branches in order, then `criteria.py retire` each of SET-8, SET-13, SET-15, SET-17 on Setup with `--owner-record o74`, point leftover test rows and How-to items at the new IDs, set criteria_max to 19 with owner record o73, re-render generated blocks.
- B: edit Setup.md by hand. Rejected: the revision tooling is the rule and the locks refuse hand edits of Reviewed lines.
- C: keep 21 and retire later. Rejected by the done lines.

## Plan
Merge origin/loop/regroup-regression then origin/loop/regroup-guardrails (no rebase, no force); retire the four; fix citing rows; criteria_max 19 (o73); docs.py check, health size rule, wiki.py prepare; STOP and report if any page is over 19 (Setup 17 after retire; check Guardrails, Delivery, Regression, Documentation, Operation, Health, three-level-ops).

## Risks
- Reviewed lines (SET-13, SET-8, SET-15, SET-17 are Reviewed): retire must go through the tooling with the owner record; criteria.py retire keeps the earlier text as a row.
- Guardrails may hit 19+ once GRD-3 absorbs SET-8/SET-15 and the regroup adds GRD-20..22 (page cap 19; GRD has 22 in the rewrite: this is why caps are the owner's).
- The local 2.0 lane floor must be dropped for START.md renders and put back; never committed.
