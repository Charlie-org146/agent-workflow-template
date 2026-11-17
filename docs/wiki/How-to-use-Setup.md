<!-- workflow-docs -->
# How to use Setup

## What it's for

Turns any repo into a ready workspace for any agent without ever blocking, judged by health before and after, keeps it in step with the template, adopts several repos in one pass through `board.py repos adopt`, and lists, with the exact instruction, what the owner must still do on a new machine.

### What's delivered

| Component | Kind | What it is | How a user uses it |
|---|---|---|---|
| `workflow-setup` | Skill | Turns any repo into a ready workspace for any agent without blocking it. | Say "Set up this repo"; it shows what it found and writes a setup branch. |
| `setup.py` | Command | Surveys a repo and writes its `.loop/` config on a branch. | `python3 skills/workflow-setup/scripts/setup.py`. |
| `unattended.py` | Command | Checks what an unattended run needs, replays the golden adoption and lists connectors. | `python3 skills/workflow-monitoring/scripts/unattended.py prerequisites`. |

## How to reach or run it

Say these to the agent in the operation session; each feature page has the exact commands.

| You say | What happens |
|---|---|
| "Set up this repo" | It shows what it found and would add, then writes it on a setup branch for you to review and merge. |
| "Show me what setup would do first" | Every file it would add or convert is listed; nothing is written. |
| "Show me every setting" | Each repo and private setting, with its default and a one-line explanation. |
| "Fill in any missing settings" | Missing repo settings are added with their defaults; your own values are kept. |
| "Check this machine before setting up" | One checklist of git, python3, gh installed and signed in, real symlinks and the platform, each gap with its exact fix; a setup run prints it first and is never blocked by it. |
| "Replay the first adoption against the golden run" | The eight golden steps are compared with what this machine shows and it stops at the first mismatch, saying what differs; the live check-in step is reported as not observed, never passed. |
| "Which connectors do my repos need?" | Each connector a followed repo's PRDs name is listed as connected, needs sign-in or missing, and nothing is enabled for you. |
| "Install the reply hook" | Operation-session replies to a scheduled or asked-for check-in that don't follow the check-in layout are blocked, saying what is missing; it also installs a prompt hook that skips the model turn of a scheduled check-in when nothing changed. |
| "Is there a newer template version?" | It shows what the newest release brings and which skill files you changed here; nothing is written. |
| "Update this repo to the newest template" | The skills update, and this repo's new settings, entry point and agent files land on an update branch for you to merge; your own values and pages are kept. |
| "Send my skill fix back to the template" | It drafts one issue with the diff and no repo name, and files it once you say so. |
| "Wire the skills into CLAUDE.md and AGENTS.md" | Both files get the same block pointing every new session at `.loop/START.md`; your own text is kept. |
| "Set up a second machine" | `machine.py` in the clone lists the skill links, hooks, private-names file, mailer, check-in and scheduled tasks it would install; `apply` installs them and prints the owner checklist. |

Each requirement and how it is delivered:

- SET-1: One command adopts a repo. Example, from the adopt-set-1 test: given SET-1, when the toy adopt-and-update test runs, then it holds.
- SET-2: Layered settings. Example, from the settings-reference test: given every repo and private setting, when the reference is read, then each is listed with its default and a one-line explanation.
- SET-4: Updates flow both ways. Example, from the adopt-set-4 test: given SET-4, when the toy adopt-and-update test runs, then check shows the change, apply keeps the repo's data and lands the repo half on its branch.
- SET-5: A self-describing workspace. Example, from the adopt-set-5 test: given SET-5, when the toy adopt test runs, then the design guide is installed and setup's .loop/START.md holds the opener and every part.
- SET-6: Adoption is proven. Example, from the adopt-fixture-existing-checks test: given a repo whose config lists its own checks (pull request 83), when setup adopts it, then the written config keeps every check and the seeded row runs all of them.
- SET-9: Learn from a repo already set up. Example, from the set9-from-borrows test: given an adopted repo as the model, when setup runs with --from, then it borrows the portable settings and page shape, holds auto_merge and reply_hook until --allow, keeps its own base and agent command, changes nothing on a second run and never writes to the model.
- SET-10: The right format for every agent. Example, from the agents-wire test: given a repo, when setup or agents.py wire runs, then CLAUDE.md and AGENTS.md hold the same workflow-loop block, text outside it is kept, and a second run changes nothing.
- SET-11: Prerequisites first, then a strict replay of the first adoption. Example, from the adoption-golden test: given the golden first adoption, when its fixture and SET-11 are read, then the fixture holds steps 1 to 8 in order, each with a check, golden result and fix, no machine path or account, and SET-11 names it and its first-mismatch stop.
- SET-12: Adopt all my repos in one pass. Example, from the adopt-many-one-pass test: given two GitHub repos chosen from the recent list, when repos adopt runs, then both are cloned into one folder, followed and set up, each reporting its template_version.
- SET-13: Workers are app sessions I can see. Example, from the set13-hooks-once test: given a repo where setup.py --reply-hook and --govern-hook run repeatedly, even on a Windows path or over a file already holding two govern hooks, when settings.local.json is read, then it holds exactly one reply hook and one govern hook.
- SET-14: The connectors each repo needs are checked. Example, from the adopt-connectors-probed test: given followed repos whose PRDs name connectors, when the connectors are listed, then each is connected, needs sign-in or missing from a read-only probe, and nothing is enabled.
- SET-16: A repo is judged fully migrated by one command. Example, from the migration-clean test: given a clean private repo and a clean public repo, both recorded mac with the task registered, when migration-check runs, then each prints MIGRATION OK and exits 0.

### Skill: workflow-setup
- **Say:** "Set up this repo"
- **Command:** `/workflow-setup setup`

### Command: setup.py
- **Command:** `python3 skills/workflow-setup/scripts/setup.py [--dry-run]`
- **Dry run:** `--dry-run` lists every file it would add or convert and writes nothing.
- **Reads:** the repo and its settings.
- **Writes:** `.loop/` files, README and agent files on a setup branch.
- **Exit codes:** 0 on a ready repo; setup never blocks, and a refusal prints its fix.

### Command: unattended.py
- **Command:** `python3 skills/workflow-monitoring/scripts/unattended.py prerequisites` (also `replay` and `connectors`)
- **Dry run:** none needed: each part only reports.
- **Reads:** this machine's tools and the followed repos' PRDs.
- **Writes:** nothing.
- **Exit codes:** 0 after it prints its checklist; a gap is a `MISSING` line with its exact fix.

## URLs and deployments

- Wiki: [Setup](https://github.com/jcl2018/agent-workflow-template/wiki/Setup)
- Milestone: [Setup](https://github.com/jcl2018/agent-workflow-template/milestone/9)
- Releases: https://github.com/jcl2018/agent-workflow-template/releases

## Links

- PRD page: [Setup](Setup)
- Backlog: [Backlog: Setup](https://github.com/jcl2018/agent-workflow-template/milestones)

<!-- kept hands-off-operation@8d9afd42 -->
