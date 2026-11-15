# A pr lane that ends BASE_MOVED, and time a goal spends held in the pr queue, on a hold, on an owner answer or after a stop, is never charged to its time budget (#4261, #3878)

- Slug: budget-fair
- Touches: skills/workflow-monitoring, skills/workflow-delivery, dev/toy

## Done lines

Frozen. A wrong done line needs a new goal.

1. A pr lane that ends BASE_MOVED is charged as held time, not against time_budget_minutes; a toy that replays five BASE_MOVED lanes leaves the budget unspent (#4261).
2. Time held in the pr queue, on a hold, on an owner answer or after a stop is never charged to the time budget; a toy proven red covers it, and what #3878 still has open is closed (#3878).
3. Every script this goal touches stays at or under 19,000 bytes, with new code in a module no other goal is trimming.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
