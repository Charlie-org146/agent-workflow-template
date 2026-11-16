# A goal's minute budget never counts time it spends held: an owner or operation pause, a wait in the pr queue, or an idle session waiting for the operation's word (#4534)

- Slug: held-time-charge
- Touches: not declared
- ETA: 205 active minutes (estimate 164m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. board_log.active_minutes charges only time a step is actually running: a fixture goal that runs 30 minutes, sits in a goal.py wait pause for 300 minutes, then runs 20 minutes is charged 50, and the same goal with no pause running 350 minutes is charged 350 (negative control).
2. A goal whose session goes idle with no step running and no reply sent for more than the idle limit stops being charged until its next step or record starts, and goal.py show prints both charged and wall minutes; a toy covers both, run through goal.py's own budget gate (fit.budget_stop) rather than the helper alone.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
