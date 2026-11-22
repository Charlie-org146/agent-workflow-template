# Design: implement-v110

Status: idea for the plan step. It meets the frozen done lines in `.loop/goals/implement-v110.md` and changes none.
Source: the v1.1.0 brief's task 4 (frozen source sha256 cd66455a83be4a0b), DOC-27 on main, and the DEL-19, DEL-23 and
DOC-28 text of that page.

## Problem
Four features are written but nothing enforces them: DOC-27 (a feature page is one reviewable unit), DEL-19 (a goal is
one fixed format), DEL-23 (tasks are frozen briefs with one list) and the revised DOC-28 (a frozen release brief names
the tasks of a cut). Their test cases have no rows ("no passing test | not enforced").

## Constraints (measured by a read-only survey of this worktree)
- No script reaches 20,480 bytes and none newly crosses 19,000. `goal.py` 18,997, `merge.py` 18,990, `release.py`
  18,994, `review.py` 18,988, `wiki.py` 18,994, `checkin.py` 18,996, `live_board.py` 18,942, `criteria.py` 20,455 have
  3 to 58 bytes of room; `sections.py` (docs, 11,575) has 7,425 under 19,000; `docs.py` 542, `render.py` 263,
  `deployments.py` 826 (to 20,480), `fit.py` 839, `role.py` 483, `guards.py` 475, `lanekit.py` 932.
- Exactly one new file, `skills/workflow-release/scripts/brief.py` (o718, o719). The shipped package is at the
  file limit (100), so the goal merges after the limit lift (200).
- `criteria.py` is full, the Reviewed seal (`<!-- reviewed HASH -->`) carries no record id, and the ledger
  (`owner-words.tsv`, `reviews.tsv` under the git common dir) is not visible to CI.
- No page holds DEL-23 today and no task concept exists in the code; a goal file has no task field.
- Existing tests assert Runbook/Deployments sections pass on topic pages; those pages stay in the old shape.
- Known red on main: `merge-guard-base-head`, `rel-major-refused`, package headroom rows.

## Design
**DOC-27 (done line 2, 6).** One function `features(root, text)` in `sections.py` (room 7,425), called from
`sections.run` (already reached by `docs.py check` through `render.front`, so `docs.py` itself is untouched). It
applies only to a feature written in the new form (a requirement line whose sub-bullets open with `### Problem`), so
every old page keeps passing. It checks: the section order (Problem, Requirements (Functional then Non-functional),
Non-goals, Success metrics, Reference, Revisions, Tests last) and no other section; at most five requirements; one
metric and at least one test case per requirement, matched exactly on `Success metric N.N.` and `Test cases`; the
Success metrics table as the index of the inline metrics; Reference lines tagged adopted, adapted, own or reference;
the milestone line linking this repo's milestone; and the Reviewed mark. A missing metric, test or reference, a
feature marked "to split" and the page-rebuild items come out as `NOTE` findings, printed and never failed (the
existing mechanism). The Reviewed rule reads the ledger when the repo has it: a Reviewed requirement needs a record
whose ID list is exactly that ID (`deployments.owner_words` is tightened to refuse a record naming two IDs), and the
check prints a NOTE "not verifiable here" when no ledger is visible (CI).

**DEL-19 (done line 3).**
- Goal file gets `Task:` and `Release:` lines in `proctree.TEMPLATE` (three copies, 5 bytes of room each, freed by
  shortening each copy's own docstring) and the freeze takes `--task`: `goal.py new` and the queue freeze refuse a goal
  that names no task, a done line that is not Given/when/then, or a missing part (checked in `fit.frozen_fields`,
  room 839). `goal.py` has 3 bytes: the flag is added by folding its lambda wrappers (lines 186 to 191).
- A skipped review cannot open the PR: one refusal in `role.requirement_gate`, which `cmd_pr` already calls.
- The head-moved refusal and the frozen done-line refusal already exist (`HEAD_MOVED` in `merge.py`, `done_sha`
  in `goal.py`); they get rows, not code.
- The steps page is generated from `flow.STEPS`: a generated block written and checked by `sections.py`'s existing
  generated-block path (as "What this is" is today); a step added without regenerating gives the `STALE` finding.

**DEL-23 and DOC-28 (done lines 4, 5, 7): `brief.py`.** One module, loaded by path from the existing scripts, holds:
task brief files (`.loop/tasks/<name>.md`: name, feature served, purpose, done-when lines) frozen by the owner's typed
record naming exactly that task (the ledger) and a hash that a changed word breaks; the one task list (state queued,
running, waiting, done or replaced, goals, ETA) read from the briefs and the goals' run records; dependency start
gate; done only when every goal merged and every done-when line met; the release brief (`docs/release-brief-vX.md`)
listing tasks in order and frozen the same way; the gates (a major or minor needs a frozen brief; a cut needs every
named task done; a feature task merges only once a frozen brief names it; a bug-fix task merges any time; a major
with a non-empty known-red list is refused with no waiver, o714); the tag notes naming every task; the brief's
per-task result after the cut. Hooks into `merge.py`, `review.py`, `release.py`, `checkin.py`, `live_board.py` are one
call each, with the bytes freed by shortening those scripts' docstrings (measured before any code is written; the
build stops with a finding if a script cannot give its bytes, never adds a file).

**Tests (done lines 1, 7, 8).** Four rows, one per feature, each running a script that holds all that feature's cases
(new cases fold into existing scripts, o736 allows +4 rows); each case has a fixture that breaks only its rule and
is proven red with `regression.py red`. `dev/toy/test-release-gate.py` check 7 becomes "the shipped package stays
within MAX_FILES" with a control where one file over fails (o719). The no-red and size ratchets stay green.

## Risks
- The byte budget is the real risk: eight scripts have under 60 bytes. Mitigation: a measured byte table is the first
  build commit, and docstring trims are the only allowed source of bytes.
- The Reviewed ledger rule cannot run in CI: stated as a NOTE, and the toy proves the local failure.
- DEL-23 and DOC-28 text must be on main first (the text goal); the build stops if the pages lack DEL-23.
