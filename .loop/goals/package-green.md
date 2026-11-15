# Make dev/package.py pass on main (98 files at most, every script under 20 KB and standalone) and have setup say up front that un-reviewing a locked requirement needs the owner's own sentence (#3800, #2874).

- Slug: package-green
- Touches: dev/package.py, skills/workflow-setup, dev/toy

## Done lines

Frozen. A wrong done line needs a new goal.

1. dev/package.py passes on main with at most 98 files and every script under 20 KB and standalone, proved by one regression row (#3800).
2. Setup says up front, in its checklist or first output, that un-reviewing a locked requirement needs the owner's own sentence, proved by a toy case seen failing first (#2874).

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
