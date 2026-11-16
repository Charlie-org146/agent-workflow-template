# A goal's ETA is a hard limit; past it the owner chooses ship now, extend once, or defer (#4512, owner o52)

- Slug: hard-eta
- Touches: not declared

## Done lines

Frozen. A wrong done line needs a new goal.

1. Every goal records a hard ETA when it is frozen (the estimate plus a margin), and the check-in shows it for every goal.
2. A goal past its ETA starts no new step and appears under Needs you with three choices: ship now with what is done, extend once by a stated amount in the owner's words, or move it to the next release; goal.py refuses to extend an ETA or raise a time budget without an owner-words record.
3. Health warns on a live goal with no ETA, fails on an ETA extended without an owner record, and checks that every overrun goal is under Needs you, each with a negative control; the Guardrails page states this as a requirement under owner record o52.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
