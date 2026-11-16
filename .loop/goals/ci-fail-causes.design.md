# Design: ci-fail-causes

Problem: the full CI regression run fails about 100 rows with no cause on record (#4516, #4515).

Approach: print each failing row's last 20 lines to the job log as well as the summary (the summary cannot be read through any API), rerun, group the failures by their first failing line, and give each group an outcome. Chosen groups: one fix here (the CI block ignored TOY_SKIP_FILE, so 22 macOS-only rows read FAIL), and eight filed groups with their rows. No row is marked known: none has a real external reason.

Done lines: line 1 is the groups file and the #4516 comment; line 2 is the fix plus the issues #4553 to #4560.
