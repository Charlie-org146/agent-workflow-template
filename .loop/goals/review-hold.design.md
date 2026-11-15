# Design: review-hold

## Problem
With auto_merge on, merge.py merges a finished goal's pull request without the operation session having read the diff
(DEL-13, issue 2875; health's draft-row finding 3803). A repo that wants that read has no switch for it.

## Approaches
1. Record the review in the goal's run state and check it in merge.py through a new small `review.py` (record, held).
   Cost: one new script (the package goes 97 to 98), a few lines in merge.py, the board and check-in. Risk: low.
2. Put the record in goal.py or sessions.py. Cost: both sit near 19,000 bytes, so each would need a trim first, and the
   merge path would import a monitoring script. Risk: more files touched, a package of unrelated edits.

## Chosen
Approach 1. `review_hold` is a repo setting in .loop/config.json, off by default. merge.py, once the pull request is open
and its head is the tested head, calls `review.held(cfg, state, head)`: it returns nothing when the setting is off or a
review recorded for exactly this head exists, else a REVIEW_HOLD refusal, and the goal stays done (not failed) with
`review_wait` set, so merge.py run again after the record merges it. `review.py record SLUG` is the operation role only:
LOOP_ROLE=worker or a path inside a goal worktree is refused and writes nothing. It stores the pull request head it read
(`gh pr view`); a later push changes the head, so the record no longer matches and the hold applies again.
The board's Issues (board_lines.issues) and the check-in's Needs you show "merge waiting on review" with the command.

## Each done line
1. merge.py hook + review.held, toy: hold blocks, off unchanged.
2. review.py record, operation only, head-bound; toy: worker refused, nothing written; push voids it.
3. board_lines.issues line, checkin Needs you line, settings.py row; toys read the output.
4. Three toys proven red with `regression.py red`, a DEL-13 criterion row, byte limits kept (merge.py needs a trim).

## Open questions
None for the owner: the setting is per repo (config.json), and a per-goal switch is not built.
