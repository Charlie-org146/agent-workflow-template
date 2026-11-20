# Owner text in the 'What this is' section survives a render, and the approved README's two new source hosts are allowed (TD385, operation-top under owner delegation; it unblocks readme-six, whose approved draft o514 puts the owner's harness-engineering paragraph after the generated part and cites two new official sources). skills/workflow-docs/scripts/sections.py fresh() rewrites the whole 'What this is' section, so any owner paragraph after the generated part is removed on each render. The change: fresh() rewrites only the generated first paragraph (up to its first blank line) and keeps every following paragraph of that section as written. Also add https://rework.withgoogle.com and https://www.gitguardian.com to public_origins in .loop/config.json (a link allow-list entry). Small fix: one script, one config line, one toy case. Target: pushed within 15 minutes of starting

- Slug: keep-what-this-is
- Touches: skills/workflow-docs/scripts/sections.py, .loop/config.json
- ETA: 460 active minutes (estimate 368m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a README whose 'What this is' section has the generated paragraph followed by an owner paragraph, when render.py blocks runs, then the generated paragraph is refreshed and the owner paragraph is kept byte for byte; and given a section with only the generated paragraph, then the output is unchanged from today (negative control)
2. Given .loop/config.json, then public_origins also holds https://rework.withgoogle.com and https://www.gitguardian.com, and a page linking a host outside public_origins is still refused by DOC-19 (negative control)
3. Given this goal's diff, then only sections.py, .loop/config.json's public_origins, one toy or regression case and the goal's record files change, sections.py stays under 19,000 bytes, and docs.py check and criteria.py render --check pass

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
