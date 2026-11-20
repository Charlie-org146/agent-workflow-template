# The docs check accepts a retired requirement ID as an ID that exists (TD379, operation-top under owner delegation; it unblocks readme-six, whose approved README draft o514 names absorbed IDs in its titles). skills/workflow-docs/scripts/render.py line 142 reads only live lines '- ID: **Reviewed|Unreviewed**', so DOC-23 refuses an ID whose line is '- ID: moved to X'. The change: that pattern also accepts '- ID: moved to ', so a retired ID counts as existing (its line says where it went), while an ID with no line at all is still refused. render.py stays under 19,000 bytes. One toy or regression case proves both. Small fix: one script, a few lines, no requirement text change. Target: a pushed pull request in about 15 minutes

- Slug: retired-ids-check
- Touches: skills/workflow-docs/scripts/render.py
- ETA: 345 active minutes (estimate 273m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a page whose Requirement cell names an ID whose only line is '- ID: moved to X', when the docs check runs, then it does not print 'DOC-23 an ID that exists' for that ID; and given an ID with no line at all, then it still prints it (negative control)
2. Given this goal's diff, then only skills/workflow-docs/scripts/render.py, one toy or regression case for D1 and the goal's own record files change, render.py ends under 19,000 bytes, and the docs check and criteria.py render --check pass

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
