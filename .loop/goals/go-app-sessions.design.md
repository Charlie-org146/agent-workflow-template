# Design: go-app-sessions (#4040)

## Problem
`watch.py go` (and every watch round) starts a goal through `start_round`: it freezes the goal, tries
`sessions.assign`, and when no session could be started or reached it launches a background `claude -p` through
`agent_command`. A pod whose rule is app sessions only has no way to say so. Separately, `runs()` calls `.get` on
whatever JSON sits in the runs folder, so a stray list file (issues.json) crashes watch.

## Approaches
1. A `workers` setting; `workers: app` makes `start_round` skip the background fallback: the goal stays frozen and
   queued with `worker: app` and a line saying to bind a session. Small, one branch, default unchanged.
2. Remove `agent_command` from the config. Breaks pods that want background workers, and does not say the rule.

## Chosen
Approach 1, plus `runs()` skips records that are not dicts. `graph.app_only(cfg)` reads the setting; `settings.py`
registers `workers` (default empty) so the Settings table documents it. This pod sets `workers: app`. mend.py's
background restart is out of scope (it needs `mend` on, which is off here).

## Each done line
1. Toy: with workers app and no session tool, `watch.py go` leaves the goal queued, worker app, no pid, no log, and no
   process started (agent_command is a marker that would write a file).
2. Same toy: without the setting the same goal launches the marker command.
3. Toy: a list file in the runs folder; `runs()` returns the goals and does not raise.
No open questions. No reviewed requirement is reworded.
