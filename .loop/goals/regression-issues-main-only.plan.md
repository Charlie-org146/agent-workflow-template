# Plan: regression issues are written only from the default branch (#5773)

Checked against the code: the row step lives in `ROUTINE`-prefixed `WORKFLOW` text in `skills/workflow-regression/scripts/actions.py` (line 65; the `python3 - --live <<'PY'` line is 83); every write in its inline script is a `gh issue ...` or `gh label ...` call through the `gh()` wrapper, which already prints `WOULD gh ...` and runs nothing when `--live` is absent; `gh api` is only used to read. `render()` and `write()` produce `.github/workflows/regression.yml`. `dev/toy/test-regression-issues.py` already cuts the block out of `actions.render()` and runs it against an in-memory gh.

## Build steps (in order)
1. Trim existing prose in actions.py by at least the bytes step 2 adds, so the LF size stays at or under main's 18,980 (measure with `python3 -c`, LF bytes, the working tree is CRLF).
2. In the row step's `run:` block, before the heredoc, add a small shell block: `live=`; read `def=$(gh api repos/{owner}/{repo} --jq .default_branch 2>/dev/null)`; set `live=--live` only if `$def` is non-empty and `$GITHUB_REF` equals `refs/heads/$def` exactly; else print one `DRY RUN: <why>, nothing is written` line. Change `python3 - --live <<'PY'` to `python3 - $live <<'PY'`. Nothing else in the inline script changes: label creation is already `gh label create` through the same wrapper, so it sits inside the dry-run.
3. Re-render regression.yml with the generator (`regression.py workflow`, never by hand) and commit it.
4. Tests, all folded into existing files, net rows 0: in `dev/toy/test-regression-issues.py` change the existing line-95 check from "starts its issue block with --live" to "passes `$live`, and sets it only on the default branch" (a stronger check, not a looser one), and add a case that cuts the shell block out of the rendered step and runs it in bash with a fake `gh` on PATH for: a schedule run on main and a dispatch on main (`live` set), a dispatch on a feature branch, `refs/pull/7/merge`, a tag, and a `gh` that fails or prints nothing (all five: `live` empty and the DRY RUN line printed). The toy skips (77) when no bash is on PATH. Widen the row `issues-live-only-ci` to also require the new PASS lines, and prove it red with `regression.py red issues-live-only-ci --break "<sed that puts --live back>"` on a copy of HEAD.
5. The goal fixes #5773, which needs a defect row linked to it: make `issues-live-only-ci` that row (category defect, link to #5773, seen failing before the change) instead of adding one, as pc-path-trust did, so net rows stay 0. If top wants it kept as a criterion row and a new defect row added, that is a +1 grant.
6. One line on the Regression wiki page naming the rule (issues are written only on the default branch), then the Tests tables regenerated; `docs.py check` clean.

## What could break
- A repo whose default branch is read differently (a renamed default): the runtime read handles it. A token without read access to the repo API: the read fails, no `--live`, a dry run: fails closed, the nightly would stop filing until fixed (the `DRY RUN` line says why).
- The existing toy check that looks for the literal `--live` after `python3 -`: updated in step 4.
- actions.py byte size: step 1.

## Out of scope
The `summary` job (it has `issues: write` but only writes a run summary with an empty token); `regression.py run` locally; any other workflow.
