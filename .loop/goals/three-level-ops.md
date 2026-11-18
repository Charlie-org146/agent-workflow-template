# The operation runs in three layers (one owner-facing top session, one operation session per machine, one worker per goal), and the Monitoring spec and scripts say so and enforce today's settings as defaults

- Slug: three-level-ops
- Touches: not declared
- ETA: 295 active minutes (estimate 235m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. The Monitoring PRD states the three layers and their duties (top: the owner's only session, governance only, only board and Loop Board publisher every 5 minutes; machine: assigns goals, schedules sessions and memory, runs auto/checkin/dry-runs/merge, reports up; worker: one goal, one worktree, talks only to its machine), the messages and their fields (STATUS on change and every 30 minutes with main per repo, worker lines, PR per goal, merges, parked and idle with reasons, needs-owner with exact words and a recommendation; ASK; OWNER-WORDS; PRIORITY; MERGE-REQUEST and MERGE-GO machine to machine, copied to top), top's 5-minute board order, the owner's 'make them busy and be aggressive about time and token' rule, and the standing safety rules, within criteria_max 19 by revising or merging existing MON requirements (a cap raise waits for the owner)
2. operate.py gains a top role that builds one board for all machines from each machine's latest STATUS, calls out a STATUS over 30 minutes old, and is the only role that publishes the board, and a machine role that runs today's loop but sends STATUS to top and prints one line instead of the board; test rows cover a two-machine board, the stale call-out, and the machine role printing no board
3. Today's settings are enforced defaults with a check each: relay counts except safety (OWNER-WORDS from top accepted as owner words except safety classes, refused from a peer); machine sessions are STATUS-only; machines raise their own time and token budgets, caps stay the owner's; agent_command passes the tool list as one --allowedTools=<list> token (a check reports the two-token form; applying it stays the owner's); STATUS carries PR numbers, parked and idle sessions with reasons
4. reply_hook.py's MON-5 check gains a machine mode that accepts a machine session's one-line check-in (time plus 'STATUS sent' or 'no change') once STATUS went to top, while top keeps the full-layout check; a test row is seen red with today's hook and green after
5. Nothing else changes: no other page's wording, and the net test-row count grows by at most 11

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
