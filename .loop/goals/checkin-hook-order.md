# The check-in hook follows CHK-1's board order (TD423 (b), approved by operation-top under owner delegation DOC-2, o486; BUILT AND HELD per TD424: never armed or merged until the owner answers whether their own check-in prompt moves to the board order). reply_hook.py SECTIONS becomes (Your move, Red team, Release goals, Task queue, Workers, Shipped) after a one-line headline of what slipped; numbered questions live under Your move; any empty section may say none; the missing-parts message counts six. Whether the per-repo Dependencies check stays is the owner's question and is left exactly as it is in this build, so only the section list and order change

- Slug: checkin-hook-order
- Touches: skills/workflow-monitoring/scripts/reply_hook.py, dev/toy
- ETA: 460 active minutes (estimate 368m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a check-in reply in the board order (headline, then the six sections, empty ones saying none), when the hook runs, then it passes; and given a reply in the old layout (All sessions, Dependencies, Needs you, Coming up), then the hook blocks it naming the expected order (a toy proves both ways)
2. Given this goal's diff, then only reply_hook.py, one toy, the docs that state the hook's sections, and the goal's record files change; reply_hook.py stays under 20,480 bytes; docs.py check and criteria.py render --check pass
3. Given the pushed pull request, then it is NOT armed and NOT merged by any session until operation-top relays the owner's answer, and its body says so in its first line

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
