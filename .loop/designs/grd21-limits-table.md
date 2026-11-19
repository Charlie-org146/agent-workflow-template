# Design: grd21-limits-table

Status: APPROVED (unattended, recommended answers; owner records o132 depth condensed, TOP-DECISION 60)

## Problem
GRD-21 says one table on the Guardrails how-to states each package limit (Agensi's figure, ours, the date Agensi's page was read), but no table exists and nothing checks that ours is never looser than Agensi's.

## Premises
1. Agensi's own packaging page (agensi.io/docs/packaging, read 2026-11-18) is the source of Agensi's figures; ours come from dev/package.py (MAX_FILES, MAX_BYTES, MAX_SCRIPT, LIMITS).
2. The table goes on docs/wiki/How-to-use-Guardrails.md (DOC-1: no table on a feature page); Guardrails.md is not touched; GRD-21 is not marked Reviewed (a draft r2 is sent, not applied).
3. The check folds into an existing guardrail row's toy so net rows stay 0 and the total stays at 1300 or fewer; dev/package.py's file count is untouched.

## Approach (recommended)
Add the table under "How to reach or run it"; extend dev/toy/test-package-caps.py (row package-caps-held) with a parser of that table: it fails when the table is missing, a numeric row's ours is larger than Agensi's (units MB and KB as binary, as dev/package.py uses them), or the files and size rows differ from package.MAX_FILES and MAX_BYTES; a negative control feeds it a table whose ours is looser.

## Risks
Agensi's "5 MB" and "20 KB" carry no stated unit and the page does not say whether 5 MB is per file or total; ours use binary multiples (5,242,880 and 20,480 bytes), which is looser than decimal MB and KB by 4.9% and 2.4%: stated in the table and sent to the owner.
