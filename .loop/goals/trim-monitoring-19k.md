# Bring sessions.py (20,000), operate.py (19,974) and reply_hook.py (19,866) to 19,000 LF bytes or less by text trims only (HLT-11.4, #4653)

- Slug: trim-monitoring-19k
- Touches: skills/workflow-monitoring/scripts/sessions.py, skills/workflow-monitoring/scripts/operate.py, skills/workflow-monitoring/scripts/reply_hook.py
- ETA: 225 active minutes (estimate 177m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given main after this goal, when git ls-tree -l reads the three scripts, then each is at or under 19,000 bytes and scripts-a-monitoring-under-19000 passes
2. Given the touched scripts, when the operate, reply-hook and session toys run before and after, then every output is unchanged, with a negative control that a one-line behaviour change fails a toy
3. Given this goal's diff, then no shipped file is added, no touched script is over 19,000 bytes or larger than on main, net regression rows are 0 or fewer, and no requirement text changes

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
