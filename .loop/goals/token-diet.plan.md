# token-diet: plan

Claims from the design checked against the code: `guards.add_tokens` (guards.py:130), `goal.py cmd_record` (calls it at
the top), `fit.spent_tokens` / `tokens_text` / `budget_stop` (fit.py:92-136), `fit.view` line 325 (step tokens),
`checkin.main` (checkin.py:325), `reply_hook.decide` (reply_hook.py:366) and its `entries()` reader, the hook installer
`agents.reply_hook` + `HOOKS` (workflow-setup/agents.py:195, setup.py:314), `operation.id` (reply_hook.claimed) all exist.
Every script is within 1 KB of the 20,480-byte cap, so each addition is a new module with a one-line call site.

## Build order
1. `workflow-delivery/scripts/tokens.py`: `transcript(id)`, `calls(path, since, until)` (dedupe by message.id),
   `measure(path, since, until)` -> {input, cache_read, cache_write, output, calls, model, peak}, `fresh(v)`, `total(v)`,
   `add(state, step, given, measure)`, `live(state)`. Never raises; unreadable gives nothing.
2. `guards.add_tokens(state, step, given, measure=False)` delegates to `tokens.add`; `goal.py cmd_record` passes
   `measure=True`; `goal.py show` prints each step's fields; `fit.spent_tokens`, `tokens_text`, line 325 and `budget_stop`
   read dict-or-int values through `tokens.fresh` plus `tokens.live`; flow.py:352 and goal.py:238 keep ints working
   through `tokens.add`; `board_status.py:46` and `milestone.py:281` read through `tokens.total`/`fresh`.
3. `workflow-monitoring/scripts/optokens.py`: `classify(text)`, `row(root, session)`, `append(root)`; `checkin.main`
   calls `optokens.append` inside try/except; the docstring says it appends one row.
4. `workflow-monitoring/scripts/quiet.py` (UserPromptSubmit hook for the operation session) and the installer line in
   `agents.HOOKS` / `setup.py --reply-hook`.
5. `reply_hook.decide`: read the tail entries always; pass when the last non-retry user turn is neither a scheduled
   check-in nor a human ask for one; unreadable turn enforces as before.
6. `outcap.py` (one copy in workflow-delivery, workflow-monitoring and workflow-release, byte-identical, like
   proctree.py) and one `install()` line in goal.py, flow.py, sessions.py, operate.py (send) and merge.py; flow.py's
   step prompt prints uncapped.
7. Wiki: MON-5 reworded and set Unreviewed (C3, C4 and op-tokens); new DEL-16 (step tokens, budget unit) and GRD-15
   (output cap), both Unreviewed; Tests rows; `docs.py render`/`audit` for stamps; `entry.py write` for START.md.

## Tests (one fixture-driven script, `dev/toy/test-token-diet.py`; each row prints one PASS line, seen failing first)
1. step-tokens: fixture transcript with duplicate message lines and two steps; record gives tokens[step] dict with the
   deduped sums, peak and model; goal show lists them.
2. op-tokens: fixture with a scheduled prompt, a peer message, a human message and a hook-feedback turn; one row appended
   with each trigger's tokens; a second run adds only the new calls.
3. budget: a run record seeded with 3,000,000 fresh tokens is refused at the next step (BUDGET_TOKENS), and cache reads
   alone never stop a goal.
4. quiet: same check-in twice blocks the second with one line; a changed goal, a prompt that is not a check-in, and a
   previous turn older than 2 hours all pass through.
5. layout: a peer-message turn with a 2-line reply passes; a scheduled check-in with one line is still blocked.
6. outcap: 5,000 characters print as at most 2,300 with a cut line naming a readable file; `LOOP_OUTPUT_CAP=0` prints all.

## Could break
- Existing toys that assert on `tokens` ints or on output over 2,000 characters: measured and fixed in the lane.
- Regression table is at 1,199 of 1,200 rows: rows added past the cap are refused at qa unless net-zero. The plan keeps one
  row per done line (6) and merges or retires the same number of redundant rows; if that cannot be done cleanly the goal
  waits for the owner to raise `max_regression_rows` (PENDING only then).
- A hook that mis-detects "no change" would hide a check-in: the 2-hour ceiling and fail-open bound the harm.

## Out of scope
C1, C2, C5-C9, C11 and agent-routing (follow-up issues on v2.0); wake accounting and the 300k context ceiling line in
Needs you (measurement rows are there, the Needs you line is a follow-up).
