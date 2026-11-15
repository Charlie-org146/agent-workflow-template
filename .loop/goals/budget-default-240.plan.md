# Plan: budget-default-240

Checked against the code: `skills/workflow-setup/scripts/settings.py:58` holds the default (120) in `TABLE`; `.loop/config.json:38` sets 120; `dev/toy/test-budget-enforce.py:154` pins 120; `references/settings.md:40`, `docs/wiki/Home.md:53` and `.loop/START.md:109` are rendered from the table.

Build steps:
1. settings.py default 120 -> 240; config.json 120 -> 240.
2. test-budget-enforce.py: the table check expects 240, and add one new check "the default time budget is 240 minutes" (table and this repo's config both 240).
3. Re-render: `settings.py reference --write`, `criteria.py render`, `entry.py write`, `docs.py check --base origin/main`.
4. Add regression row `grd2-default-240` (land, GRD-2 tie): `python3 dev/toy/test-budget-enforce.py 2>&1 | grep -qF "PASS: the default time budget is 240 minutes"`; commit, then `regression.py red grd2-default-240 --break "<sed 240 -> 120 in settings.py in the HEAD copy>"` so it is seen failing.
5. Existing row grd2-limits-in-settings keeps its text (default list); it passes with 240 since the test is updated.

Could break: any other test pinning 120 (grep found only test-budget-enforce.py and unrelated toy fixtures that set their own config). Docs check may ask a re-stamp of the Guardrails page; covered by o19 with --owner-record.
Out of scope: DECISIONS.md history, token_budget, other defaults, the legacy "120 for new repos" decision text.
No owner decisions left.
