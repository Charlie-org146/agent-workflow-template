# The pr queue keeps a goal's place even when its session never reported its step (#4523)

- Slug: pr-queue-step
- Touches: not declared

## Done lines

Frozen. A wrong done line needs a new goal.

1. Goal A joins the pr queue first while its run record says build, goal B joins later at pr, and A stays first in pool.py pr_turn --list and in pr_turn.
2. A toy covers that case, and a negative control shows a merged goal's ticket is still dropped.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
