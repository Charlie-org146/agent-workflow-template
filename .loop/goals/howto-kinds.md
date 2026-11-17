# DOC-18: How-to-use pages follow the Kind rules: one file per feature, README links only, and every delivered row names a Kind with its required block (Site/URL, Skill, Command, API/file contract, Scheduled routine, Deployment, Message/channel, Playbook), enforced by docs check (#4677, owner o78)

- Slug: howto-kinds
- Touches: not declared
- ETA: 210 active minutes (estimate 166m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given How-to-use pages with a README table, a delivered row with no Kind, and a Command row missing its dry-run form, when docs check runs, then each fails naming the page and the missing piece; with one file per feature, README links only and every Kind block complete, it passes
2. Given a feature page that names a command its How-to-use page doesn't list, when docs check runs, then it fails naming the command
3. Every How-to-use page in this repo meets these rules, the Documentation page states them with a test row, and the new wording goes to the owner for review

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
