# Before build, a fresh-context reviewer red-teams each goal's plan against every principle and lists unverified assumptions, risks, principle breaks and cheaper paths; a principle break blocks the build until the plan changes or the owner accepts the break in their own words; the reviewer never edits, merges or decides; a second hourly pass reviews the board and both machines' STATUS (owner o222, o237; TOP-DECISION 94, 98, 100)

- Slug: plan-red-team-core
- Touches: not declared
- ETA: 220 active minutes (estimate 175m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. A red-team command gives a fresh-context reviewer one goal's plan and records its findings (unverified assumptions, risks, principle breaks naming the principle, cheaper paths) with a timestamp; a test proves the reviewer reads but never writes repo files, merges or sends decisions
2. A recorded principle break blocks that goal's build step until the plan changes or an owner record accepts the break, with a negative control for each case
3. An hourly pass and a pass before any release ETA review the board and each machine's latest STATUS and list unverified assumptions, work idle capacity could start and the biggest risk to the release time, each routed to operation-top as a proposed TOP-DECISION or to ops-findings
4. Requirement wording goes to the owner before merge; no new shipped file unless a fold pays for it; net regression rows 0 or fewer

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
