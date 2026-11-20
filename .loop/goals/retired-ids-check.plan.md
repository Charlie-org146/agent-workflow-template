# Plan: retired-ids-check

Design: `.loop/goals/retired-ids-check.design.md` (condensed; one self-review pass, no findings).

## URGENT, outside this plan

None.

## Implementation plan

Done lines (frozen): (1) a retired ID counts as existing and an ID with no line is still refused; (2) only render.py, one toy case, and the goal's record files change; render.py stays under 19,000 bytes.

### 1. `skills/workflow-docs/scripts/render.py`
- The ID pattern in `front()` becomes `^- ([A-Z]{2,5}-\d+): (?:\*\*|moved to )`.

### 2. `dev/toy/test-docs-format.sh` and `.loop/regression.tsv`
- Two cases: an ID with no line fails DOC-23, an ID whose line says "moved to" passes; one regression row `retired-id-exists` with a seen-red.

## Verification
Run the toy script; revert render.py to see the retired-ID case fail.
