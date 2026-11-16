# Regression sweep, 2026-11-15

Every open "Regression: <row>" issue was rerun one row at a time with `regression.py run ROW --live`. Tracking issue: #4564, with one summary comment grouping every row.

| Group | Rows | What was done |
|---|---|---|
| Passing | 6 | 4 issues closed with the pass line (merge-failed-retry, health-mail-env-windows, scripts-a-monitoring-under-19000, scripts-a-delivery-under-19000); docs-block-split had no open issue; review-findings-skill-lines passes on main and its issue is already closed |
| Real defect | 0 | none |
| Needs Linux or Mac | 106 | bash toys that exit 77 on native Windows; issues moved to Backlog: Regression |
| Known Windows-only, flaky, stale | 0 | none seen |
| Leaks into the home folder on Windows | 5 | the `dev/toy/test-settings.sh` rows (settings-reference, setup-both-halves, parallel-unlimited, settings-read-fresh, criteria-max-setting) were not run; see #4393 |

The sweep also added the REST fallback to the issue read (#4464): the GraphQL issue list times out on this repo's history, so a local `run --live` reads 100 issues a page over REST before it gives up. Nothing else was fixed.
