# merge-queue-ci design

Problem: regression-pr.yml reports its required check only for pull_request and branch pushes, so a GitHub merge-queue branch (merge_group event) would wait forever for a check that never reports (REL-13 prerequisite, TD219).

Approaches:
1. Add `merge_group: types: [checks_requested]` to the NARROW template in lanes_cli.py (two lines), regenerate regression-pr.yml. Cost: ~45 bytes, paid back by trimming one comment. Risk: none while the queue is off.
2. A separate merge-queue workflow. Costs a new shipped file and a second check name that the ruleset would have to require.

Chosen: 1. Same job and check names. actions/checkout@v4 checks out github.sha by default, which for merge_group is the merge-group head, and the affected lane runs on it as for a pull request. pull_request is untouched.

Done lines: (1) `on:` lists merge_group beside pull_request, names unchanged, committed file equals generated text. (2) toy asserts merge_group + types, no ref override, and that a copy with merge_group stripped fails the assertion (negative control), added to the existing ls-narrow-triggers row, so net rows are 0. (3) lanes_cli.py is 18,662 LF bytes, smaller than main's 18,674; no new files, no requirement text changed.

Open questions: none.
