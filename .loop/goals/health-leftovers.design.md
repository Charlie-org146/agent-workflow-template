# Design: health-leftovers

## Problem
`health.py file` crashes on any close or reopen (`args_of` builds all four argument lists eagerly and the "open" list reads `act["label"]`). The sweep also left the non-Backlog health findings that need no owner decision: monitoring SKILL.md at 151 lines, four requirements without a criterion row (DEL-13, SET-13, MON-16, MON-17), two fixed defects without a defect row (#3854, #3939), and a nightly finding.

## Approaches
1. Fix each finding in the code it names (build DEL-13's review hold, rewrite tests). Cost: large, and DEL-13 is a feature, not a leftover. Risk: scope creep into reviewed requirements.
2. Fix the crash, trim the file, and add rows that point at tests that already exist (a criterion row for a requirement whose behaviour a toy already proves; a defect row linked to the issue whose fix a toy already proves), each seen red. Cost: small. Risk: a row only covers what its toy covers, so each row's description says which bullet it proves.

## Chosen
Approach 2. DEL-13 (review hold) has no code or toy anywhere (grep finds nothing), so it gets a `draft` row naming the missing test, which satisfies "has a row" honestly and fails nothing; it is not built here. SET-13 gets a criterion row on the hooks-once toy (its other bullets stay unproven and are named in the row); MON-16 gets rows on the three machine-status toys (Machine line, memory floor, checkout fast-forward); MON-17 on the machine-status pod toy. #3854 and #3939 get defect rows linked to the issue URLs, reusing the body-file and node_modules toys. #4223: join two Rules bullets in monitoring SKILL.md (151 to 150). #3810 (nightly): the Actions regression run itself fails on its shards (the Regression: issues, pool-09), so it is an off-machine to-do, commented on the issue. #143 (done lines without rows) is the live goals' own done lines, history once a goal finishes; it clears when this goal merges.

## What each done line needs
1. A toy `dev/toy/test-health-file-actions.py` that calls `args_of` for open, update, reopen and close and the real `apply` on a fake gh for a close and a reopen; row `file-close-no-crash` seen red by reverting the dict.
2. Rows added with `regression.py add` (each seen red with `regression.py red`), the SKILL.md at 150 lines, #3810 commented as an off-machine to-do; closes with proof after the merge.
3. No change to #3822, #347, #3903; no reviewed requirement text; file.py stays at or under its current size (it is 19,621 bytes: scripts-c owns trimming it).

## Open questions
None for the owner. DEL-13 stays unbuilt: a `draft` row is the honest state, and filing the build as a backlog item is the ship step's job.
