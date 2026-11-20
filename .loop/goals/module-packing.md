# Bring the shipped package to 100 files or fewer so the release Size rule passes, with no feature or command dropped

- Slug: module-packing
- Touches: skills/workflow-setup/SKILL.md, skills/workflow-setup/references/settings.md, skills/workflow-release/SKILL.md, skills/workflow-release/references/commands.md
- ETA: 200 active minutes (estimate 160m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given main after this goal, when the package's file count is read the way the release Size rule reads it, then it is 100 or fewer; no feature or command is dropped (owner o70); every script stays at or under GRD-20's 20,480 bytes; every moved function keeps its callers working (each skill's toys pass on CI)

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
