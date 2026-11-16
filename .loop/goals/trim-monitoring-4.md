# checkin.py, auto.py, replan.py and pool.py in workflow-monitoring are each under the 19,000-byte cap (health size issues for them)

- Slug: trim-monitoring-4
- Touches: not declared
- ETA: 210 active minutes (estimate 166m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. On main, workflow-monitoring's checkin.py, auto.py, replan.py and pool.py are each at or under 19,000 bytes as git stores them, and the health size rule reports none of them.
2. No behavior changes: every regression row that runs those four scripts still passes, the package file count stays at or under its cap, and the open health size issues for the four scripts are closed with a comment naming this goal.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
