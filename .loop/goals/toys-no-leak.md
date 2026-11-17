# REG-1: No toy changes the real ~/.workflow-loop; on the CI runner and on the PC every toy uses a temp home (#4555)

- Slug: toys-no-leak
- Touches: not declared
- ETA: 205 active minutes (estimate 164m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given the four LEAK rows, when they run, then the real ~/.workflow-loop is unchanged before and after
2. A guard row fails when any toy writes under the real ~/.workflow-loop

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
