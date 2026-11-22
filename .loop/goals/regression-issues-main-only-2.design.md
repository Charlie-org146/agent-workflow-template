# Design: regression issues are written only from the default branch (#5773)

## Problem
The generated regression workflow's row step runs `python3 - --live`, so a `workflow_dispatch` on a feature branch (or any ref) files, reopens, comments on and closes `regression` issues as if it were the default branch. Closing main's real issues for rows that are green on a branch is the harm. The inline script already dry-runs every `gh` call that is not `gh api` when `--live` is absent (all writes are `gh issue ...` or `gh label ...`; `gh api` is only used to read), so the whole fix is deciding `--live`.

## Approaches
1. Compare `github.ref` with `github.event.repository.default_branch` in the YAML. Cheap, but that context value is not present on every event (schedule), and a missing value would compare unequal and silently never go live on the nightly run: it fails closed but breaks the nightly.
2. Read the default branch at runtime in the step's shell, `gh api repos/{owner}/{repo} --jq .default_branch`, and set `live=--live` only when it is non-empty and `$GITHUB_REF` is exactly `refs/heads/<it>`; otherwise print one `DRY RUN` line saying why and pass nothing.

## Choice
Approach 2. It works the same on schedule and dispatch, fails closed (an unreadable default branch gives no `--live`), and `refs/pull/N/merge`, tags and every other ref compare unequal. Label creation is already `gh label create` through the same `gh()` wrapper, so it sits inside the dry-run with no extra code.

## What each done line needs
1. Line 1: two shell lines in the ROUTINE row step of actions.py (the `python3 - --live` line becomes `python3 - $live`), `GITHUB_REF` is already in the runner environment.
2. Line 2: no code beyond line 1; the toy proves it with a fake `gh` that records every call and fails on a write, run on `refs/pull/7/merge`, a tag and a feature branch.
3. Line 3: one toy renders the workflow with actions.py, extracts the step's `run:` block and runs it with a fake `gh` on PATH for a schedule run on main, a dispatch on main and a dispatch on a feature branch; writes happen only on the first two, and an unreadable default branch writes nothing.
4. Line 4: regression.yml is re-rendered by `actions.py` (never by hand); actions.py must not grow past main's 18,980 LF bytes, so a few existing words are trimmed to pay for the new lines; the new check folds into an existing row (net 0 rows).

## Open questions
None blocking. The `summary` job also has `issues: write` but only prints a run summary with an empty token; it is out of scope.
