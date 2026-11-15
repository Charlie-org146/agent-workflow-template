# Fix health.py file's crash on close and reopen, and fix or close with proof the non-Backlog health findings that do not need the owner

- Slug: health-leftovers
- Touches: skills/workflow-health, skills/workflow-monitoring/SKILL.md, skills/workflow-monitoring/references, dev/toy, docs, .loop

## Done lines

Frozen. A wrong done line needs a new goal.

1. health.py file builds only the argument list of the action it runs, so a close or reopen no longer crashes, proven by a toy case seen red
2. The monitoring SKILL.md is 150 lines or fewer and the requirements-rows, defect-test and nightly findings are fixed or closed with proof, or marked an off-machine to-do
3. #3822, #347 and #3903 are left alone, no reviewed requirement text changes without the exact sub-bullet sent first, every file stays at or under 19,000 bytes and the package at 98 files or fewer

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
