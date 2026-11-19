# Plan: setup-retire-rows (condensed review)

1. Pre-merge, in order, no rebase, no force: origin/loop/regroup-regression, then origin/loop/regroup-guardrails; then origin/main again. Drop the local lane floor before any render and put it back.
2. On Setup, `criteria.py retire` SET-8 -> GRD-3, SET-15 -> GRD-3, SET-17 -> HLT-10, SET-13 -> OPS-12 with owner record o89.
3. Repoint rows and items: regression.tsv goal columns, How-to items and issue links that still cite SET-8/13/15/17 (net rows zero).
4. criteria_max stays as main has it (21; v2-health-green sets it, TOP-DECISION 37); regenerate START.md (floor shows its committed value).
5. Verify: docs.py check, health size rule, wiki.py prepare, entry.py check, `criteria.py guard`; count live requirements per page (all <= 19) else STOP and report.
Review: docs/config only; risks are the Reviewed locks and a page over 19.
