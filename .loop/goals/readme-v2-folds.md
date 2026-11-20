# Five v2.0 requirement texts land verbatim, approved by operation-top under DOC-2's delegation with delegated records (TD462, TD464, TD468, TD472; owner o665, o666, o667): CHK-1 gains the step-ETA clause ('each step with its own progress bar and ETA, and whose ETA it is'); REG-4 gains 'No test stays parked' and pytest xfail(strict=True) in Follows; HLT-2 gains 'Release rules run before merge when they are fast' and 'GitHub required status checks: adopted'; MCH-1 gains 'A restart loses nothing' and 'Cloud sessions', with macOS launchd and Claude Code cloud sessions in Follows; DEL-17 gains '; from push to main takes at most 3 minutes, checks and queue together'. Exact texts are in operation-top's TD message, copied into the PR body

- Slug: readme-v2-folds
- Touches: docs, README.md, .loop
- ETA: 445 active minutes (estimate 353m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given CHK-1, REG-4, HLT-2, MCH-1 and DEL-17 on this branch, then each carries its new text exactly as approved, revised with criteria.py revise and reviewed with a delegated record, each record listed in the PR body
2. Given README, Home and each requirement's page on this branch, then each renders the new text, and criteria.py render --check and docs.py check pass
3. Given this goal's diff, then nothing outside those five requirements' text, their renders and the goal's record files changes

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
1. Run `grep -c "No test stays parked" docs/wiki/Regression.md README.md docs/wiki/Home.md`.
   Expect: at least 1 in each of the three files.
2. Run `grep -c "from push to main takes at most 3 minutes" docs/wiki/Delivery.md README.md docs/wiki/Home.md docs/wiki/Principles.md`.
   Expect: at least 1 in each file.
3. Run `python3 skills/workflow-docs/scripts/docs.py check | tail -1` and `python3 skills/workflow-docs/scripts/criteria.py render --check | tail -1`.
   Expect: DOCS OK: 16 pages, then TABLES OK.
4. Run `grep -n "^- \(REG-4\|HLT-2\|MCH-1\|DEL-17\|CHK-1\):" docs/wiki/*.md | cut -c1-90`.
   Expect: all five read Reviewed 2026-11-20.
