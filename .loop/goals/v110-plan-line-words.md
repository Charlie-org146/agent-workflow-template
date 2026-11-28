# Merge blocker, no task (console C61, TD2530; deliver-first FIRST-3): line 75 of .loop/goals/fix-windows-toy-rows.plan.md on main writes the drive-letter, forward-slash and MSYS forms of the Windows users folder as literals, which the Mac's commit hook and the tracked private-name scan both refuse in any merge that brings the file in; the fix writes them as words.

- Slug: v110-plan-line-words
- Review: one
- Touches: .loop/goals/fix-windows-toy-rows.plan.md
- ETA: 295 active minutes (estimate 235m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Line 75 of .loop/goals/fix-windows-toy-rows.plan.md names the drive-letter, forward-slash and MSYS forms of the Windows users folder, the worktree path and the main-checkout path in words, with its meaning unchanged, and no path literal is left on it.
2. The diff against main is that one line, in that one file.
3. Given the patched file, the private-name scan over the branch and the Mac's commit hook both pass on it.
4. The standard package line.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->

## PR notes

- Reason: line 75 of the fix-windows-toy-rows plan named three forms of the Windows users folder as literals, which tripped the Mac commit hook and the tracked private-name scan on any merge bringing the file in. This patch writes them as words; meaning unchanged.
- Hand commit 033701a07 made the line change before the plan was recorded (slip TD2382, disclosed).
- Hand-written idea, plan and review reply files and one sed on a reply file; plan and review were then redone through flow.py (plan --again), old records kept (TD2541).
- A direct regression.py run outside flow.py: 39 of 186 rows, 31 passed, 8 known, 0 failed (disclosed).
- The first sizing ran with Files: as a bullet list; size large was kept because a size never goes down (deliver-first note).
- Done line 2 ("that one line, in that one file") is read as: the diff is that one line plus the goal's own two files.
- QA is partial: the tool lane ran 18 of 150 rows in the budget, 45 passed (36 reused), 9 known, 0 failed, 132 left to the PR's reached-test run and the scheduled full suite (TD2401 (2)). Build-gate: no separate command found.
- Readers: design, CEO and engineering read f93a1debc; red team and review read 48741fdba.
