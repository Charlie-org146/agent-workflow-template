# Plan: checkin-zh-cn-crash

Checked against the code: `skills/workflow-monitoring/scripts/board_status.py` holds `slug_busy` (PowerShell and `ps` reads),
`stalled_line` (its only caller), `machine_line` (`tasklist` and `ps` reads) and `memory` (`vm_stat`). `dev/toy/test-silent-worker.py`
shows the toy pattern; rows live in `.loop/regression.tsv`.

## Build steps
1. In board_status.py add `_run_text(argv, timeout)`: `subprocess.run(argv, capture_output=True, timeout=timeout).stdout`
   decoded with `errors='replace'` (empty string when stdout is None).
2. Use it in `slug_busy` (PowerShell and `ps`), `machine_line` (`tasklist`, `ps`) and `memory` (`vm_stat`).
3. Add `dev/toy/test-slug-busy-bytes.py` (header `# windows: ok`, `# reads:` board_status.py): patches `subprocess.run` to return
   bytes with 0xa1, checks slug_busy True for the goal's line and False for another slug, checks `checkin.render` prints the
   check-in with no STALLED for that goal, and the strict-decode negative control.
4. Add one row to `.loop/regression.tsv` and prove it red on main with `regression.py red`.

## Tests per done line
Done line 1: the toy above; its row is seen failing on unfixed main (UnicodeDecodeError or wrong result) and passing after.

## What could break
Callers that read `.stdout` as str keep working: the helper returns str. A test that patches `subprocess.run` with a str
stdout would break; none found (tests use LOOP_PROCS and LOOP_MACHINE).

## Out of scope
`text=True` reads of git, our own scripts and Unix `ps` elsewhere in skills/; health's `controls.py` and `enforce.py` that run
repo-defined commands.
