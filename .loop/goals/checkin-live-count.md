# checkin.py's first line counts goals from live sessions, not stale run records (TD481): today it reads '44 running, 27 waiting on you' from old records. A goal counts as running or waiting only when it holds a slot and has spoken within silent_minutes, the rule machine-log (#5573) uses for the status file; stale records show once as parked, so nothing vanishes

- Slug: checkin-live-count
- Touches: skills, dev/toy
- ETA: 470 active minutes (estimate 373m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given 2 live goals and 40 stale running records, when checkin.py runs, then line 1 counts 2 running and the stale ones show once as parked, shown by a toy
2. Given the same rule as layers.py's live-worker count, then checkin.py and the status file agree on the running count in the toy
3. Given this goal's diff, then every script stays under 20,480 bytes, docs.py check and criteria.py render --check pass, package.py --static passes, and each new regression row has a red proof (regression.py red)

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
