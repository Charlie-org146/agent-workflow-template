# One review at the start: a goal asks the owner once, and no later step waits on the owner (owner o1037, o1038)

- Slug: v110-one-review
- Touches: skills/workflow-delivery, skills/workflow-monitoring, dev/toy, .loop/regression.tsv, docs/wiki/Delivery.md, docs/wiki/Deliver-first.md, docs/wiki/How-to-use-Deliver-first.md, docs/wiki/Operation.md, docs/wiki/How-to-use-Operation.md, docs/wiki/Tests.md, skills/loop-files.md, listing.json
- ETA: 870 active minutes (estimate 694m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. A goal asks the owner once, at its start: its done lines and its known safety items together, in one message.
2. After that start review, no step waits on the owner: readings, red-team findings and plan questions are decided by the operation on its recommendation.
3. A safety finding found later takes the safe option without asking: fixed in the build, or that part dropped and filed as a later item; a check is never waived or loosened.
4. Every such decision appears in the next check-in with a one-line revert command, and a revert stops that part.
5. Checks, leak reads and merge rules stay as they are; only the waits on the owner go.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
