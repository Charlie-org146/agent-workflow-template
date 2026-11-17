# Design: checkin-zh-cn-crash

## Problem
`board_status.slug_busy` reads the Windows process list with `subprocess.run(..., text=True)`. PowerShell writes the console
code page (GBK on zh-CN), so a non-ASCII command line holds bytes such as 0xa1 that are not UTF-8. With PYTHONUTF8=1 the
text decode raises UnicodeDecodeError and the check-in dies (#4810). `machine_line` reads `tasklist` the same way.

## Approaches
1. Read bytes, decode with `errors='replace'`. One helper, no PowerShell change, works for any code page. Cost: a few lines.
   Risk: a replaced character in a line we only match with ASCII slugs and script names: none.
2. Force `[Console]::OutputEncoding = UTF-8` in the PowerShell command. Fixes this one call, leaves tasklist, adds quoting
   risk, and still raises if the encoding is ignored.

## Chosen
Approach 1: a `_run_text(argv, timeout)` helper in board_status.py that runs without text mode and decodes with
`errors='replace'`; `slug_busy` (PowerShell and `ps`), `machine_line` (tasklist, ps) and the `vm_stat` read use it. Other
`text=True` calls read git, our own scripts or `ps` on Unix and stay as they are (out of scope, kept small).

## Done line 1
A new toy `dev/toy/test-slug-busy-bytes.py` patches `subprocess.run` to return bytes containing 0xa1 and a goal line, then
checks `slug_busy` finds the goal (True) and a different slug is False (not the unreadable fallback), and `checkin.render`
prints the check-in with no STALLED line for a goal with a process. Negative control in the same toy: strict UTF-8 decode
of the same bytes raises, so the input really is not UTF-8. One regression row runs it; it is seen failing on main first.

## Open questions
None.
