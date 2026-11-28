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
