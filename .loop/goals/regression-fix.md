# Fix the regression rows that began failing in today's merges, and make health finding keys path-separator free.

- Slug: regression-fix
- Touches: dev/toy, skills/workflow-health/scripts, skills/workflow-monitoring/scripts, skills/workflow-delivery/scripts, skills/workflow-regression/scripts, .loop/regression.tsv, docs/wiki, docs/regression-fix-2026-11-15.md

## Done lines

Frozen. A wrong done line needs a new goal.

1. Rows #4364 mon8-silent-30, #4366 grd8-silent-worker, #4367 set8-local-setting-refused, #4373 lane-over-minutes, #4374 mon12-pool, #4375 parallel-unlimited and #4376 held-all each have the release where they first fail named, and the code or the test, whichever is wrong against its requirement, is fixed, with the passing line on the issue before it closes. Every health finding key holds its path with forward slashes only, so Windows, Mac and Linux runs match one issue per finding; the existing duplicate pairs are merged once; a toy case is proven red first (#4379). Files stay at or under 19,000 LF bytes, the package at 98 files or fewer, and no reviewed requirement text changes.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
