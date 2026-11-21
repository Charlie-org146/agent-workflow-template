# A Codex worker can commit and push from its sandbox (owner o676, narrowed by TD537): the Codex profile gains writable roots for exactly the repo's git objects/, refs/, logs/ and worktrees/<this worktree>/ (filled in at launch like WORKTREE, from git rev-parse --git-common-dir), never hooks/, config or info/; the guard refuses a profile naming hooks, config, info, danger-full-access or the bypass flag; if a push needs another path, the worker stops and names it

- Slug: codex-git-root
- Touches: skills, dev/toy
- ETA: 305 active minutes (estimate 241m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a stubbed launch, then the Codex args carry exactly those four writable roots for this worktree and nothing else, and a profile adding hooks/, config, info/, danger-full-access or the bypass flag is refused (toy, negative controls)
2. Given the pull request, then its rows are SEEN RED, it cites o676 and TD537, a live Codex goal commits in its sandbox, and docs.py check and criteria.py render --check pass
3. Given this goal's diff, then no file is added to the package (100 files), no script newly crosses 19,000 bytes, every script stays under 20,480, and the private scan is clean

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
