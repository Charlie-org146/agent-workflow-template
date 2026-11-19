# known-red-w8-size: design

## Problem

Nine rows fail on main's full run 44463859531: byte and line caps on scripts and SKILL.md files, and one stale toy assertion. With the owner's "no waivers" (o195, o212) each must pass or be removed with evidence; none may go into regression-known.tsv, and net rows stay at or under 0.

## Approaches

1. **Trim prose only.** Enough for the SKILL.md line caps, setup.py and regression.py/lanes.py; not for runs.py, checkin.py, the four health scripts or the eleven docs scripts, whose code outweighs their prose.
2. **Trim prose, move the explanation into the skill's references, and make one pure move of a cohesive helper block into an existing script with room (TOP-DECISION 57; chosen).** No new file, names imported back, no logic deleted, every printed string kept. Rejected: re-aiming the rows to the 20,480 fail line or removing them, which the owner did not rule.

## What each row needs

- skill-kept: the toy looks for the review rule in the moved place (SKILL.md or references/commands.md).
- skill-size-116, skill-lines-release-4172: monitoring and release SKILL.md under 150 lines by rewrapping.
- trim-setup-under-19000: setup.py 18,991 from docstring prose.
- size-141, scripts-c-regression-under-19000: regression.py 18,992, lanes.py 18,966, runs.py 18,931; runs.py's format notes move to references/commands.md.
- scripts-c-health-under-19000: report.py 18,966, rules.py 17,577, automation.py 18,862, controls.py 18,994; each file's explanation moves to a notes section in the health references.
- trim-monitoring-4-size: checkin.py 18,096, by moving shown() and gather() verbatim into board_lines.py (re-exported; live_board imported lazily because it imports board_lines; the local dict `states` renamed `stat` so it no longer shadows board_lines.states()).
- docs-release-scripts-under-19000: passes when w11's trim of the eleven docs scripts lands; merge main after it (the row is not removed, TOP-DECISION 55).

## Open questions

None for the owner. Kept stamps on the pages the changed paths map to; a one-sentence intro edit on Principles.md clears its stale mark (a guide page cannot be restamped).
