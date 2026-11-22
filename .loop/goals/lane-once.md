# One test lane per goal head, reused by the qa, ship and pr steps, as Reviewed DEL-17 promises (patch, fixes #5734)

- Slug: lane-once
- Touches: skills/workflow-delivery, dev/toy, .loop/regression.tsv, docs
- ETA: 365 active minutes (estimate 290m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a goal's head, then one test lane runs for it, and its pass for that exact head satisfies the qa, ship and pr steps' lane gates; any move of HEAD needs a new lane
2. Given that lane, then it selects exactly the rows today's qa lane selects for the same diff; no row is dropped, and no budget or test is loosened
3. Given a lane whose head differs from HEAD, or a failed lane, then ship and pr are refused as today, with a negative control
4. Given the change, then docs, package and private-name checks are green, no existing row turns red, and no new file is added under skills/
5. The pull request merges on green as a patch

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
