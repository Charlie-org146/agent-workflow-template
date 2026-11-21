# Design: trust-fail-closed

## Problem

`operate.untrusted(folder)` (skills/workflow-monitoring/scripts/operate.py, line 127) is the one check that stops a worker session from being bound to, or handed work in, a worktree the owner never trusted in Claude Code (GRD-4). Its `except` branch returns "" (trusted) when ~/.claude.json is missing, unreadable, unparseable or has no `projects` map. So the check fails open: anything that makes the file unreadable turns the guard off. Issue #5741. Both callers (`sessions.py` bind line 234 and assign; `worker.py` line 312) treat "" as go.

## Approaches

**A. Fail closed in the one function.** Compute `ok` inside the try, set `ok = 0` in the except, and return one refusal for both "no trust entry" and "no readable file". Both callers already `sys.exit(why)` on a non-empty line, so nothing else changes. operate.py is at 20,455 of 20,480 bytes (GRD-20); the rewrite measured 20,467, so it fits with 13 bytes spare and adds no file.

**B. Check the file in each caller.** Two more copies of the rule and more bytes in scripts that are also near the cap. Rejected (DRY, size).

**C. A new helper module.** A new file under skills/, which the done lines forbid. Rejected.

## Chosen: A

Same refusal text as today ("ask the owner to trust FOLDER (FOLDER_TRUST)"), so the plain reason is the one the owner already knows; it now also covers a missing file.

## What each done line needs

1. A toy with HOME holding no .claude.json, an empty file, a file of invalid JSON, a directory in its place, and a file with no `projects` key: bind refuses each with "ask the owner to trust" and names the folder; the file is not created or changed.
2. The existing "trust" toy keeps its trusted-root and trusted-parent cases (the control); its old negative control, "with no ~/.claude.json bind goes through", becomes the refusal case above, and selfcheck's "no ~/.claude.json no folder is called untrusted" case likewise. Toys that bind under a temporary HOME gain a trusting .claude.json so they test what they tested.
3. Run the docs, package and private-name checks; add no file under skills/.

## Open questions

- A machine with no ~/.claude.json at all (Claude Code never run) now cannot bind. That is the intent: nothing is trusted. Recommended: yes.
- #5743 (case folding) and the unmerged pc-path-trust (#5722) touch the same function; merge up when it lands, and stop if the 13 spare bytes do not hold.
