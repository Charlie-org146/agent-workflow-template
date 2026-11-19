# Before build, a fresh-context reviewer red-teams each goal's plan against every principle and lists unverified assumptions, risks, principle breaks and cheaper paths; a principle break blocks the build until the plan changes or the owner accepts the break in their own words; the reviewer never edits, merges or decides; a second hourly pass reviews the board and both machines' STATUS (owner o222, o237; TOP-DECISION 94, 98, 100)

- Slug: plan-red-team-core
- Touches: skills/workflow-monitoring/scripts/layers.py, dev/toy/test-three-level.py, .loop/regression.tsv, docs/wiki/Delivery.md, docs/wiki/Health.md, docs/wiki/Tests.md, skills/workflow-delivery/scripts/flow.py, DECISIONS.md, skills/workflow-delivery/scripts/goal.py, skills/workflow-delivery/scripts/guards.py, skills/workflow-monitoring/scripts/mailbox.py, dev/toy/test-guards.sh, dev/toy/test-goal.sh
- ETA: 220 active minutes (estimate 175m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. A red-team command gives a fresh-context reviewer one goal's plan and records its findings (unverified assumptions, risks, principle breaks naming the principle, cheaper paths) with a timestamp; a test proves the reviewer reads but never writes repo files, merges or sends decisions
2. A recorded principle break blocks that goal's build step until the plan changes or an owner record accepts the break, with a negative control for each case
3. An hourly pass and a pass before any release ETA review the board and each machine's latest STATUS and list unverified assumptions, work idle capacity could start and the biggest risk to the release time, each routed to operation-top as a proposed TOP-DECISION or to ops-findings
4. Requirement wording goes to the owner before merge; no new shipped file unless a fold pays for it; net regression rows 0 or fewer

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
1. In a repo with a goal `g` that has a plan, run `python3 skills/workflow-monitoring/scripts/mailbox.py plan-review g`.
   Expect: it prints the goal, design and plan, the eight principles and a request for `A:`, `R:`, `B<n>:` and `C:` lines.
2. Put `B3: the plan contradicts a page` and `A: an assumption` in a file and run `mailbox.py plan-record g FILE`.
   Expect: `BREAK principle 3: the plan contradicts a page`, `git status` unchanged, and one `plan-g-<time>.json` in `.git/loop/redteam/`. A `B9:` or `B:` line prints `REFUSED` and records nothing.
3. Run `python3 skills/workflow-delivery/scripts/goal.py step g build` as a worker (LOOP_ROLE=worker).
   Expect: `REFUSED (no try used): the red team recorded a break of principle 3 ...` and exit 2.
4. Have the operation session record the owner's words, then run `mailbox.py plan-accept g 3 --owner-record <id>` and step build again.
   Expect: `STEP g build`. Changing the plan file instead prints `NOTE: the plan changed since the red team ran` and the step runs.
5. Run `python3 skills/workflow-monitoring/scripts/layers.py redteam input`, record `A:`, `I:`, `R:` lines with `layers.py redteam record FILE`, then `layers.py redteam due`.
   Expect: three ROUTE lines (the A item as a `mailbox.py finding` command, the others as a proposed TOP-DECISION) and `RED-TEAM ok: last pass 0 minutes ago`.
