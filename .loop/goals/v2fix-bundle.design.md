# v2fix-bundle: design

Mode: builder (a maintenance bundle, no new product). Recommended answers taken throughout; nothing approved, merged or pushed.

## Problem

Six reviewed fixes and one header cleanup sit on one branch, each already written, each already past its own Claude review: #5344, #5308, #5078, #5359, #5346 and #5679, with defect rows for #88, #5635 and #5638. #5317 was carried and then reverted at the coordinator's word, and #5350 is not carried, so neither joins.

## Premise check

1. Is this the right problem? Yes: the fixes exist and are reviewed. The open work is to prove them together on the current main and ship them in one pull request.
2. If we do nothing: each fix lands later as its own pull request, serializing the merge queue six more times.
3. What already solves part of it: the branch carries every fix, its row and its kept record. The pull request body draft is `.loop/goals/v2fix-bundle.pr.md`.
4. Distribution: the pull request path through `goal.py pr`, no new artifact.

## Approaches

A. Minimal: re-merge main, re-render, rerun each carried row, open the pull request. Effort S, risk low.
B. Per-fix pull requests. Six times the queue time and six merges of the same stamp lines. Effort L, risk medium.
C. Rebuild the fixes against current main from scratch. Lateral, no benefit over A since each fix still applies.

Recommended: A, because every fix is already reviewed and the merge with main was clean apart from two data files.

## Findings carried into the plan

- The merge of main (v1.0.x after `scan-fail-closed`) conflicted only in `.loop/regression.tsv` (both sides add rows: kept all) and the generated `docs/wiki/Tests.md` (re-rendered).
- `scan-fail-closed` makes the private-name scan refuse when no list exists. CI sets an empty list; a local toy run needs one too.
- On a Mac inside a Claude session, toy rows that walk the stand-in flow take the in-session path and fail on pristine main as well (`defect-flow-steps`, `defect-categories`, `closing-unaffected`); `defect-88-closing-keywords` is in that family. CI decides those.
- `test-tree.sh` has one known failure, `lanes-headers`, which needs a `narrow.py` change and is out of scope; the pull request body says so.

## Done lines

The goal file's frozen done lines stand: each carried fix's own row seen failing then passing; `lanes_cli.py check` and `test-tree.sh` clean (bar the known row); only the fixes, headers, rows, re-rendered pages and records change.

## Risks

`merge.py` (18,996 bytes) and `graph.py` (18,982 bytes) sit at the 19,000 limit: no further growth. No check is weakened.

## The assignment

Run plan, review, qa and ship in this session; then `goal.py pr v2fix-bundle` with the body's Fixes lines for #5344, #5308, #5078, #5359, #5346, #5679, #5635 and #5638, and no Fixes line for #88 (a merged pull request).
