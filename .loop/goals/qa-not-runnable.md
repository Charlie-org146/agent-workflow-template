# qa records a lane whose only failures are rows this machine can't run (GRD-11, #4492)

- Slug: qa-not-runnable
- Touches: not declared

## Done lines

Frozen. A wrong done line needs a new goal.

1. The lane marks a row it can't run on this machine (a missing tool such as node or pnpm, a POSIX-only import, exit 77) as not runnable here, apart from a real failure.
2. goal.py records qa as 'N pass; M not runnable here' when every other row passes, and a real failure still refuses qa.
3. Each goal with not-runnable rows files one other-machine to-do on its feature milestone listing them, and a toy test proves all three with a negative control.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
