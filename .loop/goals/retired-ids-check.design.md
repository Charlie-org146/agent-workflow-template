# Design: retired-ids-check

Condensed; one self-review pass, no findings.

The DOC-23 front-door check collects the IDs that exist from lines `- ID: **...` on the wiki pages (render.py, `front()`). A retired ID's line reads `- ID: moved to X`, so it was refused. The pattern also accepts `moved to `; an ID with no line is still refused. No requirement text changes.
