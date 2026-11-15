# scripts-a plan

Files: the 14 scripts over 19,000 LF bytes in skills/workflow-delivery/scripts (guards, goal, role, lanekit, private, fit, flow) and skills/workflow-monitoring/scripts (watch, sessions, reply_hook, worker, pool, board_page, graph). All exist.

Steps:
1. Per script: cut comments, docstrings and dead or repeated text; keep every behavior and every printed token (toys grep them).
2. Run each script's toys (dev/toy tests that read it) after each trim.
3. Add regression row scripts-a-under-19000 (python3 -c, shell-agnostic): every script in both folders is under 19,000 LF bytes; seen red by temporarily lowering the bound.
4. Confirm file count is 98 or fewer.

Could break: a toy greps a trimmed comment or message. Out of scope: narrow.py, lanes.py, other skills.

VERDICT: self: approve
PENDING: none
