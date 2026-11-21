# DEL-19 really adopts GitHub closing keywords (DEL-21; v2.0 part 3, TD531): a defect or fix goal's pull request must name its issue with a GitHub closing keyword (Fixes, Closes or Resolves #N); the plain and goal.py pr routes refuse a defect goal whose PR body has none, and health's defect-tests rule reads the merged PR's closingIssuesReferences first and the goal file only as a fallback; then DEL-19's Follows line for closing keywords can say adopted

- Slug: adopt-closing-keywords
- Touches: skills, dev/toy
- ETA: 295 active minutes (estimate 235m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a defect goal whose PR body lacks a closing keyword, then the pr route refuses with one line naming the fix; given Fixes #N, it passes; a non-defect goal is unaffected (toy, negative control)
2. Given the pull request, then its row is SEEN RED with the check removed, the PR body proposes the exact DEL-19 Follows wording change for the owner without editing reviewed text, and docs.py check and criteria.py render --check pass
3. Given this goal's diff, then no file is added to the package (100 files), no script newly crosses 19,000 bytes, every script stays under 20,480, and the private scan is clean

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
1. Run `bash dev/toy/test-defect.sh closing-keywords` and `bash dev/toy/test-defect.sh closing-unaffected`.
   Expect: both exit 0 with no output.
2. In a branch that adds a defect row linked to issue #88, save a PR body without a keyword (say `see issue #88`) and run `python3 skills/workflow-monitoring/scripts/pool.py closing BODYFILE`.
   Expect: `REFUSED: the PR leaves #88 open. Fix: add Fixes #88.` and exit 1; with `Fixes #88` in the file, `CLOSING OK` and exit 0.
3. Run `goal.py pr SLUG` for such a goal whose file has no closing keyword.
   Expect: `REFUSED: the PR leaves #88 open. Fix: add Fixes #88 to the goal file outside its done lines, commit, run pr.`
