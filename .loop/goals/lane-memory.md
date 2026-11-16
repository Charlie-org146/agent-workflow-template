# Lanes stay inside the PC's memory floor and never blame a goal for the machine: lanes_cli affected is lean, a memory wait is not a lost try, and a Windows process-start failure is ENV, not FAIL (#4151, #4385, #4639)

- Slug: lane-memory
- Touches: not declared
- ETA: 210 active minutes (estimate 167m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. lanes_cli.py affected's peak memory per process drops well below today's ~800 MB (measure before and after on this PC and put both numbers in the PR), and a lane that waits for memory and gives up reports MEMORY_WAIT without charging a counted try (#4385).
2. A row that exits 0xC0000142 or another Windows process-start code is counted as ENV with a rerun hint, not FAIL, and a lane made mostly of ENV rows is not a counted try; a toy covers both, with a negative control that a row exiting 1 is still FAIL (#4639).

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
