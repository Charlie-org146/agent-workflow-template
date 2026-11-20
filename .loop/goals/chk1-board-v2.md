# CHK-1's board sentence gains a progress bar for every release-goal step and a Merge queue section (owner o665, wording approved by operation-top under DOC-2's delegation, TD462). Old: 'Release goals (short: one line, one bar, an ETA, at most five steps); Task queue'. New: 'Release goals (short: one line, one bar, an ETA, at most five steps, each step with its own progress bar); Merge queue (a card per pull request in columns: Building, PR checks, In the queue, Merged today, Held, read from GitHub); Task queue'. Only that part changes

- Slug: chk1-board-v2
- Touches: docs, README.md, .loop
- ETA: 425 active minutes (estimate 340m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given CHK-1 on this branch, then its text is the new sentence exactly, revised with criteria.py revise using record o665, and its review mark is set under DOC-2's delegation and listed in the PR body
2. Given README, Home and the CHK-1 page on this branch, then each renders the new sentence, and criteria.py render --check and docs.py check pass
3. Given this goal's diff, then nothing outside CHK-1's text, its renders and the goal's record files changes

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
