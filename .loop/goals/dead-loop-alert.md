# A goal whose worker's retry loop died is flagged STALLED in the check-in

- Slug: dead-loop-alert
- Touches: skills/workflow-monitoring/scripts/checkin.py, skills/workflow-monitoring/scripts/proctree.py, dev/toy, .loop/regression.tsv, docs/wiki

## Done lines

Frozen. A wrong done line needs a new goal.

1. The check-in flags a live goal whose log has not moved for longer than silent_minutes while no goal.py, flow.py or lane process for that slug is running, as 'STALLED <slug>: no process since <time>; restart <worker>', under Needs you, with a toy case proven red (#4359)

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
