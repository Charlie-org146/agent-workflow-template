# Design: start-from-head

Problem: merge.py's wiki check (wiki.pending) audits a PR head in a temporary worktree (#4208) but runs docs.py from the main checkout's skills, so entry.py renders START.md from main's skill commands; a PR that adds skill commands carries a correct START.md that is refused as WOULD FIX (#4340, seen on adoption PR #4334).

Approach A: run the whole docs audit with the head's own docs.py. Rejected: a goal could then loosen the check that judges it (RUN_FROM_WORKTREE reasoning).
Approach B (chosen): keep main's docs.py for everything, but for START.md and the agent blocks replace the audit's "WOULD FIX ... (entry.py write)" lines by the head's own `entry.py check` verdict, run in the temp tree. Only the generated entry point is judged by the head's skills.

Done line: a PR that adds a skill command with its rendered START.md passes; a PR with a really stale START.md is refused; each with a toy case proven red (two rows). wiki.py was already over 19,000 bytes, so the change is net-negative in bytes (docstrings shortened). Out of scope: any other check, the installed skills.
