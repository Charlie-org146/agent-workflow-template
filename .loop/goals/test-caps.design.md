# Design: test-caps

## Problem
The template holds 1,032 regression rows and its full suite takes about 1,650 seconds in CI (more than two hours on the PC when a
release check reran rows one by one). Nothing stops the next goal adding rows past that, so the test load itself blocks delivery
(#4511, owner o51: "you cannot let test pass a certain number, or test time pass a certain amount ... and block the delivery").

## Approaches
1. **Two settings, one measuring function, three readers (chosen).** `max_regression_rows` (default 1100) and `max_suite_seconds`
   (default 1800) are repo settings in `.loop/config.json` and Home's settings table (`settings.py`). One function counts the table's
   rows and reads the suite time (the newest completed full run of the repo's regression workflow, by `gh`; not measured offline).
   Health shows both against the caps (WARN at 90%, FAIL over, each with a negative control in controls.py); the qa step refuses a goal
   with the numbers; the Guardrails page states it as a requirement under o51.
2. A CI-only check: too late, the goal is already built; and the cap would not show in health or Home. Rejected.
3. Hard-coded caps: not an owner-raisable setting. Rejected.

## The qa gate
A goal is refused at qa when, after its own changes, rows or the measured suite seconds are over a cap AND the goal adds at least one
row net: rows(HEAD) - rows(base) > 0 for rows, and (net added rows' seconds from the lane record, when timed) for seconds. A goal
whose net row change is zero or negative (it removes or merges at least as many as it adds) always passes, so a consolidation is never
blocked. The owner lifting a cap in their own words is a `goal.py set`-style config change recorded as an owner record, which raises
the cap the check reads; the refusal message names that way out.

## Each done line
1. Both settings exist in `settings.py` with defaults the template passes today (1,032 rows under 1100; ~1,650 s under 1800) and show in Home.
2. role.py's qa lane refuses with numbers; toy: over the cap and adding rows refused; over the cap and removing as many as it adds, or a
   consolidation, allowed; a raised cap allows.
3. Health rule `test-caps` rows and seconds; WARN at 90%, FAIL over; controls for each; Guardrails gets a requirement under o51.

## Open questions
- Suite seconds come from GitHub (gh); offline they are not measured, and the rule says so (INFO), the qa gate still enforces the row cap.
- Files near the 19,000-byte cap and the 98-file package: no new file; wording trimmed elsewhere to fit.
