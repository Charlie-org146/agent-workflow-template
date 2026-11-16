# The release header's ETA uses the goals' hard ETAs, and the ETA margin is a repo setting (#4519, #4528)

- Slug: eta-header-margin
- Touches: not declared
- ETA: 205 active minutes (estimate 162m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. A release header's ETA is the latest of its goals' hard ETAs from #4512, falling back to the estimate only for a goal with no hard ETA, and the header says which it used; a toy board with one hard-ETA goal and one estimated goal shows the header take the later of the two, and a board with no hard ETAs reads as it does today (negative control).
2. The ETA margin is a repo setting (default 25 percent) that auto.py reads instead of its constant and that the settings docs list; a toy shows a 40 percent setting moves a goal's hard ETA and the default still gives today's value.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
