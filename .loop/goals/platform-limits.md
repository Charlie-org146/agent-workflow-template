# Count each platform limit (app send cap, owner-only session start) before it is reached and work inside it

- Slug: platform-limits
- Touches: skills/workflow-monitoring/scripts/unattended.py, skills/workflow-monitoring/scripts/sessions.py, .loop/regression.tsv
- ETA: 240 active minutes (estimate 190m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Every app send a machine session makes is counted in the persisted sends.json (the file under the git common dir): sessions.py send, the operation's own sends through operate.py send, a worker's or STATUS send recorded with unattended.py sends add TO, and sessions.py report when it messages the operation session. Each count keeps its time. The count resets to 0 by itself when the owner's words are recorded (sessions.py owner-words from owner or top), with no hand reset; a peer's words never reset it.
2. One event is one batched send: sessions.py send takes several goals (a comma list) and one text, sends one message to each distinct worker session it covers, never twice to the same session for the same event, and counts each message actually sent once.
3. At 15 of 20 sends, unattended.py status prints one line, once per count period (not on every call), for top, naming the count, the sends left and the projected time the cap runs out from the rate of the last hour (or 'not at this rate' with no rate); it is cleared by the reset. The check-in lines() carries it as a Needs-you line only when printed.
4. A worker comes only from waking an archived session: assign reuses a free pool session and never starts a new one; with no free session it is refused with the reason 'a new session needs the owner's typing: wake an archived session or free one', prints REFUSED, starts no session and no background process, and leaves the goal queued.
5. Everything above works on Windows and on the Mac: no path, shell or locking call is platform-specific, and a toy proves it on this machine with a fake session tool; unattended.py and sessions.py are no larger than they were, and each stays at or under the 20,000-byte package gate.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
