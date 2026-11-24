# Patch (v1.1.0 Task 1, priority 1, FIRST; TD1361, owner o889): the pr regen commits every file its render changed, and the render is stable

- Slug: wiki-commit-front-files
- Touches: skills/workflow-release, skills/workflow-docs, dev/toy, .loop/regression.tsv
- ETA: 345 active minutes (estimate 275m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given `goal.py pr` or `role.py record` regenerates pages, then the one commit it makes includes every file that same render changed (README's generated blocks with the wiki pages), so no generated file is left dirty; shown by a toy where today's code leaves README dirty after the render (seen red) and the fix leaves the tree clean, plus a control where nothing changed and no commit is made.
2. Given the render runs twice on the same committed data, then it writes the same values both times, so a lane run between them can't flip the generated cells (the cells are rendered from committed run data, not the working copy's); shown by a toy seen red today.
3. Given the package, then every script stays under 20,480 bytes, no test is loosened, no row turns red, and committed text never names the service repo.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
