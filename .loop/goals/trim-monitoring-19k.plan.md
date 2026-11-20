# Plan: trim-monitoring-19k

Files (all exist): skills/workflow-monitoring/scripts/sessions.py, operate.py, reply_hook.py. Functions touched are docstrings and comments only; operate.apply folds a duplicated `pages = sorted(...)` expression into a local `stale()`.

Steps
1. Trim module docstrings (help text), function docstrings and `issue N` comments in each script; keep requirement IDs (MON-n, GRD-n, C4 removed only as comment text), all printed messages, the reply-hook TEMPLATE and the refusal strings.
2. Measure each with `git cat-file -s` (LF bytes): must be <= 19,000.
3. Run test-operate.sh, test-reply-hook.sh, test-session-workers.sh (via a uname shim on Windows) plus test-reply-deps.py, test-reply-repo-blocks.py and test-go-app-sessions.py before and after on a pristine worktree; PASS/FAIL sets must match.
4. Negative control: change one hook message line; test-reply-deps.py must fail, then restore.

Tests per done line: (1) sizes by git ls-tree; scripts-a-monitoring-under-19000 row; (2) toy before/after + negative control; (3) git diff --stat shows no added file and no regression.tsv change.

Could break: argparse help text (description=__doc__) is shorter; no toy reads it. Host is Windows, so many shell toys fail identically before and after; the same-set comparison is the check.

Out of scope: any behaviour change, new files, regression rows, requirement text.
