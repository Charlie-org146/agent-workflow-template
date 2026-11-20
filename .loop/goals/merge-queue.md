# merge.py enqueues a green pull request at its GO'd head into GitHub's merge queue (`gh pr merge --merge --auto --match-head-commit <GO head>`, which queues it when main's ruleset requires a queue), waits for the queue to merge it, then cuts the release as today; with the queue off it merges as today; it records each PR's green-to-main time and health reports the median against 15 minutes (REL-13 rewritten, TD219, o282; GitHub merge queue, Uber SubmitQueue, Zuul)

- Slug: merge-queue
- Touches: skills/workflow-release/scripts/merge.py, skills/workflow-health/scripts/rules.py, docs/wiki/Release.md, docs/wiki/How-to-use-Release.md, dev/toy/test-merge-guard.sh, .loop/regression.tsv, skills/workflow-release/scripts/autorelease.py, skills/workflow-monitoring/scripts/graph.py
- ETA: 450 active minutes (estimate 358m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given the Release page, then REL-13 is revised through criteria.py to read: "Pull requests merge through GitHub's merge queue when main's ruleset requires one. The release step enqueues a green pull request bound to the exact head the GO named and never bypasses the queue; the queue merges it only after the required checks pass on the merge-group commit; then the release is cut. With no queue required, the release step merges the GO'd head itself as before. Health reports the median time from a green pull request to main over the last 20 merges, 15 minutes or less." The revision goes for approval (owner or operation-top under DOC-2), the build starts after it is recorded, and no other requirement text changes
2. Given a toy repo with a fake gh reporting a ruleset that requires a merge queue and a green PR with a GO head, when merge.py runs, then it calls `gh pr merge --merge --auto --match-head-commit <head>` once, never a plain direct merge, waits until the fake gh reports the PR merged, then releases; with the head moved after the GO it refuses naming both heads; with the fake ruleset requiring no queue it merges directly as today; with a negative control that the old direct-merge-only path fails the queue case
3. Given merged PRs whose checks finished 10 and 25 minutes before they reached main, when health check runs, then it prints "MERGE-TIME median N min (target 15)" with a WARN above 15 and UNREAD when the data can't be read, never green
4. Given the PR body and the How-to page, then they list the owner's ruleset values for main exactly: require merge queue; merge method merge commit; build concurrency 3; minimum group size 1; maximum group size 3; all entries must pass required checks; required checks: the regression-pr affected job (both its pull_request and merge_group runs) and GitGuardian; and say the owner flips it only after this goal is on main; the goal changes no repo setting
5. Given a merge_group commit in the toy and on the real repo after merge-queue-ci lands, then the goal lists which required checks actually report on merge_group and makes only those required for the queue; if GitGuardian (an app check) does not report there, it stays required on pull_request only and the PR body says so, so no queue entry waits forever
6. Given a ruleset that requires a merge queue, then the plan review settles how the release commit is cut (a release PR through the queue, a release-step bypass the owner sets, or a tag-only release) so a direct push to main is never refused and three in-flight entries never collide on the version, and the toy proves that path; any bypass is listed with the owner's ruleset values
7. Given main has no ruleset today (TD224), then the PR body gives the owner the full recipe for a new ruleset targeting main: Require merge queue (merge commit, build concurrency 3, group size 1 to 3, all entries must pass), Require status checks naming exactly the checks that report on both pull_request and merge_group, and any bypass the release step needs; and the plan review records that GRD-6 is enforced only by local hooks until the owner creates it
8. Given a ruleset that requires a merge queue, when merge.py --batch runs, then it refuses with one line pointing to the queue (GitHub builds merge groups itself), and merge_batch keeps working only for a repo with no queue; with a negative control that a no-queue repo still batches
9. Given this goal's diff, then no shipped file is added, merge.py is not larger than on main (18,994: the enqueue path is paid for by trimming merge.py's header comments and the waiting loop it replaces), no touched script is over 19,000 bytes, net regression rows are 0 (assertions folded into the existing merge-guard and health rows), and no requirement text changes beyond the REL-13 revision above

## Verify by hand

1. Open docs/wiki/How-to-use-Release.md and read the Playbook "Main's merge queue ruleset".
   Expect: it lists require merge queue, merge commit, build concurrency 3, group size 1 to 3, all entries must pass, the required checks, and says the owner flips it after this change is on main.
2. Run `bash dev/toy/test-merge-guard.sh | grep -i queue` on Linux.
   Expect: PASS lines for the one `--merge --auto --match-head-commit` call, the dropped entry, the unreadable rules, the batch refusal and the no-queue direct merge.
3. Run `python3 skills/workflow-health/scripts/health.py check --group performance`.
   Expect: a `MERGE-TIME median N min (target 15)` row (WARN above 15, UNREAD if gh can't be read).
4. Run `tr -d '' < skills/workflow-release/scripts/merge.py | wc -c`.
   Expect: 18994 or less.
