# The 19,000-byte size rows pass again: every script they name is under its 19,000-byte target with behaviour unchanged (TOP-DECISION 39: trim, not retire)

- Slug: known-red-size
- Touches: not declared
- ETA: 290 active minutes (estimate 232m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Rows docs-block-split, size-140, scripts-a-delivery-under-19000 and scripts-a-monitoring-under-19000 pass: render.py, docs.py, the six delivery scripts (private.py largest) and sessions.py, checkin.py, reply_hook.py and operate.py are each under 19,000 bytes, with size-140's expected names following docs.py's real imports
2. Behaviour is unchanged: each trimmed script's own tests and the rows that reach it pass, by moving code to existing or new helper modules or tightening text, never by deleting a check or a feature
3. Every row this goal fixes leaves .loop/regression-known.tsv; nothing else changes; net test rows grow by at most 0

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
