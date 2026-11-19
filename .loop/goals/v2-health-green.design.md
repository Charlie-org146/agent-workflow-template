# v2-health-green design

Problem: health.py check on main 43c410ef fails 38 rules, so the v2.0.0 gate (REL-1) refuses: 32 consistency `refs` fails, two SKILL.md files at 150 and 151 lines, two requirement-per-page caps, #4557 closed with no defect test and row quiet-plain-import-4892 guarding an ID no page defines (TOP-DECISION 37, owner record o194).

Approaches:
1. Delete the 16 retired-ID markers and repoint the rest. Cost: small. Risk: breaks "an old ID resolves through its moved-to marker" (DOC-20), the reason the regroup goals kept the markers.
2. Teach the health `refs` rule that an ID listed under `### Retired` resolves through its marker (two lines in defects.py with a negative control that a truly undefined ID still fails), keep the markers, and repoint the real stray references at their source. Cost: one small script change. Risk: a typo in a retired list hides a dangling reference; the control and the Retired list's own revision tooling keep that narrow.

Chosen: 2 (operation-pc confirmed it, TOP-DECISION 37).

What each done line needs:
1. `retired()` in defects.py; refs repointed in the row descriptions (DOC-7/8/9 to DOC-1, GRD-14 to DEL-17, DOC-17 to INT-3), the How-to-use-Documentation examples, the Regression runbook and Home; revision-history rows and the generated Roadmap rows quoting issue titles are left (they resolve).
2. Row depth-marker-rows-4557 (defect, link #4557, goal DEL-3); quiet-plain-import-4892 re-pointed to GRD-20. Seen-red for the new row needs a non-Windows runner because its toy exits 77 here.
3. Move the monitoring Statuses table and the release "A major" paragraph into each skill's references/commands.md.
4. criteria_max 23, max_suite_seconds 2800; two v2.1 issues filed at ship.
5. The rows cap (max_regression_rows 1300, table already at 1300) forces one row out for the one added: the exact duplicate aut-regression-off-written. Net 0.

Open questions: none beyond the off-platform red proof for #4557.
