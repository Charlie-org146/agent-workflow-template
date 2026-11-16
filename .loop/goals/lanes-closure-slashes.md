# lanes.closure and touches() agree on Windows paths: no dep comes back with backslashes (#4457)

- Slug: lanes-closure-slashes
- Touches: not declared
- ETA: 205 active minutes (estimate 162m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. On Windows, skills/workflow-regression/scripts/lanes.py closure returns every dep with forward slashes (for example .loop/config.json, never .loop\config.json), and touches() normalises paths the same way config_hit does, so a goal touching .loop/config.json matches the rows that read it; a toy feeds both slash forms and gets the same rows.
2. The same toy run on a POSIX path list reads exactly as before (negative control), and the regression rows that use lanes.closure still pass on main.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
