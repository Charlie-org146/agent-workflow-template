# MON-5: The operation session emails the owner on a new Needs-you item, a stopped or past-ETA goal, or a merged and released goal, through mail.py, off by default and machine-local (#4671, owner o77)

- Slug: email-notify
- Touches: not declared

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a check-in with a new Needs-you item, a stopped goal and a merged goal, with notification on, when it runs, then one email per new event goes out through mail.py naming the goal and the owner's action; a repeat sends nothing; with notification off nothing is sent
2. The Monitoring page states the rule (a sub-bullet under MON-5 or MON-8, since Monitoring is at criteria_max), the setting is in the settings table off by default with a test row, and the new wording goes to the owner for review
3. Notification is on for this PC, and a milestone to-do covers turning it on for the Mac

## Verify by hand

<!-- Numbered steps a person can follow, each with an Expect: line. -->
