# Plan: settings-ref

Checked against the code: `settings.py reference --write` writes `skills/workflow-setup/references/settings.md` (settings.py:293); `entry.py` reads that file at line 92 for START.md's settings part; `entry.py write` rewrites START.md.

Steps:
1. Regenerate the reference and START.md (done: review_hold, eta_margin_percent, max_regression_rows, max_suite_seconds appear; auto_merge reads the table's wording).
2. Row `settings-reference-fresh` (settings-ref:2): the committed reference equals `settings.py reference`. Seen red with a drifted file.
3. Row `settings-start-fresh` (settings-ref:1): START.md equals `entry.py render`, so it shows today's auto_merge and review_hold lines. Seen red.
4. Render the Tests tables; docs check; regression sync. settings.py stays at 19,133 bytes (unchanged).

What could break: pages Setup and How-to-use-Setup read STALE until re-stamped by operation. Out of scope: other scripts over the cap.
