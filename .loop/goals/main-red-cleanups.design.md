# Design: main-red-cleanups

Problem: settings-render-tables reads README.md for an automation row that moved to Home.md when the README became principles-only; runbook-repo wants anthropic_api_key, judge_command and "not run on the runner" in Health's health-round runbook, which now (correctly) says the round runs only on the Mac with its own claude login.

Approaches: (A) edit the check and the toy to match the pages as they are; (B) rewrite the pages to carry the old words. B would make the runbook false (no GitHub Actions health run exists), so A.

Chosen: A. render_tables_check.py uses Home.md only. test-runbook.sh's health-round words become feature_labels and claude. Both known-row lines are removed. #4120 and #5043 are cross-linked by comment.

Done lines: 1 needs both rows green and the two known rows gone; 2 needs only these files to change, net rows zero.

Open questions: none.
