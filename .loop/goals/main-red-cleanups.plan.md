# Plan: main-red-cleanups

Checked: dev/render_tables_check.py (main, pages list), dev/toy/test-runbook.sh (case_repo need dict), .loop/regression-known.tsv lines for both rows, Health.md health-round runbook all exist and match the design.

Steps
1. render_tables_check.py: pages = Home.md only; messages and docstring say so.
2. test-runbook.sh: health-round need words become feature_labels and claude (the runbook is Mac-only, claude login).
3. Remove the two known-row lines.
4. Comment on #4120 and #5043 linking each other.

Tests: rows settings-render-tables and runbook-repo (existing, no rows added): both red before (no automation row in README; missing words), green after (run locally: OK / ALL PASS).

Could break: nothing else reads these two files; regression.tsv rows unchanged.
Out of scope: README, Health.md text, reply-hook rows.
