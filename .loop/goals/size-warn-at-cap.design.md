# Design: size-warn-at-cap

## Problem
Health's script-size rule warns at 90% of the 20,480-byte limit (18,432 bytes), while the script target is 19,000. A script that meets the target still warns, the size toys (split-check, size-139/141 and the "under 18432" toys) fail by design, and health files a warning issue for each (#4370, #4560).

## Approaches
1. **Move the warning line to the target (chosen).** `health.size_rows` warns for a script over `WARN` = 19,000 (never above the configured limit), fails over the limit; the toys that hard-coded 18,432 follow to 19,000; one toy (test-size-warn.py) checks 18,900, 19,000, 19,100 and over the limit, plus a negative control for the old band.
2. Lower the target to 18,432: needs a trim of ~25 scripts. Rejected.
3. Make the warning a setting: more surface, no need. Rejected.

## Each done line
1. test-size-warn.py (5 checks), rows size-warn-band, size-warn-over, size-warn-control; size-139 and size-141 pass (split-check uses health.size_rows).
2. After merge: close the open size-warning health issues the new line clears, with a comment naming this goal, and #4370 and #4560.

## Open
The reviewed HLT-2 text on the Health page says "a warning from 90%"; it is now out of date and left for the owner to re-review (not edited here).
