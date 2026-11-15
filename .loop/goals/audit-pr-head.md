# merge.py audits the goal's PR head render, not the main checkout's (#4208); goal.py new in a Claude app worker session binds that session (#4257)

- Slug: audit-pr-head
- Touches: skills/workflow-release/scripts, skills/workflow-delivery/scripts, skills/workflow-docs/scripts, skills/workflow-monitoring/scripts, dev/toy, .loop/regression.tsv, docs/wiki

## Done lines

Frozen. A wrong done line needs a new goal.

1. merge.py's wiki.pending check audits the goal's PR head render, not the main checkout's: a PR that fixes a page main left stale passes, a PR that stales a page is still refused (#4208)
2. goal.py new, run inside a Claude app worker session, binds the new goal to that session like sessions.py bind SLUG ID and says so; outside an app session it changes nothing (#4257)

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
