# Finished goals leave the check-in: the MON-14 check requires only live goals (running, holding, queued, waiting on the owner, or merged since the previous check-in), and a goal whose PR merged or that is retired or stopped closes for good and drops off the graph.

- Slug: checkin-tidy
- Touches: skills/workflow-monitoring/scripts, docs/wiki/Monitoring.md, dev/toy

## Done lines

Frozen. A wrong done line needs a new goal.

1. The MON-14 check in checkin.py and graph.py requires only live goals: running, holding, queued, waiting on the owner, or merged since the previous check-in; a goal merged before the previous check-in is never required and its [x] line may be dropped.
2. A goal whose PR merged or whose status is retired or stopped closes for good and the graph stops listing it; today's stale goals are closed after checking each one's PR and worker state, except the parked general-asks.
3. MON-5 and MON-14 each carry one sub-bullet saying so, and toy cases proven red cover both; every script stays at or under 19,000 bytes and the package at 98 files or fewer.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
