# Hands-off operation (#4781, #4507, #4813, #4679): a worker start works from a scheduled or Remote Control turn (background agent_command worker, then bound), the operation session archives merged and released workers and idle ones under memory pressure, one clean command starts an operation session with a readiness report, the session sets up its own check-in timer, and the check-in groups goals under their feature

- Slug: hands-off-operation
- Touches: skills/workflow-monitoring, skills/workflow-setup/scripts/settings.py, skills/workflow-delivery/scripts, docs/wiki/Monitoring.md, docs/wiki/Home.md, .loop/regression.tsv, dev/toy
- ETA: 275 active minutes (estimate 219m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given workers: auto (or a start asked with --background) and a frozen goal that no app session can take because the turn is scheduled or from Remote Control, when watch starts it, then a background agent_command worker is launched in the goal's worktree and bound to the goal, the board names it background, and with workers: app and no flag nothing is launched.
2. Given a goal whose merge and release the operation session has verified, when the next check-in runs, then that worker's session is archived and the check-in names it; a session whose goal is running, waiting or has an open PR is never archived.
3. Given free memory below min_free_memory_gb, when the next check-in runs, then idle sessions whose goal is released or retired are archived oldest first until memory is back above the floor, each is named in the check-in, and operation sessions and sessions of running, waiting or open-PR goals are never archived.
4. Given operate.py start on a machine, when it runs, then it prints one readiness table (session tool, workers mode, installed skills against the repo's, hooks, free memory, idle pool) with ok or the fix on each row, starts no goal, and starts no background worker unless workers: auto is set.
5. Given an operation session started with cadence 5 and no recorded check-in timer, when it starts, then operate.py timer shows the interval, the steps and what it never does and records the timer on the owner's yes, a changed cadence marks it stale, and the check-in shows a missing or stale timer under Needs you with the words to fix it.
6. Given goals naming only an issue number, with a feature label, a feature set by batch.py add --feature, or touches mapped in docs.tsv, when the check-in builds Dependencies, then each groups under its feature page, and with nothing to go on it shows no feature.
7. Given a queued goal, when the check-in builds, then it shows an estimated time from its size, not ~?.
8. checkin.py stays at or under 19,495 bytes, no script grows past its current size or past 19,000 bytes when it started under it, and the package holds no new shipped file.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->

1. In a repo with `.loop/config.json`, run `python3 skills/workflow-monitoring/scripts/operate.py start`.
   Expect: a table with the rows session tool, workers, skills, hooks, memory and pool, each ok or FIX with its fix, and a READY or NOT READY line; no goal starts.
2. Run `python3 skills/workflow-monitoring/scripts/operate.py timer`, then `operate.py timer created`, then `python3 skills/workflow-monitoring/scripts/checkin.py`.
   Expect: the first shows the interval, the steps and what the timer never does; after `created` the check-in has no timer item under Needs you, and after changing `cadence` it says the check-in timer is stale.
3. With a session tool set and a goal whose release is published, run `python3 skills/workflow-monitoring/scripts/pool.py archive`, then the check-in.
   Expect: `ARCHIVED <session> (<goal> released vX)` and, in the next check-in, an Archived section naming it; a running goal's session is untouched.
4. Run `python3 skills/workflow-monitoring/scripts/checkin.py` in a repo with queued goals that name only issue numbers.
   Expect: each goal under a feature heading (not "no feature") when its issue has a feature label or its touches map in `.loop/docs.tsv`, and a time instead of `~?` once finished goals exist.

