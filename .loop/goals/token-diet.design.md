# token-diet: design

## Problem
v1 goals spend a median 18.0M tokens (operation session 41% of all tokens) and nothing measures it where it is spent:
5 of 204 run records hold per-step tokens, and `fit.py`'s `token_budget` reads a field that is almost never filled, so it
never stops anything. Scope for this goal (owner, o115): measurement plus the cheapest cuts C3, C4, C10 of #4788.

## Facts found
- A session's transcript is `~/.claude/projects/*/<CLAUDE_CODE_SESSION_ID>.jsonl`. Each assistant line has
  `message.usage` (input, cache_read, cache_creation, output), `message.model` and `message.id`; one call can appear on
  several lines, so a call is counted once by `message.id` (the last line wins). Subagent calls are in other files.
- Every script under `skills/` is within about 1 KB of the 20,480-byte cap, so each piece goes in a new module.
- `operation.id` holds the operation session's transcript id; the transcript shows what woke each turn: a scheduled
  check-in prompt, a peer message or task notification, a human message, or `Stop hook feedback`.

## Approaches
A. Measure with new modules and thin call sites (chosen). Cost: 4 small modules, one-line hooks in goal.py, guards.py,
   checkin.py, reply_hook.py. Risk: transcript format drift (the reader returns nothing, never raises; the goal then reads
   "tokens unread" as before).
B. Wrap every script in a tracing shim that counts tokens from stdout size. Rejected: it measures output size, not
   model tokens, and cannot see cache reads, which are 99% of the spend.

## Chosen design
1. `workflow-delivery/scripts/tokens.py`: finds the transcript, reads calls in a time window, returns
   {input, cache_read, cache_write, output, calls, model, peak} (peak = the largest input+cache_read+cache_write of one
   call). `goal.py record` (through `guards.add_tokens(..., measure=True)`) measures from the goal's last mark (first
   log line for the first step) to now and stores it as `tokens[step]`; an int already there (flow.py, `--tokens N`) is
   kept as `reported` inside the dict. `goal.py show` lists the fields per step.
2. Budget unit: `fit.spent_tokens` sums `fresh = input + cache_write + output` per step (the unit commands.md already
   documents: "no cache reads") plus the live window since the last mark, so the budget reads transcript-measured tokens.
   Cache reads stay in the record for reports. Decision recorded as auto: counting cache reads against a 3M budget would
   stop 139 of 143 goals (their median is 18M with cache reads), which stops the loop rather than limiting it.
3. `workflow-monitoring/scripts/optokens.py`: classifies each user turn (`scheduled`, `peer`, `human`, `hook-retry`),
   adds each call's tokens (all four fields, the baseline's unit) to its turn's trigger, and `checkin.py` main appends one
   row to `<git common dir>/loop/op-tokens.tsv`: time, session, context (last call's), then tokens since the last row for
   each trigger, then total. Failures never stop a check-in.
4. C3 `quiet.py`: a `UserPromptSubmit` hook for the operation session. For a scheduled check-in prompt it renders the
   check-in (`checkin.render`), drops the Machine line and numbers, hashes it, and when it equals the last full turn's hash
   (and that turn was under 2 hours ago) it blocks the prompt with one line: no model turn runs, nothing enters context.
   `setup.py --reply-hook` installs it beside the Stop hook; `reply_hook: false` or `LOOP_REPLY_HOOK=0` turns both off.
5. C4: `reply_hook.py` enforces the MON-5 layout only when the last non-retry user turn is a scheduled check-in or a
   human ask for one (check-in, where do things stand, status, report, board); any other turn (peer message, task
   notification, other human talk) passes with a 1-3 line reply. When the trigger can't be read it enforces, as before.
   MON-5 is reworded and marked Unreviewed for the owner.
6. C10 `outcap.py` (a copy per skill, like proctree.py): `install()` makes stdout keep the first 1000 and last 1000
   characters of anything over 2000 and write the full text under `<common>/loop/out/`, naming the file in the cut line;
   `LOOP_OUTPUT_CAP=0` turns it off. Installed in goal.py, flow.py, sessions.py, operate.py send and merge.py; flow.py's
   step prompt prints uncapped (a worker must read it whole).

## What each done line needs
1. tokens[step] dict + goal show: tokens.py, guards.py, goal.py, test with a fixture transcript.
2. op-tokens.tsv row: optokens.py, checkin.py main, test with a fixture transcript of four trigger kinds.
3. Budget: fit.py reads the dict; regression row seeds 3M fresh tokens and the goal's next step is refused.
4. C3: quiet.py + installer; test: unchanged check-in blocks with one line, a changed one and a 2-hour-old one do not.
5. C4: reply_hook.py; test: a peer-message turn with a 2-line reply passes, a scheduled check-in with one line still blocks.
6. C10: outcap.py; test: 5,000 characters print as at most about 2,200 with a cut line and a readable file.

## Open questions
- Whether the owner wants the budget unit to include cache reads (taken: no, see 2). Decided by default, logged.
- MON-5's wording changes (C4), so it goes back to the owner as Unreviewed.
