# Design: v110-cbs-asz (CBS-1 checks by size, ASZ-1 autonomous sizing)

Mode: intrapreneurship, built from owner-approved text (the file reviewed-features-2026-11-23-reworded-DRAFT.md, units CBS-1 and ASZ-1). The goal's four done lines are frozen; this design meets them and changes none.

## Problem
- Every goal runs the same full set of checks, and a goal's size and checks are argued in messages that wait for the owner (CBS-1 and ASZ-1 Problem sections).
- Plan review alone took 32 to 144 minutes a goal on 11-22 and 11-23, whatever the goal's size.

## What is in scope (all of CBS-1.1 to 1.4 and ASZ-1.1 to 1.3)
- One checks table (small, medium, large) with named forms of each check, shipped as template defaults and changed only on the owner's words.
- Fixed checks that no row may lighten: build gate, full test run before merge, two leak readers before any push, every safety class. A table row that lightens one is refused when settings are read.
- A size computed at freeze from the plan (files, lines, gate, safety class), recorded with its reason, checks taken from the table, no question to the owner.
- Up-only re-size at build record, with the added checks run before the PR; a safety-class goal is always large.
- Skipped or light checks listed on the release; the cut can require a full run of any.
- The board shows size, reason and checks; one owner line changes a size and is logged with the owner's words.

## Premises (taken as stated by the owner text)
1. The size lines are fixed by the owner: small is 3 files or fewer, 150 lines or fewer, no gate and no safety class; medium is 10 files or fewer and no safety class; large is everything else.
2. The table and the fixed list are settings, not code constants, so a repo changes them with the owner's words and no code edit.
3. Sizing needs no model call: it is a pure function of the plan's file list, line estimate, gate list and safety-class flag, so the same plan always gets the same size.
4. Scripts in the delivery skill are near the 20,480-byte cap, so the logic lands in new small modules, never as growth of an existing script.

## Approaches
- A (recommended): one new pure module for the size function and the table check, the table as a settings key with shipped defaults, thin hooks at freeze, build record, release list and board. Smallest diff that meets every done line; reuses the settings table, plan-accept's owner-record pattern and the board's existing line renderers.
- B: put the size rule into the planning tool's own guard. Rejected: the guard is the planner's, ASZ-1 is a goal-routine feature, and the guard must stay untouched.
- C: separate sizing service or file store with its own CLI. Rejected: more surface than the requirement needs; a settings key plus a pure function covers it.

Auto-decided (recommended option taken at each decision, per the step's rule): A.

## Risks
- Hooks touch tools that sit at their byte cap: each hook must be a one-line call into the new module.
- Gate and safety-class detection must use the repo's own lists (risky_paths and the guard lists), not a new list.
- Re-sizing must be monotone across resume and across a build that is re-recorded.

## The assignment
Plan the goal at the tool's depth: name each file touched, the table's default values and named forms, how freeze, build record, release list and board call the sizing module, and a fixture per rule that breaks only that rule.
