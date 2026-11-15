# Design: finished goals leave the check-in

## Problem
The MON-14 map and its check (checkin.py `expected`, graph.py `classify`) already skip runs marked merged, retired or stopped, but a run
stays "done" or "running" in `.loop/runs` after its PR merged on GitHub (reg3-same-as-run, win-flock, health-clear x3), and old
records nobody runs (operator-setup, size-caps) keep being required. The check-in keeps asking the owner for them.

## Approaches
1. Filter only in the check: treat a goal as live only if running/holding/queued/waiting or merged since checkin.json `at`; leave records alone.
   Cheap, but the records pile up and the graph still lists them.
2. Filter in the check (live-only plus one [x] check-in after merge) and close records for good: a done run whose PR is MERGED (board_lines.states)
   becomes merged-and-closed (`release: merged`), and retired or stopped runs drop from the graph. Chosen: it is what the done lines say,
   and the cost is one extra read of PR state we already do (board_lines.states).

## Chosen
Approach 2. `graph.classify` returns "merged" for a done run whose PR GitHub reports MERGED; `checkin.gather` keeps a merged goal
only if its merge time is after the previous check-in (the one [x] showing), otherwise drops it; `expected` requires only live
goals plus those just merged. Close today's stale records by hand after checking each PR and worker: close reg3-same-as-run, win-flock,
the three health-clear records, operator-setup and size-caps (no PR, no worker, days idle); leave thermis newsletter-v2 (PR 904 OPEN) and
steward general-asks (parked; ask operation).

## Done lines
1. checkin.py/graph.py change plus toy cases proven red (a merged-before-check-in goal is not required; a merged-since one is).
2. Closing: classification of merged PRs plus the manual closes with PR and worker checked first.
3. MON-5 and MON-14 sub-bullets (owner-record o35 un-review, o36 review; text sent to operation first), toys red, scripts <= 19,000 bytes, package <= 98 files.

## Open questions
- None for the owner. general-asks closing goes to operation. newsletter-v2 stays open (its PR is open).
