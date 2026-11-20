# board.py board and checkin.py stop crashing with 'can't subtract offset-naive and offset-aware datetimes' at board_log.py:171 (flow_seconds, at - last). Fix it at the cause, in the clock and in record-stamp parsing, so every datetime is aware; coerce nothing silently: a stamp that can't be read as aware is reported, not guessed

- Slug: board-tz
- Touches: skills, dev/toy
- ETA: 465 active minutes (estimate 369m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a run record with one naive and one aware stamp, when board.py board and checkin.py run, then neither crashes, and a toy proves it with both stamps
2. Given a stamp with no time zone, then the parser names it in its output rather than silently assuming a zone, shown by the same toy
3. Given this goal's diff, then every script stays under 20,480 bytes, docs.py check and criteria.py render --check pass, and each new regression row has a red proof (regression.py red)

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
