# merge-queue: design

## Problem
`merge.py` merges a green PR with a plain `gh pr merge --merge --match-head-commit`. Once the owner turns on GitHub's merge
queue for main, a plain merge is refused or bypasses the queue, and the release commit (a direct push, or a release PR
merged the same plain way) breaks too. Main has no ruleset today (TD224). Required checks must also report on the
`merge_group` event, or a queue entry waits forever.

## Approaches
1. Enqueue in merge.py and keep the release as is: `gh pr merge --merge --auto --match-head-commit <GO head>` when main's
   ruleset requires a queue, wait for MERGED, then release. Cheap, but the release step's direct push is refused by the
   same ruleset (GH013), so the release fails after a good merge.
2. Enqueue, then run the release through the existing release-PR path (`merge.advance`: `release/vX-<slug>` PR) and send
   that PR through the same enqueue helper. No bypass for the owner to set, no new file. The release PR is cut only
   after the goal PR is MERGED, from main's tip, under `merge_lock`, so three in-flight entries never share a version.
3. Tag-only release (no VERSION commit): breaks `autorelease`'s VERSION/CHANGELOG contract and REL-3; too large.

**Chosen: 2.** A release-step bypass stays the fallback the owner may set; it is listed with the ruleset values, not built.

## Decisions
- Queue detection: `gh api repos/{owner}/{repo}/rules/branches/<base>` has a rule of type `merge_queue` (sibling of
  `autorelease.protected`). Unreadable means "no queue" only when the call succeeds with no such rule; a failed call
  refuses (never silently a direct merge).
- Enqueue: one call, `gh pr merge <pr> --merge --auto --match-head-commit <head>`, where head is the GO head or the
  tested head. Then poll the PR until MERGED; CLOSED or a head change refuses. The waiting loop it replaces and the
  header comments are trimmed to keep merge.py at or under 18,994 LF bytes.
- Release under a queue: `advance` merges the release PR through the same helper; `protected()` is true under a queue
  ruleset, so the existing path is taken. GRD-6 is enforced only by local hooks until the owner creates the ruleset;
  the plan review records that.
- Required checks on `merge_group`: `regression-pr` needs a `merge_group` trigger (merge-queue-ci adds it); its
  `affected` job then reports on both events. GitGuardian is a GitHub App check that reports on PR commits; it is
  expected NOT to report on the merge-group commit, so it stays required on `pull_request` only and the PR body says so.
  After merge-queue-ci lands, list the contexts on a real merge-group run and require only those.
- Health: `rules.py` adds MERGE-TIME: median minutes from a PR's last required check finishing to its merge into main,
  over the last 20 merged PRs (`gh pr list --state merged --json mergedAt,statusCheckRollup`); WARN above 15, UNREAD
  when the data cannot be read, never green. Size is paid for with the existing rule bodies.
- `--batch` under a queue refuses in one line pointing to the queue; no queue still batches.
- REL-13 is revised through criteria.py (owner record o283); no other requirement text changes. Net regression rows 0:
  assertions fold into the existing merge-guard and health rows.

## What each done line needs
1. criteria.py revision of REL-13 with --owner-record o283, before the build.
2. toy fake gh: ruleset with merge_queue, green PR; one `--auto --match-head-commit` call, no plain merge, waits for
   MERGED then releases; head moved refuses naming both heads; no-queue merges directly; negative control: old path.
3. rules.py MERGE-TIME rule and toy cases 10 and 25 minutes, WARN above 15, UNREAD.
4. PR body and How-to-use-Release list the ruleset values exactly (merge commit, concurrency 3, group 1 to 3, all
   entries must pass, required checks); the goal changes no repo setting.
5. Required-checks-on-merge_group list (toy merge_group commit; real repo after merge-queue-ci).
6. The release-commit path (approach 2) proved in the toy.
7. PR body carries the full new-ruleset recipe for main.
8. merge.py --batch refusal line and no-queue negative control.
9. Size: no new shipped file; merge.py not larger than 18,994; every touched script at or under 19,000 LF bytes.

## Open questions
- Does GitGuardian report on merge_group? Expected no; confirm on the real repo after merge-queue-ci lands.
- Whether `gh` on the owner's machine enqueues with `--auto` when the queue is on and checks already pass (it should);
  the toy fakes it, the first real merge proves it.
