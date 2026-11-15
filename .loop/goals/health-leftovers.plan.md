# Plan: health-leftovers

## Build steps
1. `file.py args_of`: build only the entry for `act["kind"]`; keep it no larger than today. Toy `dev/toy/test-health-file-actions.py` (open, update, reopen, close through `args_of`, and a fake `gh` for `apply`); row `file-close-no-crash` (HLT-4), seen red by putting the eager dict back.
2. monitoring SKILL.md: join two Rules bullets (151 to 150 lines); check the docs rows and `review-findings-skill-lines`.
3. Criterion rows: `set13-hooks-once-bullet` (SET-13), `mon16-machine-line`, `mon16-memory-floor`, `mon16-checkout-ff` (MON-16), `mon17-this-pod-only` (MON-17), each reusing the toy command of its existing row, each seen red with the existing break; `del13-review-hold` as a `draft` row (no test exists).
4. Defect rows `defect-3854-long-pr-body` (link issue 3854, body-file toy) and `defect-3939-lane-skips-node-modules` (link issue 3939), seen red.
5. Re-render Tests and the page tables; `docs.py check --own`; health check shows the four requirement rows, both defect-tests and the SKILL.md line gone.
6. Comment #3810 as an off-machine to-do (the Actions regression shards fail; Regression: issues are pool-09's).

## Tests (one per done line)
- Done line 1: `file-close-no-crash`, seen red.
- Done line 2: each new row seen red; `health.py check` no longer lists #4223, #3803, #3804, #4142, #4143, #3879, #4025.
- Done line 3: the diff touches no wiki requirement text, no #3822/#347/#3903 file, and no script over 19,000 bytes beyond file.py's existing size.

## What could break
- `file.py` is the writer of every health issue: the toy covers each kind. The reuse of an existing toy command in a second row doubles its lane time slightly.
- A joined SKILL.md bullet changes no meaning.

## Out of scope
Building DEL-13's review hold, trimming file.py to 19,000 (scripts-c), the Mac, Documentation stale findings, the failing Actions shards.
