# homeguard-skills-main design

## Problem
The home guard (`dev/toy/homeguard.py`) snapshots the owner's real `~/.workflow-loop` when a toy starts and fails the toy at exit on any change. Other sessions write there while a toy runs: a checkout of `skills-main` rewrites `.loop/START.md` and `config.json`, and the registry `schedule/repos.json` gains a real repo. The guard reported a false LEAK (#4760: doc-milestone-sync lost a PR try on machine-done-7, a row that passes alone). The goal is to tell a toy's own writes from another process's.

## Approaches
1. **Judge by what the write is** (chosen). `skills-main` is a git checkout: judge it by `git status`, so another session's move (clean afterwards) is invisible and a toy's edit or new file shows. The registry: judge only entries that point into the system temp folder (a toy's fixture; another session registers real repos), or a registry that no longer parses; `repos.json.bak-*` is not judged. Cost: three functions in homeguard.py (about 50 lines). Risk: a toy that registers a real-looking path, or edits skills-main and commits, passes; no toy takes either path.
2. Attribute writes to a process. Needs the writer's pid at write time; unavailable after the fact.
3. Retry the check. Hides real leaks.

Strict mode (a fresh home) still hashes everything, so the proof for toys-no-leak is unchanged.

## What each done line needs
1. A toy body that, like another session, adds a real-path entry and a backup to the registry, or commits a new START.md in a skills-main checkout, is not a LEAK (row homeguard-other-writer).
2. A toy that registers a temp-folder fixture, edits a tracked skills-main file or adds an untracked one still fails with a LEAK line naming it (row homeguard-own-write).

## Open questions
None for the owner.
