# setup --git-hooks writes hooks it reads back as its own: the hook mark survives in the stub (#4506)

- Slug: hook-stub-mark
- Touches: not declared

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a repo where setup --git-hooks just wrote its hooks, when setup checks them, then none is reported foreign
2. Given a hook someone else wrote, when setup checks it, then it is still reported foreign and left alone

## Verify by hand

<!-- Numbered steps a person can follow, each with an Expect: line. -->
