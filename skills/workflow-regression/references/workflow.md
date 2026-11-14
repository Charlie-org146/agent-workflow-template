# workflow-regression workflow

```bash
python3 scripts/regression.py workflow
```

Writes `.github/workflows/regression.yml`: rows run on `regression_cron` (4-hourly by default; `off` drops the schedule), on
`v*` tags and by hand; each failing row's issue is labeled `regression` and `defect`, names what it guards and, with `feature_labels` on, carries its `feature:<Page>` label (no milestone is read, made or set); a failed write fails the step (`FILE_FAILED`). It refuses to replace a workflow it didn't write. The job has 90 minutes. Each row runs in its own process group
with a 15-minute limit, and starts only if that full limit still fits the job's time; a row that doesn't fit is
skipped, reported `SKIPPED`, and fails with an issue. Each row's result is saved as it ends, and a last step that
always runs writes the run summary: one header with totals and the run time, then one table per feature (`tests.py
summary`); if that fails, the plain results still reach the summary. Rows (here too, under `regression.py run`) run with no GitHub token and none of the
runner's own files (`GITHUB_STEP_SUMMARY`, `GITHUB_ENV`, `GITHUB_OUTPUT`, `GITHUB_PATH`, `GITHUB_STATE`) in their
environment, so no row inherits the real summary (this stops accidents, not a hostile row), and the checkout keeps no token in its git config.
