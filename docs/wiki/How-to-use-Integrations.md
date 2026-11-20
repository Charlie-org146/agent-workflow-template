<!-- workflow-docs -->
# How to use Integrations

## What it's for

Lets the loop work with systems outside the repo, such as a PRD kept in Notion or a milestones page, through one contract: the repo's copy stays the source of truth, a difference is a delta and never an overwrite, and nothing is written outside without a switch and an accepted delta.

### What's delivered

| Component | Kind | What it is | How a user uses it |
|---|---|---|---|
| `workflow-docs` | Skill | Keeps the wiki pages in the repo and syncs the ones that opt in to an outside document. | Say "Sync the PRDs" or "What differs from Notion?". |
| `docs.py` | Command | Compares the repo's copy with the outside source and accepts one side's text. | `python3 skills/workflow-docs/scripts/docs.py sync --dry-run`. |
| `.loop/docs.tsv` | API/file contract | The map of pages to paths, with the optional PRD source of a page that opts in. | Add the page's `url:` or `mcp:` source as the third column. |

### System diagram

```text
[Skill: workflow-docs | the agent session] --sync, accept--> [Command: docs.py | the repo checkout]
[API/file contract: .loop/docs.tsv | the repo] --names the page's PRD source--> [Command: docs.py | the repo checkout]
[Command: docs.py | the repo checkout] --reads, and writes only an accepted delta--> (the outside document)
[Command: docs.py | the repo checkout] --posts each delta once--> (GitHub issue on the Backlog milestone)

Legend: a box is Kind, Component and where it runs; --text--> a flow of data or control; (text) a part outside the table.
```

## How to reach or run it

Say these to the agent in the operation session; the feature page has the rules.

| You say | What happens |
|---|---|
| "What differs from Notion?" | `docs.py sync --dry-run` lists each delta with the page, the ID, which side changed and both texts, and exits 1 when there is one. |
| "Accept the repo's text for DOC-1" | `docs.py sync --accept Documentation:DOC-1=repo` writes only that text to the outside document and closes the delta. |
| "Accept the document's text for DOC-1" | `docs.py sync --accept Documentation:DOC-1=source` writes only that text to the repo's copy and closes the delta. |

Each requirement and how it is delivered:

- INT-1: One contract for every integration. An integration is declared by a page's PRD source in `.loop/docs.tsv` or by `milestones_source` in `.loop/config.json`, and each is opt-in; the single registry is not built yet.
- INT-2: The repo stays the source of truth. Every check reads the repo's copy, and `docs.py sync` against a source it cannot reach prints `not connected: ...`, changes nothing and exits 0.
- INT-7: PRDs kept in an outside document. A page opts in by its PRD source in `.loop/docs.tsv`, and the repo's copy at `.loop/prd/PAGE.md` stays the one every check reads.

### Skill: workflow-docs
- **Say:** "What differs from Notion?"
- **Command:** `/workflow-docs sync`

### Command: docs.py
- **Command:** `python3 skills/workflow-docs/scripts/docs.py sync [--dry-run] [--accept PAGE:ID=repo|source]`
- **Dry run:** `--dry-run` only reports each delta and exits 1 when one is open; nothing is written.
- **Reads:** `.loop/docs.tsv`, `.loop/config.json`, `.loop/prd/` and the outside source where a reader is set.
- **Writes:** `.loop/prd/PAGE.md`, one GitHub issue per delta, and the outside document only for an accepted delta.
- **Exit codes:** 0 when every page is in step or an integration is not connected; 1 when `--dry-run` finds a delta.

### API/file contract: .loop/docs.tsv
- **Path:** `.loop/docs.tsv`
- **Fields:** page name, a tab, the paths it describes (comma separated), and an optional third column with the page's PRD source (`url:` or `mcp:`).
- **Example:** `Delivery`, a tab, then `skills/workflow-delivery`.
- **Writer:** `docs.py add`, or the owner by hand.
- **Reader:** `docs.py check`, `audit`, `sync` and `publish`, and health.

## URLs and deployments

- Wiki: [Integrations](https://github.com/jcl2018/agent-workflow-template/wiki/Integrations)
- Releases: https://github.com/jcl2018/agent-workflow-template/releases

## Links

- PRD page: [Integrations](Integrations)
- Backlog: [Backlog: Integrations](https://github.com/jcl2018/agent-workflow-template/milestones)

<!-- kept gap-cheap-fixes@c917e3165 -->
