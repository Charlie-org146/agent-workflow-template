# Settings in the spec: each scheduled routine declares its permissions in its repo (setup writes them to project settings, a health rule catches drift), and the operation session keeps running unattended (standing merge instructions, sends-left warning before the 20-send cap, check-in loop re-created before 7-day expiry, owner-words records accepted by every worker, startup self-check).

- Slug: settings-in-spec
- Touches: not declared

## Done lines

Frozen. A wrong done line needs a new goal.

1. Each routine in .loop (health round, newsletter, steward triage) has a committed permissions declaration (commands, paths, sites, denies); setup writes it into the repo's project .claude/settings.json and a health rule fails when it drifts from the routine's runbook, with a negative control.
2. The five operation-continuity requirements are drafted in DECISIONS.md with one un-review-then-review sentence per reviewed page, and nothing reviewed is edited before the owner's words.
3. Tooling, a toy and a regression row (seen red first) for each.

## Verify by hand

<!-- One or more numbered steps a person can follow, each with an Expect: line. Every release needs this. -->
