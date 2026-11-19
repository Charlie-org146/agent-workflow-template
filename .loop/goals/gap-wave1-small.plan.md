# Plan: gap-wave1-small

Checked against the code in this worktree (main 88ac1354): every file and line below exists.

## Build steps

1. Floor to 3 GB (done line 1). `replan.py:184` (`cfg.get(..., 4)`), `lanes_cli.py:337` (`.get(..., 4)` and its docstring at 333), `file.py:345/346` (two `4`), `board_status.py:158/161/230` (3.5 to 3), `settings.py:58` (4 to 3). `docs/wiki/How-to-use-Regression.md:69` says "(default 4)": change to 3. Every reader keeps `get("min_free_memory_gb", 3)`, so a set value (repo or machine-local) still wins.
2. `milestones_source` (done line 2, #5079). `settings.py`: new REPO row `("milestones_source", REPO, "", ...)`, a check in `fill_repo` that refuses a value that is not empty, `url:https://...` or `mcp:<server>:<id>` (`mcp:notion:` needs 32 hex), and trimmed help text on other rows to stay under 19,000 LF bytes. `defects.py:255`: leave it out of "missing" like `regression_runs` (opt-in). Regenerate `skills/workflow-setup/references/settings.md` and the Home Settings block.
3. Own-repo image links (done line 2, #5078). `prdcopy.py:346` NEAR: add `/blob|raw/<ref>/<path>.<png|jpe?g|gif|svg|webp>` with an optional `?raw=true`, checked against the page's own repo as the other branches are. Source files, issues, another repo's image still fail.
4. Token never writes (done line 3, GRD-5.1). `automation.py:225` `live = args.live`, message and DRY RUN line say `--live`; `regression.py:242` and `:309`, `runs.py:389` use `args.live` alone; the usage line already says a token writes nothing. The Mac tick already passes `digest --live` (`workflows.py:340`). Update `dev/toy/test-automation.sh` (`live()`, line 96 and 102 texts) and `test-automation-email.sh` (`dg`, line 483) to pass `--live`.
5. Rows. New toy `dev/toy/test-gap-wave1.py` (python, windows ok) and `dev/toy/break-gap-wave1.py`. Rows: `gap-floor-default-3` (goal :1: defaults read 3 with no key, a set key wins, in all five readers), `gap-milestones-source-known` (goal :2: known setting, bad values refused), `gap-own-image-links` (goal DOC-19: own image passes, another repo's image and a source file fail), `gap-token-no-live` (goal :3: each of the four sites writes nothing with a token and no `--live`, and writes with `--live`), and `done-gap-wave1-small-4` (covered, goal :4). Each is seen failing with `regression.py red --break`. Net rows 0: the four `done-docs-gate-scope-*` covered rows of the merged goal come out.
6. Wiki pages: re-render the Tests tables, `entry.py write` for START.md; `docs check` and `wiki.py prepare` clean.

## Test per done line

1. `gap-floor-default-3`, red when any reader's default goes back to 4 or 3.5.
2. `gap-milestones-source-known` and `gap-own-image-links`, with negative controls (bad value, another repo's image, a source-file link).
3. `gap-token-no-live`, red when a site takes the token again; the `--live` half is the positive control.
4. `done-gap-wave1-small-4` and the size rows; `wc` shows every touched script at or under 19,000 LF bytes or not grown.

## What could break

The two toys that run the digest with a token and no `--live`; both updated. The `Home.md` Settings block and `settings.md` go stale until regenerated. A script over 19,000 bytes: settings.py (18,993) pays for its row by trimming its own help text.

## Out of scope

`fit.py`, `guards.py`, `private.py`, `role.py`, `routing.py`, `lanekit.py`; `--live` on docs sync, health file, release (the rest of GRD-5.1); the `--body-file` cluster (MCH-1.7, GRD-5.2); the PC's local memory-floor edit. Requirement text does not change.

VERDICT: self: plan matches the design and the frozen done lines
PENDING: none
