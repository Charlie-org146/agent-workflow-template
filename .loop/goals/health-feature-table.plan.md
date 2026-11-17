# Plan: health-feature-table

Checked against the code (all exist): `report.build`, `report.rule_of`, `report.TITLE`/`ORDER`, `report.plan_for`,
`report.cmd_file` (skills/workflow-health/scripts/report.py); `health.cmd_check` (health.py); `issues.feature_of`,
`issues.fetch` / `CACHE` (scope `health`, already read by `rules.finding_age` in a full check), `issues.key_of`,
`issues.feature_label`, `issues.feature_labels_on`, `issues.NO_FEATURE` (issues.py); `file.plan` (`tagging`), `file.FOUND`,
`file.REPORT_ONLY`, `file.held_all` (file.py); `automation.compose` / `cmd_digest` / `health_line` (automation.py);
`workflows` tick steps `health check` → `health file` → digest (workflows.py).

Correction to the design: check runs before file in the tick, so check's table can only name issues that were open
before this round. `health.py file` therefore prints the same table after filing (issue list read again), the tick
appends file's output to the saved report, and the digest shows the last FINDINGS table in it.

## Build steps

1. `table.py` (new, workflow-health/scripts): `rows_of(rows, root, issues)`, `lines(rows, root, issues)`, `insert(text,
   rows, root)`, `show(rows, root)` (after file: drop the cached health list, read it again, print), `from_report(text)`.
   Issue: `#N` of the open health issue whose `loop-health` marker key is the finding's key (or a legacy key);
   `report only` for a REPORT_ONLY rule; `not filed`; `not read` when no list was read. Feature: page or `Other`.
   Mine rows: finding text "details stay local".
2. `health.py cmd_check`: `insert` the table after the header (text mode only; --json unchanged).
3. `report.py`: `plan_for` keeps the rows it gathered on the file module; `cmd_file` prints `table.show` after apply.
   Trim the module docstring to stay under 19,000 bytes.
4. `workflows.py` tick: append `health file`'s output to the saved report. Trim to stay under the cap.
5. `automation.py`: `compose` adds `### Findings` with `table.from_report` of HEALTH_REPORT, `#N` linked when open;
   `No feature` sections titled `Other`.
6. `file.py plan`: feature always `IS.feature_label(page or "Other")`; drop `feature_labels_on` use (and the helper in
   issues.py if nothing else uses it). Docstring: always tagged.
7. `settings.py` text for `feature_labels`: regression issues only; health issues always carry it. Re-render START.md,
   Home and README (`entry.py write`, `/workflow-docs render`).
8. Tests: new `dev/toy/test-health-table.sh` (done lines 1 and 2); update the health-side "off by default" assertions in
   test-milestones.sh, test-health-prd.sh, test-health-repeat.py, test-automation-email.sh. Two regression rows
   (`health-findings-table` on HLT-3, `health-feature-always` on HLT-4), `regression.py red` on the old code.
9. Pages: HLT-3, HLT-4 text (unreview with operation-pc's owner records, never review), How-to-use-Health, Tests rows.

## Tests per done line

1. `test-health-table.sh`: findings in size, docs, hygiene, requirements; check prints `FINDINGS (N)` and the
   six-column header; every row's Feature is `Calc` or `Other`; digest dry run with HEALTH_REPORT shows the same rows
   under `### Findings`. Red on old code: no FINDINGS line.
2. Same script: `health.py file --group size,docs` with feature_labels false: `--label feature:Other` and
   `feature:Calc` on the create calls, labels made first. Red on old code: no feature label call.
3. Docs check on the Health page; criteria state left unreviewed; Tests rows render.

## What could break

- Tests grepping exact check output line counts (`grep -c`) or `tail`: the table adds lines in the middle only.
- Toy tests asserting no feature label when off (listed in step 8).
- The digest's 65,536-character comment limit with many findings: cap the table at 50 rows plus a "N more" line.
- Script sizes: report.py, file.py, workflows.py, issues.py near the cap: measure with `git ls-tree -l` after each.

## Out of scope

- Removing the per-group finding lines (approach 1).
- Regression issues' feature labels (still behind feature_labels).

DEPTH: full
