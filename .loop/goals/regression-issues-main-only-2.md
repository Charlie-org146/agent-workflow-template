# The generated regression workflow writes, reopens, comments on and closes regression issues only on a run of the default branch; any other ref prints what it would do and writes nothing (fixes #5773, SAFETY)

- Slug: regression-issues-main-only-2
- Touches: skills/workflow-regression/scripts/actions.py, .github/workflows/regression.yml, dev/toy, .loop/regression.tsv, docs
- ETA: 315 active minutes (estimate 251m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a regression.yml rendered by actions.py, when the row step starts, then it reads the default branch at runtime (gh api repos/{owner}/{repo} --jq .default_branch) and passes --live to the issue script only if github.ref is refs/heads/ plus that name, and fails closed with no --live if the default branch can't be read
2. Given a run on refs/pull/N/merge, a feature branch, a tag or any other non-default ref, when rows fail or a regression issue's row is green, then no --live is passed, the log prints the file, reopen, comment or close it would do, label creation sits inside the dry-run, and no gh api write (POST, PATCH) is issued; read calls still run
3. Given a schedule run, a dispatch on the default branch and a dispatch on a feature branch with a fake gh on PATH, when the toy runs the rendered step on each, then writes happen only on the default-branch runs and the schedule run (negative control: the default branch still files, reopens, comments and closes)
4. net regression rows +1, the defect row for #5773 (TD867)

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
1. In GitHub's Actions tab, start the `regression` workflow from the default branch (the nightly does the same), with target `land`.
   Expect: the "Run the rows" step log has no `DRY RUN` line, and a failing row still gets its issue opened or commented on.
2. Only after step 1, and never on a branch you care about: read the workflow file's "Run the rows" step on the branch you would dispatch from.
   Expect: it holds a `live=` line, a `gh api repos/$GITHUB_REPOSITORY --jq .default_branch` read, and `python3 - $live <<'PY'`; on any non-default ref the log prints `DRY RUN: <ref> is not the default branch (...), nothing is written`.

## PR notes

What this changes: the generated regression workflow (`actions.py`, re-rendered into `.github/workflows/regression.yml`, never edited by hand) now reads the repository's default branch at run time (`gh api repos/$GITHUB_REPOSITORY --jq .default_branch`, one read per shard) and passes `--live` to the issue script only when `$GITHUB_REF` is exactly `refs/heads/<default>`. Any other ref (a feature branch, a tag, a pull ref), an empty read or a failed read gets no `--live`, prints one `DRY RUN` line, and writes nothing, so a dispatch on a branch can no longer open, comment on or close main's regression issues (fixes #5773, SAFETY). Label creation sits inside the dry run because it goes through the same `gh()` wrapper.

Rows: +1, the defect row `defect-5773-issues-default-branch` (seen failing with the gate broken to always set `--live`); top granted +1 under TD867 and this goal's done line 4 says so (the first goal's net-0 line was re-frozen here under TD869). Every other row is net 0: `issues-live-only-ci` stays a criterion row (GRD-5); the toy updates fold into existing toys (test-regression-issues.py holds the new gate cases; test-ci-summary.py, test-regression.sh at two places, test-row-output.py and test-ci-target.sh follow the changed `python3 - $live` line).

Stated limits: a fail-closed unreadable default branch stops nightly filing with one `DRY RUN` log line only; a branch can edit its own workflow file, so the guard protects against mistakes, not intent; whether the first real nightly (schedule run) reads the default branch and sets `--live` is unproven until it runs after the merge; actions.py has no byte slack (18,940 LF bytes, main 18,980); `gh()` still treats every `gh api` as a read, so the toy's fake gh fails on `api -X/-f`; a dry run on a branch still counts `filed` and, in cleanup mode, sleeps its pace per would-be write (follow-up, nothing is written). The new toy fails rather than skips when bash is missing. To fit the bytes the timeout `ps` diagnostic in the row runner was dropped (no row asserted it); the Windows taskkill branch stays.

Depth: idea and plan condensed (TD867 override): one independent reviewer, two red-team gate runs (the first recorded four breaks, fixed in the plan; the second, NO BREAKS), no gstack.

## Handover notes for the Mac (PC to Mac, qa passed on the PC)

- The bash toys `dev/toy/test-regression.sh` and `dev/toy/test-ci-target.sh` skip on native Windows: the Mac's qa and ship MUST run them (their extractors now match `python3 - $live <<'PY'`; test-ci-target.sh ignores only the exact default-branch read in calls.log).
- The +1 row `defect-5773-issues-default-branch` is top's TD867 grant, and done line 4 of this goal says so; every other row is net 0.
- Still unproven until the first nightly after the merge: the real GITHUB_REF forms and token read of a schedule run.
- Never dispatch regression.yml on any branch. It is a patch that merges when green and does not take the Mac slot ahead of the cut chain; the Mac decides when.
