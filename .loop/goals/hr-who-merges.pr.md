Fixes #5680. Built by the Codex fallback

This widens what dev/toy/test-who-merges.py accepts by allowing one more caller of merge.py: mailbox.py, in addition to worker.py. TD499 and PR 5608 intentionally added mailbox.py's tick-job path, which merges a job written by the operation session at its exact head. The old assertion rejected that intended behavior.

The test checks that mailbox.py's launch is inside resume(), then exercises it through cmd_tick() with watcher job files. Missing records, nonwaiting records, invalid PRs, unarmed jobs, moved heads, pending checks and red checks must not merge; an armed green job must invoke merge.py for its own id and exact head. Other callers remain forbidden. Product scripts are unchanged.

Negative controls use the same validator: a toy third script starting merge.py is rejected, and a toy mailbox.py copy with its waiting/PR job-record guard removed is rejected for merging nonwaiting and invalid-PR jobs.

Validation:
- python3 dev/toy/test-who-merges.py: 0 FAIL, exit 0; both negative controls rejected as expected.
- python3 skills/workflow-docs/scripts/docs.py check
- python3 skills/workflow-docs/scripts/criteria.py render --check
- python3 dev/package.py --static
