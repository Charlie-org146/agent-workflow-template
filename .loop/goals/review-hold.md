# Build the review hold of DEL-13 (#3803): a review_hold setting, off by default, under which the release step merges only after the operation session records that it has read the diff, and the board shows a merge waiting on review

- Slug: review-hold
- Touches: skills/workflow-release, skills/workflow-monitoring/scripts/board_lines.py, skills/workflow-monitoring/scripts/checkin.py, skills/workflow-setup/scripts/settings.py, dev/toy, .loop, docs/wiki

## Done lines

Frozen. A wrong done line needs a new goal.

1. With "review_hold": true in .loop/config.json, merge.py refuses with REVIEW_HOLD and merges nothing until the operation session records a review of the pull request's head; with the setting off or absent merging is unchanged
2. review.py record SLUG records that review only for the operation role: a worker (LOOP_ROLE=worker, or inside a goal worktree) is refused and nothing is recorded, and a push after the record voids it
3. The live board's Issues and the check-in's Needs you say merge waiting on review for a goal held this way, and review_hold is a listed setting, off by default
4. Toy cases proven red cover the hold blocking, a recorded review letting the merge go, and a worker unable to record; a DEL-13 criterion row exists so health's draft-row finding 3803 clears; every script stays at or under 19,000 bytes and the package at 98 files or fewer

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
