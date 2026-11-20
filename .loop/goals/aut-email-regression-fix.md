# The row aut-email-regression passes again (issue 5466; TD441: next, because a row already red on main fails every pull request that selects it, and it blocks #5518 and #5520 on the release path). It prints 'FAIL: schedule'. FIRST diagnose: read the toy and the code it tests, say why the schedule case fails (a code regression, a changed page or setting it reads, or the toy), name the merge that most likely started it with evidence (it was already red at 04:41 PT tonight), and send that to operation-mac. THEN fix the cause at the same strength: no check loosened, no retry, with a negative control

- Slug: aut-email-regression-fix
- Touches: skills, dev/toy
- ETA: 460 active minutes (estimate 368m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given the pull request, then it names the cause of 'FAIL: schedule' with the failing line and evidence, and the merge that most likely started it
2. Given the row on this branch in CI, then it passes, and a negative control shows the schedule case still fails when the schedule really is wrong
3. Given this goal's diff, then only the files the cause needs and the goal's record files change, every script stays under 20,480 bytes, and docs.py check and criteria.py render --check pass

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
