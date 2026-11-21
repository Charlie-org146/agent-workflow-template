Fixes #5680. Built by the Codex fallback, then taken through the full plan and review steps.

## What this widens

dev/toy/test-who-merges.py now accepts one more caller of merge.py: mailbox.py, in addition to worker.py. TD499 and PR 5608 intentionally added mailbox.py's tick-job path, which starts merge.py for a job the operation session wrote, at the job's exact head. The old assertion (only worker.py may start merge.py) rejected that intended behavior, so main's test fails (issue 5680). Only the test and this goal's own records change: no product script, no regression row, no known-list change.

## What the test checks

- Callers: among skills/workflow-monitoring/scripts and skills/workflow-delivery/scripts, exactly worker.py and mailbox.py may name merge.py. No scanned file, worker.py included, may spell a direct `gh pr merge` (a list or tuple with `pr`, `merge` adjacent, the text, or a shell string).
- mailbox.py structure: the MERGE assignment may build a path but never run a command; its one launch is inside resume(); resume() is called only by cmd_tick(), and no alias or callback of resume() exists.
- mailbox.py behaviour: the real resume() and cmd_tick() source runs with stubs. merge.py runs only for a waiting, armed, green job at its exact head, with argv `merge.py <job id> --go-head <job head>`, and gh_json must be asked for the job's own PR. It never runs for: no job file, an empty record, a nonwaiting record, a string PR, an unarmed job, a moved head, pending checks, red checks, one green check beside a pending or a red one, commit-status PENDING or FAILURE, a PR that is MERGED or CLOSED, gh_json returning None, or an empty check list (17 cases). Each case also checks the record it leaves behind (waiting, green, red, done or armed), and the armed job is not merged again by the next tick.
- 21 negative controls run on every execution and each must be rejected: a third script naming merge.py; the job-record guard removed; `gh pr merge` as a helper call, with a `-R` option, as adjacent tuple items, as a shell string, and in worker.py; the legacy `"pr", "merge"` and `"merge.py"` text in a comment; in a mailbox copy a `gh pr merge` call with an admin flag in another function, the legacy text in a comment, a second MERGE reference, a second resume() caller, a resume alias, the launch moved out of resume(), and a MERGE assignment that runs a command; and mutants of resume() that drop the OPEN check, the empty-checks guard, the None and empty-checks guards, change the pending test from any to all, or query another PR number.

## Evidence

- Main's test against this tree fails, naming mailbox.py as a caller: `FAIL: only worker.py (the worker's own exit) starts merge.py among the monitoring and delivery scripts: ['mailbox.py', 'worker.py']`.
- This branch's test: 35 PASS lines, 0 FAIL, exit 0.
- dev/toy/test-restart-tick.py (the watcher integration test: head matching, pod propagation, repeat ticks): 21 PASS, exit 0.
- The test header says what the scan is not: a tripwire against accident for enumerated spellings, not a proof of exclusive merge authority; it scans only the two script folders above (workflow-release, workflow-health, workflow-docs, workflow-regression and workflow-setup are not scanned); it does not cover a REST merge, a GraphQL mutation, an import or runpy of merge.py, concatenated strings, a flag between the words, a single-quoted 'merge.py', subfolders or shell scripts; and a docstring in a scanned script that says "pr merge" would fail it. It is coupled to the shape of resume() and cmd_tick(), and says so when that shape changes.

## Known gaps and follow-ups

- The test does not check who wrote a watcher job file; that gate is proctree.require_operation in mailbox.py's cmd_watch and is out of scope here.
- merge.py's own refusal of a missing or mismatched --go-head is tested elsewhere: dev/toy/test-merge-guard.sh (the #5171 --go-head cases) and dev/toy/test-merge-batch.sh.
- The existing row who-merges-report (issue 5299, OPS-1) runs this test and is on the known list (.loop/regression-known.tsv). When this merges it prints FIXED, and its known-list line comes off in the next known-list removal PR, owned by operation. Do not remove the line before this PR merges, or the row turns red on main; while the line stays, a later failure of the row is reported as KNOWN, not as a failure. No new row is added here (operation-mac, 2026-11-20 19:27).
