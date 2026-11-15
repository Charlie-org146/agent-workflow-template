# Design: home-leak

## Problem
Issue 4393: dev/toy/test-settings.sh set HOME to a temp dir and then wrote "limit": 99 to os.path.expanduser("~/.workflow-loop/flow.json").
On Windows Python's expanduser reads USERPROFILE, not HOME, so the toy rewrote the owner's real flow file and every lane died.

## Approaches
1. Isolate each toy (USERPROFILE beside HOME, LOOP_FLOW and LOOP_HEALTH at temp paths) and add a harness guard that hashes
   the real ~/.workflow-loop before and after each toy. Cost: a mechanical edit of the toys that set HOME, one new small
   script, a few lines in reap.sh. Risk: low; the guard only reads.
2. Set HOME and USERPROFILE to a fresh temp dir for every toy in the harness. Cost: tiny, but toys that need the real home
   (git identity, gh) could break, and the Windows-skipped toys cannot be run here to find out. Risk: high.

## Chosen
Approach 1. dev/toy/reap.sh (sourced by every shell toy) exports LOOP_FLOW and LOOP_HEALTH at temp paths, snapshots the
real ~/.workflow-loop through dev/toy/homeguard.py snap, and at exit runs homeguard.py diff: any added, removed or changed
file there prints a LEAK line and fails the toy (TOY_REAL_WL points the guard test at a throwaway folder, so it never touches
the real one). Every `export HOME=` line in dev/toy/test-*.sh gets `export USERPROFILE="$HOME"` after it, and the inline
HOME= forms get USERPROFILE too. Python toys that put HOME in an environment add USERPROFILE.

## The leaking toys found (grep for HOME, expanduser and ~/.workflow-loop in dev/toy)
- test-settings.sh: the known one (writes flow.json by expanduser).
- 74 `export HOME=` lines across the shell toys set HOME alone; each now sets USERPROFILE too.
- test-govern.sh (an inline HOME= for setup.py --bare), test-guard-enforce.sh and test-pods.sh (inline HOME= forms),
  test-monitoring.sh (HOME inside a longer export), test-health-repo-rules.py (HOME in an env dict), test-health-on-windows.py
  (no HOME at all while running the local schedule register).
- test-review-depth.sh writes "~/.workflow-loop/flow.json" through its own HOME, now isolated with USERPROFILE.
Python toys do not source reap.sh, so the guard covers the shell toys; the static check in test-home-guard.py covers every toy.

## Each done line
1. USERPROFILE and the LOOP_* overrides: test-home-guard.py isolate leg reads every toy.
2. The guard: test-home-guard.py guard leg runs real toys that leak and ones that do not.
3. The list above.
4. Rows seen red, issue 4393 closed with proof, byte limits and package count kept.

## Open questions
None for the owner.
