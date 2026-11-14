# lanes_cli.py affected holds under about 200 MB per process on a large repo (it held 430 to 820 MB, #4151), with the same output and behavior

- Slug: lane-affected-memory
- Touches: skills/workflow-regression/

## Done lines

Frozen. A wrong done line needs a new goal.

1. affected stays under about 200 MB peak on thermis: the lane stops holding every file's text for the whole run, found by measuring first (a file text cache of 135 of 182 MB)
2. a toy shows the memory bound: a repo of many large files stays under the bound, and affected prints the same answer as before
3. optional: the lane waits before affected when free commit memory is under min_free_memory_gb, only if REG-7's new sub-bullet from budget-enforce already covers it, else left out and said

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
1. Run `python3 dev/toy/test-lane-affected-memory.py`. Expect: three PASS lines, and a peak under 100 MB (about 58 MB here).
2. In a large repo with many rows (the thermis checkout), run `python3 skills/workflow-regression/scripts/lanes_cli.py affected PATH...` for about ten changed paths. Expect: the same AFFECTED line and the same DELETED and UNMAPPED lines as before, in minutes not tens of minutes, with a peak memory under about 200 MB.
3. Read `.loop/goals/lane-affected-memory.design.md`. Expect: it says why done line 3 (waiting for free memory) was left out.
