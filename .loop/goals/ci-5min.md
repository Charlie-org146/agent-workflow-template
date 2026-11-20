# The pull-request CI run finishes within 5 minutes (owner words 03:18, Operation TD352: every push waits about 15 minutes for the affected job before a merge queue that takes under a minute; #5458's affected run took 15 min 23 s). It serves DEL-17, Reviewed and on main since PR #5454: Push and PR CI: one run per push, same test selection, parallel jobs, 5 minutes. The goal cuts the affected job's time budget from 15 to 5 minutes, splits the selected rows across parallel jobs so the 5 minutes cover as many rows as today's 15, names the rows not run and leaves them to the scheduled full suite, and lets a change that touches no code skip the heavy job. The final check that the ruleset requires is named affected and must stay named affected (a matrix of shard jobs needs a final job that depends on all shards and is itself named affected, so the required check context still matches). The change is made where regression-pr.yml is generated (NARROW in lanes_cli.py, currently 20,216 bytes: trim real content, no reformat, GRD-20, the file must not end larger than main). The smoke job small and its 11-second run stay as they are. No local lane while CI runs on the exact head; lane prep (Tests-table render, restamp) and a red proof for any row added run before the push (TD343). ETA frozen at 45 minutes to a pushed PR

- Slug: ci-5min
- Touches: skills/workflow-regression/scripts/lanes_cli.py, .github/workflows/regression-pr.yml, dev/toy/test-local-schedule.sh
- ETA: 525 active minutes (estimate 420m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a pull request, when CI runs, then the affected check (same name) is green or red within 5 minutes of the push, with the selected rows split across parallel shard jobs and one final job named affected that depends on all of them
2. Given rows selected but not run inside the 5-minute budget, then the run prints how many were left and names them, and the scheduled full suite runs them (as the 15-minute run did)
3. Given a change that touches only documents or the goal's own record files, then the heavy job is skipped (the final affected job still reports success) and the small smoke job and the queue are unchanged
4. Given this goal's diff, then only lanes_cli.py (no larger than on main), the generated regression-pr.yml, the toy or row guarding the workflow and the goal's own record files change, any added row has its red proof recorded, and the docs check passes

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
