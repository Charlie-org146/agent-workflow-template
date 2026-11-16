<!-- workflow-docs -->
# How to use Setup

## What it's for

Turns any repo into a ready workspace for any agent without ever blocking, judged by health before and after, keeps it in step with the template, adopts several repos in one pass through `board.py repos adopt`, and lists, with the exact instruction, what the owner must still do on a new machine.

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
| "Install the reply hook" | Operation-session replies that don't follow the check-in layout are blocked, saying what is missing. |
| "Is there a newer template version?" | It shows what the newest release brings and which skill files you changed here; nothing is written. |
| "Update this repo to the newest template" | The skills update, and this repo's new settings, entry point and agent files land on an update branch for you to merge; your own values and pages are kept. |
| "Send my skill fix back to the template" | It drafts one issue with the diff and no repo name, and files it once you say so. |
| "Wire the skills into CLAUDE.md and AGENTS.md" | Both files get the same block pointing every new session at `.loop/START.md`; your own text is kept. |

## URLs and deployments

- Wiki: [Setup](https://github.com/jcl2018/agent-workflow-template/wiki/Setup)
- Milestone: [Setup](https://github.com/jcl2018/agent-workflow-template/milestone/9)
- Releases: https://github.com/jcl2018/agent-workflow-template/releases

## Links

- PRD page: [Setup](Setup)
- Backlog: [Backlog: Setup](https://github.com/jcl2018/agent-workflow-template/milestones)

<!-- kept how-to-use-docs@14272c88 -->
