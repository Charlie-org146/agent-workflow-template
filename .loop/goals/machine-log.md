# OPS-1 machine log: the machine status file (.git/loop/status/<machine>.json, written by layers.py status) counts workers from live app sessions, not from session-pool records (TD430), and the status is rewritten every minute while an operation session runs, so the Machine line never shows an inflated worker count or a stale time

- Slug: machine-log
- Touches: skills, dev/toy
- ETA: 465 active minutes (estimate 369m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given 2 live worker sessions and 7 stale busy records, when the status is written, then it reports 2 workers, and a toy proves both cases
2. Given an operation session running, then the status file's timestamp is never more than 60 seconds old, shown by a toy with a fake clock
3. Given this goal's diff, then every script stays under 20,480 bytes, docs.py check and criteria.py render --check pass, and each new regression row has a red proof (regression.py red)

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
