# platform-limits: design

## Problem
Two platform limits can leave the loop waiting for the owner's typing: the app pauses sends after 20 with no owner message, and only the owner's typing starts a new session. Today sends.json counts only `sessions.py send`, resets only by hand (`unattended.py sends reset`), warns at 16 on every status call with no projection, and `assign` starts a new session when no free one exists.

## Approaches
1. Count and shape in the two scripts that already own the limits: `unattended.py` (sends.json, the warning line, reset) and `sessions.py` (send, assign, owner-words). Cost: small; risk: both scripts sit at their size gate (20,000 and 18,967 bytes), so every added line is paid for by a trimmed one.
2. A new module for limits that both import. Cost: one more file the package gate lists; risk: off the brief's file list. Rejected.

## Chosen: approach 1
- **sends.json** `{since, count, times, warned}`. `unattended.sent(to)` (also `sends add TO`, which workers and STATUS sends call) appends the time and counts once. `reset()` writes a fresh file and clears `warned`. `sessions.py owner-words` calls `reset()` for the owner or top (a peer is already refused before it writes), so no hand reset is needed. Operation sends go through `operate.py send` into `sessions.py send`, already counted.
- **Batched send**: `sessions.py send A,B,C TEXT` groups the goals by their session id and sends one message to each distinct session (its text names the goals it covers), counting each message sent. A goal with no session or an unreachable one is reported as today.
- **15 of 20**: `WARN_AT = 15`. `sends_status()` adds, the first time the count is at or over 15 in a count period, the projected time the cap runs out from the sends in `times` over the last hour (`not at this rate` with none), and sets `warned`. The same text is the Needs-you line in `lines()`, printed once.
- **No new sessions**: `assign` tries only free pool sessions, in order, and never calls the tool's `start`. With none free it sets `worker_why` to "a new session needs the owner's typing: wake an archived session or free one" and returns False; `cmd_assign` prints REFUSED and exits 1 instead of BACKGROUND. Under `workers: app` (this repo) `machines.start_worker` starts no background process and the goal waits for `sessions.py bind`. A repo that sets neither keeps today's background fallback; it is not a session.
- **Windows and Mac**: only `json`, `os`, `datetime`; no shell or lock call is added. A new toy `dev/toy/test-platform-limits.py` (`# windows: ok`) runs a fake session tool through all five lines.

## What each done line needs
1. times in sends.json, `sends add`, reset in owner-words.
2. comma list in `cmd_send`, grouped by session id.
3. `warned` flag and projection in `unattended.py`.
4. `assign` and `cmd_assign` change.
5. the toy, one regression row, and both scripts no larger than on main.

## Open questions
None for the owner. The text a worker or STATUS send passes to `sends add` is its recipient id, as today.
