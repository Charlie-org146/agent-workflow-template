# Design: v110-fast-renumber

Source: the owner's final page frozen-source-final-1742 (sha256 c952ee382c4153f8, checked), owner record o743 (the principle split), operation TD791 to TD793. Done lines are frozen in `.loop/goals/v110-fast-renumber.md`. Names and numbers only; the principle sentences, every feature's text and every mark stay as they are. This goal replaces the first half of the retired v110-fast-text (its plan and four gates stay as reference).

## What it does
1. The principles are renumbered 1 to 8: 1 Guided, 2 Sensed, 3 Fast, 4 Cheap, 5 Small, 6 Private and guarded, 7 Reproducible, portable and adoptable, 8 Autonomous and human-friendly. The three new names are the page's words ("Fast", "Cheap", "Small").
2. Features sit where the page puts them: DEL-17 and HLT-7 under 3 Fast (HLT-7 does not fold yet: that is part 1b); GRD-20 under 5 Small; every feature of the old 4, 5 and 6 under 6, 7 and 8; OPS-16 moves to 7 Reproducible (o750). Cheap's first feature is DEL-17's token part moved out word for word (o750).
3. No principle sentence changes. The old combined sentence is kept where it is; the new Cheap and Small sections reuse nothing new until part 1b writes the owner's final sentences (o746).
4. Every reference to an old number is updated (README, Home, Principles page, the principles list, toys that pin the old headings, the how-to pages).

## What it does not do
No sentence, feature text, mark, retirement or DEL-22 (part 1b, v110-fast-text-2). No code.

## Held (answered by o750; kept for the record)
Done line 2 (health not red) cannot hold with an empty Cheap principle: measured in a scratch clone of main, `PRINCIPLE 4 Cheap: RED (none)`, `FAIL requirements principle 4 principle-map: principle 4 has no Reviewed requirement`, and `FORMAT README/Home/Principles ... (got 0 rows)` from docs.py check. The goal waits for the owner's answer on which feature goes under 4 Cheap (operation TD791 iii). Planning and the gate run now; no build.

## Open
- The principles list is `skills/workflow-health/references/commands.md`; the goal's Touches name `skills/workflow-delivery/references/commands.md`, which holds no principle text (grep). Operation is asked which is meant; if health's is not added, the build stops at the list.
- TD793: no page lists DEL-19.2's eight step names on main; every page carries the old list (README.md:11,31,134; docs/wiki/Home.md:8,28,131; Principles.md:18; Delivery.md:39 Reviewed, :240 history). Reported, not reworded.
