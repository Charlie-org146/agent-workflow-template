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
