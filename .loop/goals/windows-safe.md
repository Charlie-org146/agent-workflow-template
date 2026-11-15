# A pull request that adds a POSIX-only call or breaks the package fails its own lane, so main stays Windows-safe and packageable

- Slug: windows-safe
- Touches: dev/package.py, dev/toy, skills/workflow-docs/scripts/prd.py, skills, .loop/regression.tsv, docs/wiki

## Done lines

Frozen. A wrong done line needs a new goal.

1. On a toy tree, a script naming fcntl outside the lock shim, os.getuid, os.killpg, os.getpgrp, os.O_NOFOLLOW, signal.SIGHUP, os.kill(pid, 0) or os.WNOHANG without its guard fails the check with its file and line; the real tree passes
2. dev/package.py passes on main: every script at most 20,480 bytes, at most 99 files, and no Safety or Disclosure failure
3. bash dev/toy/test-pods.sh size no longer fails on caps below the committed script sizes

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
1. Add `os.getuid()` with no guard to any script under `skills/*/scripts`, then run `python3 dev/toy/test-windows-safe.py`.
   Expect: `FAIL` naming that file, its line and `os.getuid`; remove the line and the run ends `ALL PASS`.
2. Run `python3 dev/package.py --out dist/check.zip`.
   Expect: `PASS: 98 files` and no `FAIL` line.
3. Run `bash dev/toy/test-pods.sh size` on a Linux or Mac machine.
   Expect: `PASS: the touched scripts stay within their budgets`.

