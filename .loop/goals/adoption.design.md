# adoption: design

## Problem
v1.0.0 item 4 "adoption proven" has five open requests (#2877 template version stamp, #1408 prerequisite checklist and strict
replay, #1409 adopt several repos in one pass, #1410 connector probe, #1411 scoped private-name patterns) and fourteen open
`health: adoption MIG_*` findings. Setup's requirements SET-11, SET-12, SET-14 and SET-15 are Reviewed but have no test, so each
shows "not enforced". Every script of workflow-setup, private.py and the docs scripts sits at its 20,480-byte cap, and the
package is at its 98-file cap, so each feature has to pay for itself by trimming.

## Approaches
1. One new `adopt.py` for everything. Cheapest to read, but the package is over its file cap (99 on main, windows-safe owns
   it): rejected.
2. Grow the existing scripts, trimming prose that `--help` and SKILL.md already carry, and place each command next to what it
   reads: the checklist and replay in `setup.py`, the multi-repo adoption in `board.py repos` (the operation session's own
   command, 2 KB free), the connector listing next to the replay, the pattern scope in `private.py`. Each toy is a python
   script (shell-neutral) run by a row seen red. Chosen.

## Chosen
- #2877: already true for an installed package (setup.py stamps `agents.installed_version()` from workflow-package.json;
  a source checkout has none, so it stays empty by design). Close with a toy that adopts a repo from a fake package layout
  and finds `template_version` set and `update --apply` with nothing to stamp.
- #1408: `setup.py prerequisites` prints one line per need (git, python3, gh installed, gh signed in, real symlinks, platform
  calls) with its exact fix, and every run prints it before it writes; `setup.py replay` walks `dev/toy/adoption-golden.tsv`
  in order, checks what this machine can observe for each step, stops at the first mismatch saying what differs and the
  step's fix from the fixture, and never accepts a looser result; a step it cannot observe from a script (workers, the first
  live check-in) says so and stops there instead of passing.
- #1409: `board.py repos adopt OWNER/NAME ...` (and `repos adopt --recent N` listing by last push through gh) clones each
  into one folder, follows it, runs `update --apply` and ends with the board's version line for each.
- #1410: the replay's step 6 and `setup.py connectors` list, per followed repo, each connector its PRDs name (mail,
  calendar, file store, notification channel) as `connected`, `needs sign-in` or `missing` from a read-only probe command
  the agent's session sets in `LOOP_CONNECTOR_PROBE`, never enabling one.
- #1411: a pattern line may start with `public:` or `repos=a,b:`; `private.py` applies it only to a matching repo, and
  setup explains the list when it seeds it.
- MIG findings: run `health.py check`, close each issue the check no longer reports with the proof, fix the rest that this
  machine can, and name the ones it cannot (#3822, the Mac's schedule).

## What each done line needs
Each has a python toy case and a row seen red (`regression.py red`); no row calls bash or `grep -q` on a toy's output.

## Open questions (recommended answers taken)
- Which script has room? None; each addition trims the same file first (docstrings, comments, repeated text).
- Real GitHub, Notion or a real connector? Never: fakes on PATH and in environment variables.
