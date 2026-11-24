# Text (v1.1.0 Tasks 12-14, priority 1; owner o907): the six reviewed features DLF-1, TSK-1, CBS-1, SKP-1, CHP-1 and ASZ-1 written into their pages word for word, and a re-frozen v1.1.0 brief that adds Tasks 12, 13 and 14

- Slug: v110-tsk12-14-text
- Touches: docs/wiki, docs, README.md, .loop/regression.tsv
- ETA: 300 active minutes (estimate 238m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given the owner's reviewed text for DLF-1, TSK-1, CBS-1, SKP-1, CHP-1 and ASZ-1, when the goal writes their pages, then each is on the page it names (Deliver-first, Task-first, Checks-by-size, Fast-checks, Cheap-checks, Autonomous-sizing) word for word, checked by a diff against reviewed-features-2026-11-23.md which shows no change but the page layout, marked Reviewed through criteria.py review with the owner record, and docs.py check passes.
2. Given the v1.1.0 brief frozen on 2026-11-21, when the goal replaces it under DOC-28, then the new brief keeps every task it had, adds Task 12 Deliver first (DLF-1), Task 13 Task first (TSK-1) and Task 14 Right-sized checks (CBS-1, SKP-1, CHP-1, ASZ-1) at priority 1 with the owner's words, and is frozen.
3. Given the package, when the goal's checks run, then every script stays under 20,480 bytes, no test is loosened, no row turns red, and committed text never names the service repo.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
