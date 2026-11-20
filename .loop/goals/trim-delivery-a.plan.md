# trim-delivery-a plan

Build steps (done in the worktree; files exist: skills/workflow-delivery/scripts/private.py, role.py, guards.py):
1. Re-indent each script to 2-space blocks with wrapped lines at the statement indent + 4, by a tokenizer pass; require `ast.dump` of the file before and after to be identical (code unchanged by construction).
2. Drop `HERE` in private.py (assigned, never read) and shorten the `cannot` docstring.
3. Check `git ls-tree -l` sizes at or under 19,000.

Tests per done line (no regression rows are added; the existing rows are the proof):
- Sizes: `git ls-tree -l HEAD` on the three scripts; existing rows scripts-a-delivery-under-19000, size-fail and the private, role and guards toys pass as before.
- Outputs unchanged: toys test-pr-tries, test-push-guard, test-guards, test-guards-null-report, test-lane-control, test-goal, test-guard-enforce, test-private-checks, test-resume-ask run on the trimmed code and match main. Negative control: a one-line behaviour change (flipping a refusal exit code in guards.py) must fail a toy.
- Diff: no new file, no row change, no requirement text change.

Could break: a toy that greps a script's text (they grep code names such as WORKER_PUSH_INTERNAL, which stay); the docstring line `private.py` prints for usage (line index 5, untouched).
Out of scope: any behaviour, message or requirement change; the other delivery scripts.
