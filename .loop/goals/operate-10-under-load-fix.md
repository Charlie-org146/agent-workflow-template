# The row operate-10-under-load passes again and stops setting the full suite's length (issue 5478, real: failed twice on main, 'operate-all under load (4 busy loops): 0 of 10 passed', about 24 to 30 minutes on one shard; TD426/TD434: first of the red-row fixes after the release blockers). FIRST diagnose: read the toy and what operate-all does under load on a CI runner, and say why 0 of 10 pass (a real regression in operate.py, a timing the CI runner cannot meet, or the toy itself) and which merge most likely started it, with evidence. THEN fix the cause: if operate.py regressed, fix it; if the toy's timing assumption is wrong for a CI runner, aim it at the requirement it guards with the same strength. No check loosened, no silent retry (REG-4), and the row runs well inside the 200-second row limit

- Slug: operate-10-under-load-fix
- Touches: skills/workflow-monitoring/scripts, dev/toy
- ETA: 460 active minutes (estimate 368m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given the diagnosis in the pull request, then it names the cause with the failing line and the evidence (code, timing or toy), and the merge that most likely started it
2. Given the row on this branch in CI, then it passes within the row limit, and a negative control shows it still fails when operate-all really fails under load
3. Given this goal's diff, then only the files the cause needs, the toy and the goal's record files change, every script stays under 20,480 bytes, and docs.py check and criteria.py render --check pass

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
