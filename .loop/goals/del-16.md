# Put requirement DEL-16 (Each step runs on the agent the config picks, from agent-routing) on the Delivery wiki page, Unreviewed, linked to agent-routing's existing tests

- Slug: del-16
- Touches: docs/wiki/Delivery.md, docs/wiki/Tests.md, .loop/regression.tsv
- ETA: 185 active minutes (estimate 145m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. docs/wiki/Delivery.md holds DEL-16 with the wording agent-routing wrote (commit d33bd506), marked Unreviewed, and the Delivery page review line is Unreviewed
2. DEL-16 is linked to agent-routing's existing regression test, and workflow-docs check prints DOCS OK

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
1. Run `grep -n "DEL-16" docs/wiki/Delivery.md`.
   Expect: a line `- DEL-16: **Unreviewed** Each step runs on the agent the config picks` followed by three sub-bullets.
2. Run `grep -n "^Review:" docs/wiki/Delivery.md`.
   Expect: it prints a line reading `Review: **Unreviewed**`.
3. Run `python3 skills/workflow-docs/scripts/docs.py check`.
   Expect: it prints `DOCS OK`.
4. Run `grep -n "DEL-16" .loop/regression.tsv`.
   Expect: the `agent-routing` row names DEL-16 as its goal.
