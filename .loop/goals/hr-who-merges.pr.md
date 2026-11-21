Fixes #5680. Built by the Codex fallback

This widens what dev/toy/test-who-merges.py accepts by allowing one more caller of merge.py: mailbox.py, in addition to worker.py. TD499 and PR 5608 intentionally added mailbox.py's tick-job path, which merges a job written by the operation session at its exact head. The old assertion rejected that intended behavior.

The test checks that mailbox.py's launch is inside resume(), that cmd_tick() is resume()'s only caller, and then exercises it through cmd_tick() with watcher job files. Missing records, nonwaiting records, invalid PRs, unarmed jobs, moved heads, pending checks and red checks must not merge; an armed green job must invoke merge.py for its own id and exact head. Adjacent string items `pr`, `merge` anywhere in a list or tuple identify a merge caller, including helper calls and gh options before the subcommand. The old plain-text checks remain an extra net over every scanned file; mailbox.py also rejects any gh pr merge form. Other callers remain forbidden. Product scripts are unchanged.

Negative controls all use the same validator and are rejected as expected:
- Third script starting merge.py.
- Mailbox waiting/PR job-record guard removed (nonwaiting and invalid-PR jobs merge).
- Third script calling `gh(["pr","merge","5"], root)`.
- Third script calling `subprocess.run(["gh","-R","x","pr","merge","5"])`.
- Third script with adjacent `pr`, `merge` in a tuple after another item, using single quotes.
- Third script containing only the legacy `"pr", "merge"` text in a comment.
- Third script containing only the legacy `"merge.py"` text in a comment.
- Mailbox copy calling `gh(["pr","merge","5","--admin"], root)` in another function.
- Mailbox copy containing the legacy `"pr", "merge"` text in a comment.
- Mailbox copy with a second MERGE reference outside its assignment and launch.
- Mailbox copy calling resume() from a function other than cmd_tick().
- Mailbox copy with the MERGE launch moved from resume() into another function.

Before the validator fix, the new controls exposed eight missed violations (the moved launch and second MERGE reference controls already rejected their mutations). After the fix, all twelve controls reject their mutations.

Validation:
- python3 dev/toy/test-who-merges.py: 0 FAIL, exit 0; all twelve negative controls rejected as expected.
- python3 skills/workflow-docs/scripts/docs.py check
- python3 skills/workflow-docs/scripts/criteria.py render --check
- python3 dev/package.py --static
