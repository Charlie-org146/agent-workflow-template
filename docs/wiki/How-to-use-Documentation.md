<!-- workflow-docs -->
# How to use Documentation

## What it's for

Keeps the wiki and README in one enforced format (feature pages are PRDs with no Usage section;.

### What's delivered

| Component | Kind | What it is | How a user uses it |
|---|---|---|---|
| `workflow-docs` | Skill | Keeps the wiki pages in the repo, finds stale ones and publishes them. | Say "Check the docs" or "Audit the docs and fix what you can". |
| `docs.py` | Command | Checks, audits and publishes the wiki pages. | `python3 skills/workflow-docs/scripts/docs.py check`. |
| `audit.py restamp` | Command | Re-stamps a page that is stale only by code its text still describes. | `python3 skills/workflow-docs/scripts/audit.py restamp SLUG PAGE...`. |
| `.loop/docs.tsv` | API/file contract | The map of wiki pages to the paths each describes. | Add a row with `docs.py add PAGE --paths A,B`, or edit the file. |

### System diagram

```text
[Skill: workflow-docs | the agent session] --check, audit, publish--> [Command: docs.py | the repo checkout]
[API/file contract: .loop/docs.tsv | the repo] --maps pages to the paths they describe--> [Command: docs.py | the repo checkout]
[Command: docs.py | the repo checkout] --a page stale only by code its text still describes--> [Command: audit.py restamp | the repo checkout]
[Command: docs.py | the repo checkout] --publish writes only the pages it wrote--> (GitHub wiki)

Legend: a box is Kind, Component and where it runs; --text--> a flow of data or control; (text) a part outside the table.
```

## How to reach or run it

Say these to the agent in the operation session; each feature page has the exact commands. A feature's routine runbooks may be written on its How-to-use page, under Runbooks, instead of on its PRD page; the docs check finds them there.

| You say | What happens |
|---|---|
| "Check the docs" | Every stale, missing, unmapped or unwritten page is listed with what is wrong, or you hear that the docs are clean. |
| "Audit the docs and fix what you can" | Mechanical fixes such as the Tests tables are made, and the wording left to rewrite is listed. |
| "Draft a feature page for billing: charge cards once a month" | A new Unreviewed feature page is drafted and mapped, with a list of what is left to write. |
| "I've reviewed the Delivery page" | The page is marked Reviewed with today's date, and its Problem, Requirements, Non-goals and Success metrics lock. |
| "Publish the wiki" | Pages are copied to the GitHub wiki; it refuses while a page still has problems. |
| "Undo the last publish" | The last publish is reverted, unless the wiki changed since. |
| "Keep the repo's copy of a PRD in step with Notion" | Syncing is opt-in per PRD. The owner sets that page's PRD source, the third column of its `.loop/docs.tsv` row, to `url:<link>` or `mcp:<server>:<resource>`; the sync then adopts it into the repo's copy, and after that either side can change a requirement. A page with no source stays in the repo and raises no signal. |
| "Has the Notion PRD changed?" | A dry run lists each difference as a DELTA with the page, the id, which side changed and both texts, writes nothing, and says not connected when no connector is set. |
| "Use the Notion text for TH-2" | The sync writes only that requirement into the repo's copy and closes the delta's issue; saying "Keep the repo's text for TH-2" instead writes the repo's text to Notion through the connector. Every other requirement is left as it was. |
| "What is out of step?" | Health and the check-in list each open delta, with its issue, as an inconsistency until one side's text is accepted. |

Each requirement and how it is delivered:

- DOC-1: PRD template. Example, from the stale-found test: given a wiki page behind the code it covers, when the docs check runs, then the page is reported as stale.
- DOC-2: The PRD is mine. Example, from the review-dated test: given a criterion, when it is reviewed, then it is marked Reviewed with the date.
- DOC-3: Tests follow on their own. Example, from the untested-listed test: given a Reviewed criterion with no test or a test that no longer matches, when the check runs, then it is listed.
- DOC-4: Home is one table. Example, from the format-home test: given a Home page with a line outside its Features table, when the docs check runs, then it fails naming Home, Features and DOC-4.
- DOC-5: The front door is natural language. Example, from the format-frontdoor test: given a README How to use table with a command in You say, when the docs check runs, then it fails naming README, the section and DOC-5.
- DOC-6: Each skill's commands are documented in its command reference. Example, from the command-reference-complete test: given each skill's SKILL.md Command map, when the reference is read, then every verb in the map has its syntax in the skill's SKILL.md or references/commands.md.
- DOC-7: Requirements are bullets. Example, from the format-bullets test: given a requirement with no sub-bullet, when the docs check runs, then it fails naming the page, Requirements and DOC-7.
- DOC-8: Problem is the user's problem. Example, from the format-problem test: given a Problem that names code internals, when the docs check runs, then it fails naming the page, Problem and DOC-8.
- DOC-9: Tests are a table. Example, from the format-tests-table test: given a hand-edited Tests table, when the docs check runs, then it fails naming the page, Tests and DOC-9.
- DOC-10: One Tests page, every release noted, a backlog milestone per feature. Example, from the milestones-once test: given a free-form milestone title such as v1.0, when new runs twice, then one milestone is made and the second run says it exists.
- DOC-14: A feature page lists what it ships: the pages people open and the deliveries people receive. Example, from the deploy-section-optional test: given a feature page with no Deployments section, a good Page table, a good Delivery table or both, when the docs check runs, then it passes, and a Deployments section before Success metrics is refused as out of order.
- DOC-16: A feature page carries a runbook for each routine it owns. Example, from the runbook-good test: given a feature page with a well-formed Runbook section after its Problem, when the docs check runs, then it passes, and a Runbook placed before Problem is refused as out of order.
- DOC-15: Home and the README show how the repo is set up and what runs by itself. Example, from the settings-overridden test: given a toy repo with one overridden setting, when render runs, then Home's Settings table marks exactly that one overridden with its value.
- DOC-17: A PRD kept outside the repo stays in step through reviewed deltas. Example, from the sync-not-connected test: given an mcp source and no connector, when docs.py sync runs, then it prints not connected, writes nothing and exits 0.
- DOC-18: Every feature page has a How-to-use page for its users. Example, from the doc18-howto-missing test: given a feature page with no How-to-use page, when docs check runs, then it reports the feature, and a feature with a How-to-use page on the skeleton passes.
- DOC-19: Each How-to-use page has one item per functional requirement, saying how it is delivered. Example, from the doc19-item-missing test: given a feature page with three functional requirements and a How-to-use page with items for two, when docs check runs, then it fails naming the missing ID, and with all three items it passes.

### Skill: workflow-docs
- **Say:** "Check the docs"
- **Command:** `/workflow-docs check`

### Command: docs.py
- **Command:** `python3 skills/workflow-docs/scripts/docs.py check [--base REF] [--own]` (also `docs.py audit`, `docs.py automation`, `docs.py criteria PAGE`, `docs.py publish`)
- **Dry run:** `docs.py audit --dry-run` and `docs.py publish --dry-run` say what they would do; `check` writes nothing.
- **Reads:** `.loop/docs.tsv`, `.loop/config.json`, `docs/wiki/` and the git history of the paths each page describes.
- **Writes:** `audit` fixes the mechanical trouble (Tests tables, generated blocks); `publish` copies the pages to the GitHub wiki.
- **Exit codes:** 0 only when nothing is left; 1 when any problem line is printed.

### Command: audit.py restamp
- **Command:** `python3 skills/workflow-docs/scripts/audit.py restamp SLUG PAGE...`
- **Dry run:** none: it prints one `RESTAMPED PAGE` line per page it changes, and nothing when no page qualifies.
- **Reads:** the named pages and the git state of their files.
- **Writes:** the named pages: their Review stamp, or a kept marker at the end of a How-to-use page.
- **Exit codes:** 0, whether or not a page qualified.

### API/file contract: .loop/docs.tsv
- **Path:** `.loop/docs.tsv`
- **Fields:** page name, a tab, the paths it describes (comma separated), and an optional third column with the page's PRD source (`url:` or `mcp:`).
- **Example:** `Delivery`, a tab, then `skills/workflow-delivery`.
- **Writer:** `docs.py add`, or the owner by hand.
- **Reader:** `docs.py check`, `audit` and `publish`, and health.

## URLs and deployments

- Wiki: [Documentation](https://github.com/jcl2018/agent-workflow-template/wiki/Documentation)
- Milestone: [Documentation](https://github.com/jcl2018/agent-workflow-template/milestone/3)
- Releases: https://github.com/jcl2018/agent-workflow-template/releases

## Links

- PRD page: [Documentation](Documentation)
- Backlog: [Backlog: Documentation](https://github.com/jcl2018/agent-workflow-template/milestones)

<!-- kept doc4-doc18-conflict@06ce732b -->
<!-- kept full-auto-all@08ab9232 -->
