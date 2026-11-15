# Plan: dead-loop-alert

Checked: checkin.py's Needs-you loop prints the "silent" and "held" lines from graph.classify; graph.silent_for/last_spoke/silent_limit give the quiet time and limit; board_status.py already reads processes for machine_line.
Build: 1. board_status.slug_busy(slug) and stalled_line(run, state, at, cfg, worker). 2. checkin.py: one `if line := bs.stalled_line(...)` before the other states, docstring updated, comments trimmed so the file is net -6 bytes. 3. test-silent-worker.py: LOOP_PROCS for the old MON-8 cases, three new cases. 4. Rows stalled-no-process-4359 and stalled-process-quiet-4359 (MON-8), each seen red. 5. Render, docs check.
Could break: the MON-8 toy (it now sets LOOP_PROCS); a slug in the command line of an unrelated process (counts as busy, no alarm). Out of scope: the retry loop, watch.py. No owner decisions.
