# The PR regression workflow also runs on GitHub's `merge_group` event, so its required check reports on merge-queue branches; workflow trigger only, no behaviour change while the queue is off (REL-13 prerequisite, TD219, o282; GitHub merge queue)

- Slug: merge-queue-ci
- Touches: skills/workflow-regression/scripts/lanes_cli.py, .github/workflows/regression-pr.yml, dev/toy/test-automation.sh, .loop/regression.tsv
- ETA: 235 active minutes (estimate 187m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given `regression.py workflow` generating regression-pr.yml, then its `on:` lists `merge_group:` (types checks_requested) beside `pull_request:`, the job and check names are unchanged, and the committed .github/workflows/regression-pr.yml equals the generated text
2. Given a merge_group event, then the job checks out the merge-group head (github.sha) and runs the same affected lane it runs for a pull request, and for a pull_request event nothing changes; with a negative control that a generated workflow without `merge_group` fails the toy
3. Given this goal's diff, then no shipped file is added, lanes_cli.py (18,674) stays under 19,000 bytes and not larger than on main beyond the trigger lines it pays for by trimming comments, net regression rows are 0 (an assertion added to an existing workflow row), and no requirement text changes

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
