# Delivery small fixes: plan text in the PR body, Verify-by-hand refusal, budget stop waits, mend only for unusable sessions, machine check GAP when skills lag (gap cluster G20: DEL-1.2, DEL-7.3, DEL-7.4, MCH-1.5, issue 4781; TOP-DECISION 156; PC record o242 under owner o355).

- Slug: delivery-small-fixes
- Touches: not declared
- ETA: 260 active minutes (estimate 208m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. The pull request body carries the goal's plan text, and pr refuses while Verify by hand is still the empty comment
2. A budget stop sets the goal waiting and puts it under Needs you with the raise command
3. mend gives a goal a fresh session only when the failure was an unusable session or tool, and a row covers the planning-tool case
4. machine check prints a GAP line when the skills checkout is behind origin
5. Every changed row is proven seen-red, and no script passes 19,000 LF bytes

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
1. In a scratch goal whose Verify by hand is only the empty comment, run `goal.py pr SLUG`.
   Expect: REFUSED (no try used): Verify by hand is still the empty comment (VERIFY_EMPTY).
2. Fill in one numbered step with an Expect: line and a plan file `.loop/goals/SLUG.plan.md`, run `goal.py pr SLUG` again.
   Expect: the PR body has a `## Plan` block with the plan text.
3. Run `python3 dev/machine.py check` on a machine whose skills checkout is behind origin.
   Expect: a `GAP skills-checkout:` line with `-> run: git -C ... pull`.

## Notes for the PR

- Behaviour change: `goal.py pr` now refuses (VERIFY_EMPTY, no try used) when Verify by hand is still the empty comment.
- In-flight goals are spared: the refusal binds only a goal frozen after 2026-11-19T14:54Z, read from the commit that first added its goal file (`mend.FROZEN_AFTER`). A goal frozen before that passes `pr` with an empty section. No new marker or sync is written.
- fit.py 19,827 to 19,815 bytes; dev/machine.py 19,774 to 19,728; mend.py 18,916.
- #5188 reindents mend.py wholesale; it absorbs these hunks at its slot.
