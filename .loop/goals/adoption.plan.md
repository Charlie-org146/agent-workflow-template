# adoption: plan

Design: `.loop/goals/adoption.design.md`, approach 2 (grow existing scripts, trim to pay for each).

## Build steps, in order

1. `dev/toy/test-adoption-proof.py` (python, shell-neutral): case 1 adopts a temp repo from a fake package layout
   (a copy of `skills/` with `workflow-package.json`) and asserts `template_version` is in its config and
   `update --apply` has nothing to stamp (#2877). Row seen red with a break that stops the stamp.
2. `setup.py` (20,328 bytes, files in `skills/workflow-setup/scripts/`): shorten the module docstring (`--help` text is
   mirrored in SKILL.md), add `prerequisites` (git, python3, gh installed and signed in, real symlinks, the platform calls
   fcntl/getuid) and print it before every run writes; toy case 2 with fake `gh`/`git` on PATH; rows red.
3. `setup.py replay`: the golden fixture's steps 1 to 6 observed on this machine, first mismatch stops with what differs and
   the fixture's fix; steps 7 and 8 say they need the live operation session and stop there; toy case 3.
4. `setup.py connectors`: connectors each followed repo's PRDs name, state from `LOOP_CONNECTOR_PROBE`, never enabling;
   toy case 4 (fake probe).
5. `board.py repos adopt` (18,464 bytes, 2 KB free) with a fake `gh` and `git clone` from a local bare repo; toy case 5.
6. `private.py` (20,360): scoped lines `public:` and `repos=a,b:`; trim, add, toy case 6; setup's seed text explains it.
7. Fourteen MIG findings: `health.py check` now, close the ones no longer reported with that proof, fix the rest.
8. Docs the check requires (README rows, SKILL.md command map, references), rendered Tests, Setup page sub-bullets only
   if reviewed text changes (an owner record is then asked for, never forged).

## Tests (each seen red before the change)
One python toy, `dev/toy/test-adoption-proof.py`, one case per done line; one row per case through `regression.py add`
with `python3 dev/toy/test-adoption-proof.py CASE`, then `regression.py red` with a break command.

## What could break
Script size caps (checked with `dev/package.py` and the headroom row), the `private.py` list format (existing lines keep
meaning), setup's output other toys read.

## Out of scope
The docs and release scripts (scripts-b is trimming them), package.py, the Mac's schedule (#3822).

PENDING: none
