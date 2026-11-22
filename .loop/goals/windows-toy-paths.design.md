# Design: windows-toy-paths

## Problem

Three toys fail on Windows only, and only in their fixtures. test-link-form-note.sh and test-docs-link.sh write a link to a
PRD file by its Windows temp path (`pwd -W`, for example `C:/Users/<name>/AppData/Local/Temp/...`); DOC-19 correctly flags
`/Users/` as a path outside the repo, so the wiki step refuses the fixture and the toys never print their PASS lines.
test-home-guard.py's registry case printf's `C:\Users\...` into repos.json, the backslashes make the JSON invalid, and the
guard names `schedule/repos.json` instead of `schedule/repos.json#fixture`. Product code is right in both cases.

## Approaches

1. Change the product: let DOC-19 or the home guard accept these shapes. Cheap, but it weakens a rule the owner relies on
   (a `/Users/` path in a link must stay flagged) and is outside this goal's conditions. Rejected.
2. Fix only the fixtures. (a) For the link toys: give the fixture a PRD path that holds no `/Users/`: when `pwd -W` shows
   one, make a directory junction at the drive root (`cmd //c mklink /J C:/loop-toy-<pid> <temp dir>`, no admin needed) and
   build the link from it, removed in the toy's exit trap; on the Mac `pwd` is used as now. (b) For the guard: write the
   registry path with forward slashes (`${d//\//}`), so the JSON is valid and the entry is still a temp path.
   Cost: a few lines per toy. Risk: the junction leaks if the trap is skipped; mitigated by removing it first on start.

## Chosen

Approach 2. It keeps DOC-19, the home guard and every product script unchanged.

## What each done line needs

1. The two link toys build their PRD link from the junction path on Windows, so DOC-19 raises nothing and the wiki step passes;
   test-link-form-note.sh prints "PASS: new code: the wiki step merge.py runs finds nothing and passes".
2. test-home-guard.py's reg-toy case writes a forward-slash path; the leak line then names `schedule/repos.json#fixture`.
3. The control: a toy step that puts a `/Users/` path in a link and runs `docs.py check` and expects the DOC-19 finding. The
   existing negative control in test-link-form-note.sh covers the old code; this adds the `/Users/` one without a new row.

## Open questions

None for the owner. Whether the junction route works in the PC lane's sandbox is proven by running the toys there (qa).
