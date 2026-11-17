# REG-1: A real change still reaches the root runners while a change only to NO_EFFECT files reaches none; the 7 affected-lane rows pass (#4554)

- Slug: ci-affected-rows
- Touches: not declared
- ETA: 210 active minutes (estimate 166m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given the 7 rows in #4554, when they run on CI, then each passes
2. Given a change to a file that isn't NO_EFFECT, when lanes pick rows, then the root runners still run, and a change only to NO_EFFECT files still reaches none

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
