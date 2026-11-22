# The generated regression workflow writes, reopens, comments on and closes regression issues only on a run of the default branch; any other ref prints what it would do and writes nothing (fixes #5773, SAFETY)

- Slug: regression-issues-main-only
- Touches: skills/workflow-regression/scripts/actions.py, .github/workflows/regression.yml, dev/toy, .loop/regression.tsv, docs
- ETA: 315 active minutes (estimate 251m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a regression.yml rendered by actions.py, when the row step starts, then it reads the default branch at runtime (gh api repos/{owner}/{repo} --jq .default_branch) and passes --live to the issue script only if github.ref is refs/heads/ plus that name, and fails closed with no --live if the default branch can't be read
2. Given a run on refs/pull/N/merge, a feature branch, a tag or any other non-default ref, when rows fail or a regression issue's row is green, then no --live is passed, the log prints the file, reopen, comment or close it would do, label creation sits inside the dry-run, and no gh api write (POST, PATCH) is issued; read calls still run
3. Given a schedule run, a dispatch on the default branch and a dispatch on a feature branch with a fake gh on PATH, when the toy runs the rendered step on each, then writes happen only on the default-branch runs and the schedule run (negative control: the default branch still files, reopens, comments and closes)
4. Given the change, then regression.yml equals the generator's re-rendered output (never edited by hand), actions.py is no larger than main in LF bytes, net regression rows are 0 or fewer, checks stay green (docs, package, private-name) and no existing row turns red

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
