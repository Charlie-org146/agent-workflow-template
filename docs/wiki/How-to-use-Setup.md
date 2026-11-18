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

### System diagram

```text
[Skill: workflow-setup | the agent session] --surveys the repo--> [Command: setup.py | the repo checkout]
[Command: setup.py | the repo checkout] --writes it--> (.loop/ config on a branch)
[Command: unattended.py | the repo checkout] --checks what an unattended run needs--> (connector and prerequisite list)

Legend: a box is Kind, Component and where it runs; --text--> a flow of data or control; (text) a part outside the table.
```

## How to reach or run it

Say these to the agent in the operation session; each feature page has the exact commands.

**Getting started**

From install to one finished goal.

1. **Install.** Run `dev/install-local.sh`. It links each `skills/workflow-*` folder into `~/.claude/skills` (or
   `$CLAUDE_SKILLS_DIR`) and prints `LINKED <name>`. It skips a name that is already a real folder. For another agent,
   copy the `skills/` folders into its skills folder.
2. **Set up your repo.** Run `/workflow-setup`. It writes `.loop/config.json`, `.loop/queue.md` and `.loop/findings.md`
   on a branch called `workflow-setup`. Preview with `/workflow-setup setup --dry-run`, using the path to the skill's
   folder. Then allow the
   tools a background agent needs in `agent_command` (for example
   `["claude", "-p", "--allowedTools=Bash,Read,Write,Edit"]`; you choose the list), and review and merge the branch
   yourself. The other skills read the config from the base branch. Setup also writes `.loop/START.md`, the entry point
   any new session reads first, and the same workflow-loop block into `CLAUDE.md` and `AGENTS.md`, so Claude Code and
   Codex run the same loop.

   To run the loop from Codex, use `codex exec -s workspace-write` with these writable roots in
   `sandbox_workspace_write.writable_roots`: the repo's git folder, its remote, and `~/.workflow-loop` (setup and `go`
   write the private settings there; a read-only home leaves them unwritten and `go` is refused). The git folder root
   also lets a run write `.git/hooks`, which a narrower `.git/loop` root would not. The first setup run exits 1 until
   `agent_command` names the tools you allow. Pick the model yourself (`-m`): a model your account does not support is
   rejected before anything runs. `dev/toy/test-codex.sh` proves this on a clean toy repo and is skipped, never passed,
   where Codex cannot answer.
3. **Start a goal.** From the main checkout, on the base branch:
   `/workflow-monitoring go "add result caching" --done "repeat searches are served from the cache"`. Done lines are
   frozen once the goal starts, so make each one provable before the pull request, by a test or by what a person
   can see (see [Delivery](docs/wiki/Delivery.md)). Setup filled `~/.workflow-loop/flow.json` with `built-in` steps,
   so this works with no skill suite; name your own skill for any step there and it replaces that step's routine.
4. **Watch it.** `/workflow-monitoring watch` starts queued goals in their own worktrees, prints what changed, and ends
   with what waits on you. Use `report` for a snapshot.
5. **Answer what waits on you**, in the exact words `watch` prints.
6. **Review.** The goal ends at a pull request. A monitored goal answers `leave` by itself, unless you started it with
   `--release ask`; then it waits for `cut <slug>` or `leave <slug>` (see [Delivery](docs/wiki/Delivery.md)). With
   `"release_auto": true`, it decides from its diff and may cut a draft instead. Answer before you merge, because `cut`
   commits on the goal's branch. Review and merge the pull request yourself; nothing here merges unless `auto_merge` is on.
7. **Keep it current.** `/workflow-setup update --check` shows what a newer template version brings;
   `/workflow-setup update` applies it and puts this repo's generated files on a `workflow-update-vX` branch for you to
   merge. A skill you fixed here is kept, and `/workflow-setup update --propose` sends the fix back to the template.

**File reference**

In the repo:

| File | Holds |
|---|---|
| `.loop/config.json` | Base branch, agent commands, risky paths, wiki folder |
| `.loop/queue.md` | Goals to run, one line each |
| `.loop/goals/<slug>.md` | One goal: frozen done lines, plan, verify steps |
| `.loop/findings.md` | Open findings |
| `.loop/docs.tsv` | Each wiki page and the paths it describes |
| `.loop/regression.tsv` | Test rows |
| `.loop/regression-known.tsv` | Rows expected to fail, with a reason |
| `.loop/regression-red.tsv` | Red results proven on another runner, with runner and commit |
| `.loop/regression-runs.tsv`, `.loop/regression-issues.tsv` | Each row's last result; each defect test's issue state |
| `.github/workflows/regression.yml`, `.github/workflows/regression-pr.yml` | A public repo's regression routines (written by setup); health and a private repo's regression run on the Mac |
| `docs/wiki/` | Wiki pages, each starting with `<!-- workflow-docs -->` |

Outside the repo, run state lives in `<git common dir>/loop/`: `runs/<slug>.json`, `logs/<slug>.log`,
`dashboard.html`, `wiki.json`, `board.json`, `board.html`, `board-artifact.html`, `cadence` (minutes between
check-ins, or `off`) and `handoff.md`. Nothing there is committed. `board.py repos add` keeps a list of repo paths in `~/.workflow-loop/repos`, and
`~/.workflow-loop/flow.json` names your skill flow.

In this template: `skills/` (the seven skills; the full contract is `skills/loop-files.md`), `dev/` (install, package and
toy tests), `listing.json`, `VERSION`, `DECISIONS.md`, `FINDINGS.md`, `docs/ROADMAP.md` and `LICENSE`.

**License**

MIT. See [LICENSE](LICENSE).

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

<!-- kept hands-off-operation@f100bbe6 -->
