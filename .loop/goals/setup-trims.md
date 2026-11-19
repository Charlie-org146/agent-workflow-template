# workflow-setup's three scripts over the 19,000-byte warning line (agents.py 19,380, seed.py 19,345, update.py 19,413) are trimmed under 19,000 with text, comment and dead-code trims only, closing the Mac's share of readme-conformance gap cluster G13 (owner o355 'rework on the implementation ... based on this new README'; TOP-DECISIONs 136-137).

- Slug: setup-trims
- Touches: not declared
- ETA: 265 active minutes (estimate 210m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. agents.py, seed.py and update.py are each under 19,000 bytes on the merged result, with no behaviour change: their own toys and the setup regression rows pass unchanged before and after
2. Only text, comments, docstrings and provably dead code are removed; no file is added or renamed, the package file count does not grow, and net regression rows are 0 or fewer

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
