# v2-health-green plan

Checked against the code: `skills/workflow-health/scripts/defects.py` holds `defined()` (reads `- ID:` lines under `## Requirements`), `refs()` (flags every page ID of a live prefix that is not defined) and `FUNCTIONS`/`CONTROLS` with `f_refs`; the v2 revision format keeps retired IDs in `## Revisions` under `### Retired` as `- ID: moved to X`, which `defined()` never reads. `skills/workflow-monitoring/SKILL.md` has a `## Statuses` table and `skills/workflow-release/SKILL.md` an `## A major` paragraph, both movable to `references/commands.md`. `.loop/regression.tsv` rows `quiet-plain-import-4892`, `depth-on-board`, `depth-in-pr-body` and `depth-reference` exist; `max_regression_rows` is 1300 and the table holds 1300 rows.

## Build steps
1. defects.py: add `retired(root)` and use it in `refs()` only (ids-unique and row-requirement stay strict); prefixes still come from live IDs.
2. dev/toy/test-health-repo-rules.py, case `run`: a repo with a Retired marker, one retired ID named on another page (must not fail) and one undefined ID (must fail refs). Row repo-rules-run already runs that case.
3. Repoint real references at their source: regression.tsv descriptions, How-to-use-Documentation examples, the Regression runbook line, Home's Guardrails line. Leave revision-history rows and the generated Roadmap rows.
4. Re-point quiet-plain-import-4892 to GRD-20; add depth-marker-rows-4557 (defect, link #4557); drop the exact-duplicate row aut-regression-off-written to keep the rows cap.
5. Move the monitoring Statuses table and the release "A major" paragraph to references/commands.md, leaving a pointer.
6. config: criteria_max 23, max_suite_seconds 2800; render, entry.py write.
7. Prove: health.py check prints HEALTH: green; repo-rules-run seen red with the old defects.py.

## Test per done line
1. repo-rules-run (seen red with defects.py from main, passing after) and the health refs count (32 to 0). 2. depth-marker-rows-4557 plus the repointed quiet-plain-import-4892; the new row's red proof needs a non-Windows runner (its toy exits 77 here). 3. skill-lines-release-4172 and skill-refusals-in-references. 4. health.py check. 5. row count: +1 -1.

## What could break
A retired ID typed into a Retired list by mistake would hide a dangling reference. Toys that grep the two SKILL.md files (test-delivery-release.sh, test-batch.sh, test-board.sh) read text I moved: the lane reruns them.

## Out of scope
Rewriting GitHub issue titles quoted in the generated Roadmap page; editing revision-history rows; the v2.1 work (suite speed, merging requirements back to 19 per page) beyond filing its two issues.

PENDING: seen-red proof for depth-marker-rows-4557 from a non-Windows runner (operation-pc arranging the Mac)
