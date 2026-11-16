# Plan: start-from-head

Checked: wiki.py `pending(top, cfg, fix, head)` builds the temp tree and calls release.docs_trouble(tree, base, whole=True), which runs main's docs.py audit; entry.problems uses main's skills (entry.SKILLS) so START.md differs for a head with new commands.

Build: 1. wiki.py `own_entry(tree, lines)`: when tree is a temp head tree and has skills/workflow-docs/scripts/entry.py, run `entry.py check --repo tree`, drop the audit's "(entry.py write)" lines and add one "WOULD FIX <path>: regenerate it (entry.py write)" per STALE or MISSING path it reports (not marker trouble). 2. Net-negative bytes in wiki.py (docstrings shortened). 3. dev/toy/test-audit-pr-head.py gets a `start` scenario: a throwaway repo with a copy of workflow-docs; branch adds-command (head START.md rendered by its own entry) passes, branch stale-start (old START.md) is refused. 4. Rows start-from-head-passes-4340 and start-from-head-refuses-4340, each seen red by breaking own_entry in a HEAD copy. 5. Re-render Tests, docs check.
Could break: the agent-block lines (same helper); a head without entry.py keeps today's behaviour. test-merge-main-own.py's last case fails on origin/main too (pre-existing).
Out of scope: other audits, installed skills. No owner decisions.
