# The release and health-assert regression rows pass again on main: their asserts match today's release code and pages

- Slug: known-red-release
- Touches: not declared
- ETA: 290 active minutes (estimate 232m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Rows release-criteria-known-skip, auto-release, rel-major-refused and no-token-would pass: their asserts follow today's code (criteria_trouble's tuple, release.bump with MAJOR_GATE, the Release page's REL-1 to REL-14, the HLT-4 milestone warning), with rel-major-refused's byte cap following the size rule the goal v2-health-green leaves
2. Rows issue-129-docs-published and skill-refusals-in-references pass once skills/workflow-release/SKILL.md is under 150 lines (v2-health-green trims it; this goal re-merges main after it and confirms), and every row this goal fixes leaves .loop/regression-known.tsv; nothing else changes; net test rows grow by at most 0

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
