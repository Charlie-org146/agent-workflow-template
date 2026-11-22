# Plan: windows-toy-paths

Depth condensed (TD871: toy fixtures only, no product file). If any product file turns out to be needed, stop: the goal goes
back to full depth and to top.

## Checked against the code

- dev/toy/test-link-form-note.sh line 149 and dev/toy/test-docs-link.sh line 169 set `dw=$(cd "$d" && { pwd -W || pwd; })`; both
  write `$dw/...` into a wiki page's `PRD:` line (and test-docs-link.sh into reader.py arguments). counting.py PERM_PRIVATE and
  prdcopy.py AWAY hold the `/Users/` shape; that is what flags it. Neither file changes.
- dev/toy/test-home-guard.py line 73 builds the registry entry with bash `printf '{"repos": {"fixture": {"path": "%s"}}}' "$d"`
  where `d="$TOY_REAL_WL/../fixture"`; TOY_REAL_WL is a Windows path with backslashes, which makes the JSON invalid.
  dev/toy/homeguard.py registry() then falls back to the key `schedule/repos.json`. homeguard.py does not change.
- dev/toy/reap.sh offers `toy_on_exit CMD`: cleanup runs on exit, INT, TERM, HUP and PIPE.

## Build steps (after the plan gate)

1. Both link toys: after `dw=` is set, if it holds `/Users/` (only native Windows), make a junction `C:/loop-toy-$$` to `$d`
   with `cmd //c mklink //J "$(cygpath -w C:/loop-toy-$$)" "$(cygpath -w "$d")"` (`//J` so MSYS does not rewrite the flag; both names
   as backslash Windows paths; target is the real fixture dir; first removing a stale one of that name; then a `[ -d ]` check), set `dw` to the junction path, and register
   `toy_on_exit 'cmd //c rmdir "C:\loop-toy-$$"'`. Removal is `rmdir` only, never `rm -rf`, which could follow the junction
   into the real fixture. If mklink fails the toy prints a FAIL naming it (never a silent skip).
2. test-home-guard.py reg-toy case: write the path with forward slashes: bash `d=${d//\//}` before printf, which inside the Python
   single-quoted source line 73 is written with doubled backslashes so bash receives exactly `${d//\//}` (a bare `${d//\//}` would delete every slash).
3. Control in test-docs-link.sh: a page whose PRD link holds a literal `/Users/x/prd.md` line; `docs.py check` must report the
   `LINKS ... DOC-19 ... outside this repo` text, not just any finding ("PASS: a /Users/ path in a link is still flagged (DOC-19)"). Runs on every platform.

## Test per done line (no new rows: the existing rows run these toys)

1. The "merge.py runs finds nothing" PASS string exists only in test-link-form-note.sh; for test-docs-link.sh the check is no FAIL and
   its own PASS lines. link-page-passes and gate-untouched-not-refused: seen red on the PC (issues #5763, #5765), expected green after.
2. home-guard-catches-leak: seen red on the PC, green after.
3. The control PASS line in test-docs-link.sh, which link-page-passes already requires to have no FAIL. Net rows 0.

## The junction, and why it is safe

#5758's rule is against symlinked paths in lane clones, where a link can point a lane's work at another tree. A toy fixture's
junction is a directory junction (no admin, not a file symlink), made at the drive root only when the temp path holds
`/Users/`, points at the toy's own temp directory and nowhere else, and exists only for the toy's run. The lane's clone
and cwd are untouched. If the toy is killed before the trap (SIGKILL): a stale `C:\loop-toy-<pid>` junction stays; it holds
no data (deleting it with rmdir leaves the target alone), the next run removes any stale junction of its own pid name first, and
`reap.sh --sweep-dead` is the existing path for a killed toy's processes. A leftover costs one empty-looking drive-root entry.

## What could break

- A machine whose drive root is not writable: mklink fails, the toy FAILs with a clear line; handled by build step 1.
- The Mac and Linux are unchanged: the junction branch runs only when `dw` holds `/Users/` and `uname` is MINGW/MSYS.
- Windows-only: fixes are proven by running the three toys on the PC lane (qa), then the Mac ships.

## Out of scope

make.sh, DOC-19, the home guard, every product script, the known list, G2's toys (cleanup, restart-tick).

## Review

Red-team (fresh reviewer, run from this worktree: pwd /c/Users/chang/code/agent-workflow-template/.git/loop/worktrees/windows-toy-paths, HEAD 43e9d11a3): CHANGES on escaping, mklink quoting, the PASS string and the control text; all four are folded in above. No product file is needed.
