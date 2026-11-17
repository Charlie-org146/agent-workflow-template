# hands-off-operation: plan

Checked against the code (all exist): `watch.start_round` / `watch.launch` / `watch.cmd_go` (watch.py), `sessions.assign` / `sessions.cmd_assign`, `worker.cmd_bind` / `worker.call` / `worker.tool`, `graph.app_only` / `graph.memory_room` / `graph.merged` / `graph.parallel_of`, `pool.return_session` / `pool.status_line` / `pool.counts`, `checkin.render` (Needs you block, `archive session ...` line from pool state `archive`), `board_status.feature_of` / `queued` / `estimate_full` / `goal_line`, `batch.py add`, `auto.eta_new`, `settings.py` ("workers" row), `.loop/docs.tsv` (page, paths). A published release is `release == "cut"` with `release_version` and `release_url` on the run record (autorelease.py:348); `release == "merged"` means merged, not published.

## Build steps
1. monitor.py (room ~4.6k, no new file): add helpers `eligible(state, name)`, `verified(state, root)`, `archive_candidates(root, cfg, pressure)`, `readiness(root, cfg)`, `timer_state(loop, cadence)`, `feature_for(root, slug, text, touches)`. They only read files and call `gh` through one wrapper with a timeout.
2. Fallback worker (done line 1): graph.py `app_only` stays; watch.py `start_round` takes `args.background` (and `workers: auto` is the documented value that already skips the "app only" wait: only the literal `app` waits). After `launch()` returns, bind the run: `worker=background`, `worker_why` = why no session started (sessions.assign already sets it; scheduled/Remote Control text added), `bound_at`, `attempt` bumped. `go --background` and `sessions.py assign --background` parse the flag. settings.py `workers` row words: `app` / `auto` / unset.
3. Archive (done lines 2, 3): pool.py `archive [--pressure]` and `archived ID`; calls `TOOL archive ID` through `worker.call`, else prints `ARCHIVE-NOW ID`; sets pool state `archived`, appends `<loop>/archived.tsv`. operate.py runs it each pass before checkin. checkin.py prints `Archived:` lines for rows since the last check-in and no longer asks the owner to archive by hand for the sessions it archived itself. Pressure: `board_status.allowed() == 0` or free memory below `min_free_memory_gb`; idle sessions whose `history[-1].slug` goal is released (verified) or retired, oldest `since` first, one per call until room returns.
4. operate.py: `start` (readiness table, starts nothing) and `timer [created]`; checkin.py gets one Needs you line from `monitor.timer_state` (`missing` or `stale`, with the words `operate.py timer created`).
5. board_status.feature_of(root, text, slug=None, touches=None) with the fallback chain; checkin.py passes the run; queue line field `feature:` parsed by graph.parse; batch.py `add --feature PAGE`; queued goals use `bs.estimate_full` (as `eta_new`) in `goal_line` instead of `?`.
6. Size trims to pay for it: checkin.py loses duplicate code (inline lambdas, the `unranked` helpers' repeats) by at least what it gains, ≤ 19,495 LF; other touched scripts end ≤ their start size.
7. Docs: MON-5 (Unreviewed) gets the timer, grouping and archived-lines sub-bullets; MON-11 (Unreviewed) the fallback worker; MON-6 and MON-1 need an owner-words un-review (ask operation-pc, o130) for archive and start. References/commands.md and SKILL.md command map gain `operate.py start|timer` and `pool.py archive`. Home/START.md/README re-render from committed data.

## Tests (regression rows, each seen red before the build, then green)
`dev/toy/test-hands-off.py` (new, not shipped): fake `gh` (dev/toy/fakegh) and a fake session tool.
- fallback-bg-auto: `workers: auto`, tool fails to start, then a background worker is launched and bound (pid, bound_at, attempt+1, `background` on the board); with `workers: app` and no flag nothing launches (negative control).
- archive-after-release: merged and released goal's session is archived and the check-in names it; running, waiting, open-PR goals and an `operation` session are never archived (negative controls).
- archive-pressure: free memory below the floor archives idle released sessions oldest first and stops once memory is back; none when above the floor.
- start-readiness: `operate.py start` prints each row with ok or the fix and starts no goal.
- timer: missing, then recorded, then stale after a cadence change; check-in shows the Needs you line only when missing or stale.
- feature-fallback / queued-estimate: label, `--feature`, docs.tsv touches, none; queued goal shows an estimate.
- size row: checkin.py ≤ 19,495 and no touched script grew.

## What could break
- checkin.py is at its cap: every addition needs a matching trim, and the reply-hook layout checks (`reply-hook-*` rows, Needs you ranking MON-19: each item must say what it holds up) must keep passing; the new Needs you lines go through `graph.rank`.
- Archiving a session the operator still uses: guarded by `eligible` and the verified release; gh doubt means not verified.
- Windows: no fcntl-dependent new code; the existing `se.locked` is used.

## Out of scope
Owner emails (#4671), machine-to-machine merge slots, the Mac's phone-first fallback (its hooks, merged separately), token-diet, flipping the repo's `workers` to `auto` (offered in the approval batch, not done here).

