# One review at the start: a goal asks the owner once, and no later step waits on the owner (owner o1037, o1038)

- Slug: v110-one-review
- Touches: skills/workflow-delivery, skills/workflow-monitoring, dev/toy, .loop/regression.tsv, docs/wiki/Delivery.md, docs/wiki/Deliver-first.md, docs/wiki/How-to-use-Deliver-first.md, docs/wiki/Operation.md, docs/wiki/How-to-use-Operation.md, docs/wiki/Tests.md, skills/loop-files.md, listing.json
- ETA: 870 active minutes (estimate 694m plus a 25% margin)

## Words used

The replacement for DLF-1.3, approved with the done lines (o1038):

> DLF-1.3 **One review, at the start.** A goal waits for me once: at its start, where I approve its done lines and the safety items it is known to touch (deleting what can't be restored, money, security and sandbox settings, private data, steward merges, a change to what a feature promises, a test loosened or deleted). After that nothing waits for me. A safety item found later takes the safe option without asking: it is fixed in the build, or that part is dropped and filed as a DLF-1.1 line; nothing is waived or loosened that the start review didn't approve. The leak read before any push and the PR's reached-test run before a merge stay as automatic checks, not waits for me. Every decision made in my place is listed in the next check-in with a one-line revert.

The DEL-3 line on the Delivery page is aligned in this goal's build to this wording (operation's decision under o1037 and o1038, listed for the owner to revert):

> My decisions are made once, at a goal's start; later ones are made on the recommendation, with the safe option for safety, and listed for me to revert (DLF-1.3).

The metric becomes "minutes a goal waits for me after its start review, target 0", and the Operation page's owner-question lines change the same way.

## Done lines

Frozen. A wrong done line needs a new goal.

1. A goal asks the owner once, at its start: its done lines and its known safety items together, in one message.
2. After that start review, no step waits on the owner: readings, red-team findings and plan questions are decided by the operation on its recommendation.
3. A safety finding found later takes the safe option without asking: fixed in the build, or that part dropped and filed as a later item; a check is never waived or loosened.
4. Every such decision appears in the next check-in with a one-line revert command, and a revert stops that part.
5. Checks, leak reads and merge rules stay as they are; only the waits on the owner go.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
