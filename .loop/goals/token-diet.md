# Measure token use per worker step and per operation-session check-in, make fit.py's token budget read those transcript-measured tokens, and make check-ins and script output cheaper (C3, C4, C10 of #4788).

- Slug: token-diet
- Touches: not declared
- ETA: 195 active minutes (estimate 155m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a worker step, when goal.py record runs, then tokens[step] holds input, cache_read, cache_write, output, calls, model and peak context read from the session transcript, and goal.py show lists them.
2. Given the operation session, when checkin.py runs, then a row (time, context, tokens since the last row by trigger: scheduled, peer, human, hook-retry) is appended to .git/loop/op-tokens.tsv.
3. Given token_budget and a goal whose transcript-measured tokens exceed it, when fit.py checks a step, then the goal waits; a regression row seeded with 3M tokens proves it.
4. Given a scheduled check-in and checkin.py showing no change since the last one, when the operation session runs it, then the model turn is skipped and nothing is printed beyond one line.
5. Given a check-in that is neither scheduled nor asked for, when the operation session replies, then 1-3 lines pass the reply hook; the full MON-5 layout is required only for scheduled or asked-for check-ins.
6. Given any loop script's output over 2000 characters, when it prints, then it is cut to 2000 characters with a line saying where the full text is.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
