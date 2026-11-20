# Bring private.py (20,297), role.py (20,034) and guards.py (20,005) to 19,000 LF bytes or less by text, comment and dead-code trims only (HLT-11.4, #4653, #5123)

- Slug: trim-delivery-a
- Touches: skills/workflow-delivery/scripts/private.py, skills/workflow-delivery/scripts/role.py, skills/workflow-delivery/scripts/guards.py
- ETA: 225 active minutes (estimate 177m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given main after this goal, when git ls-tree -l reads the three scripts, then each is at or under 19,000 bytes and the pass rows that test them (scripts-a-delivery-under-19000, size-fail and the private, role and guards rows) pass as before
2. Given the touched scripts, when their own toys run before and after, then every output is unchanged, with a negative control that a one-line behaviour change fails a toy
3. Given this goal's diff, then no shipped file is added, no touched script is over 19,000 bytes or larger than on main, net regression rows are 0 or fewer, and no requirement text changes

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
