# Plan: checkin-tidy

Checked against the code: checkin.py `gather` (live = not merged/retired, `shown`), `expected`, `render`; graph.py `merged`, `classify`;
board_lines.py `states` (PR state MERGED|CLOSED|OPEN). All exist.

## Build steps
1. graph.py: `classify` returns "merged" for a done run whose PR GitHub reports MERGED (gather passes board_lines.states into a merged-check);
   a retired or stopped run stays out of every list.
2. checkin.py `gather`: live = running/holding/queued/waiting/done-awaiting-merge, plus goals merged since checkin.json `at` (their `updated`
   time is later than it); a goal merged before it is dropped. `expected` uses the same list, so MON-14 requires only those.
3. Trim docstrings so checkin.py and graph.py stay <= 19,000 LF bytes; no new files.
4. Close stale records with the loop's own close path after checking PR and worker: reg3-same-as-run, win-flock, health-clear (thermis, steward,
   portfolio), operator-setup, size-caps. Keep newsletter-v2 (PR 904 open). general-asks: ask operation.
5. Docs: send operation the MON-5 and MON-14 sub-bullet text; apply with o35 (un-review) and o36 (review); re-render tables.

## Tests (each seen failing before the change)
- toy: a goal merged before the previous check-in is not required by `missing`/`expected`; a goal merged since is; a done run with a MERGED PR
  classifies as merged. Rows: mon14-live-only, mon14-merged-since, mon5-closed-leaves-graph.

## Could break
The existing mon14-map rows (finish, arrows, live-only, times); byte caps; the reply hook's Dependencies check (reply_hook.py).

## Out of scope
general-asks, newsletter-v2, board.py/unattended.py (adoption worker's).

VERDICT: self: plan meets the done lines
