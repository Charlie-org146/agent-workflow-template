# platform-limits: plan

Files that exist and are changed: `skills/workflow-monitoring/scripts/unattended.py` (`sent`, `sends_status`, `lines`, `main`), `skills/workflow-monitoring/scripts/sessions.py` (`assign`, `cmd_assign`, `cmd_send`, `cmd_owner_words`, `main`). New: `dev/toy/test-platform-limits.py`. Rows go into `.loop/regression.tsv`.

## Build steps
1. unattended.py: `WARN_AT = 15`; `sent` appends the time to `times`; `reset()` (also `sends reset`); `sends_status` adds the projection and sets `warned` once; `lines` carries it.
2. sessions.py: `cmd_owner_words` calls `unattended.reset()` after recording; `cmd_send` takes a comma list and sends once per distinct session; `assign` never calls `start`; `cmd_assign` prints REFUSED. Trim comments and long strings elsewhere in sessions.py so it ends under 20,000 and no larger than main.
3. The toy: a fake session tool in a temp repo, one check per done line, plus a size check against `git show origin/main:`.
4. One regression row per done line group (at most 5), levels `land`, `# windows: ok` toy as the command; red proof by running the toy against main's scripts.

## Tests
1. times, `sends add`, reset on owner-words: the toy counts 3 sends, records owner words, expects 0, and a peer's words leave it at 3.
2. batch: two goals on one session and one on another send 2 messages, count 2.
3. 15 of 20: at 15 status prints the projection line once; the second call prints none.
4. assign with no free session prints REFUSED and the fake tool's start is never called.
5. sizes, from the toy.

## What could break
sessions.py is at the package gate (20,000 bytes): a line added without a line trimmed fails the gate. Callers that parse `sends status` keep the first line unchanged. `machines.start_worker` falls to a background worker where `workers` is not `app`; that is a process, not a session, and stays.

## Out of scope
layers.py, checkin.py, auto.py, board_status.py, machines.py and the health scripts; the app's own cap; the QA and PR lanes (TD333).
