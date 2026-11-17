# hook-stub-mark plan

Checked: seed.py (18,961 LF bytes) holds MARK, STUB with its mark line, call_of, hook_state, git_hooks and show; setup.py parses `--git-hooks`, `--check`, `--remove`; git_hooks refuses to write from a path under /loop/worktrees/, so the toy runs setup from a temp copy of the skills.

## Build steps
1. `dev/toy/test-hook-stub-mark.py`: copy workflow-setup and workflow-delivery into a temp folder, make a temp git repo, run `setup.py --repo R --git-hooks`, then `--git-hooks --check`; check all three hooks read `installed` and exit 0. Second repo: write a hand-made commit-msg hook first; check setup says it is left alone, `--check` reports `foreign`, and the text is unchanged.
2. Rows `hook-stub-mark-own` (done 1) and `hook-stub-mark-foreign` (done 2), each seen failing against a stub whose mark line is removed (own) and against a setup that overwrites the foreign hook (foreign).

## Test per done line
Done 1: hook-stub-mark-own. Done 2: hook-stub-mark-foreign.

## What could break
A shell-less machine (hooks are `#!/bin/sh` text only; the toy never runs them) and a temp path with a quote or percent sign, which setup refuses; the toy marks itself `# windows: ok` only if both pass on Windows.

## Out of scope
Hooks written by the unmarked stub before 14e19abe (they stay foreign until removed by hand); changes to seed.py or setup.py.

PENDING: none
