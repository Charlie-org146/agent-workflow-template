# review-hold plan

1. New skills/workflow-release/scripts/review.py: `held(cfg, state, head)`, `wait(state)`, `record SLUG` (operation role only).
2. merge.py: import review, call it after the base_moved check; trim its docstring to stay at or under 19,000.
3. board_lines.issues and checkin Needs you: a "merge waiting on review" line; settings.py: the review_hold row.
4. Toy dev/toy/test-review-hold.py with three legs (hold blocks, recorded review merges, worker cannot record) plus board and check-in text; rows seen red with regression.py red; a DEL-13 row.
5. SKILL.md command map row for review.py; criteria.py render; docs.py check --own.

Out of scope: a per-goal switch, recording through goal.py or sessions.py.
Could break: merge.py size (trim first); the package file count (97 to 98).
