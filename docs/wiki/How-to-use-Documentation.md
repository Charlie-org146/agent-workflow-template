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

Keep the wiki in step with the code. Pages live in `docs/wiki/`, so they're reviewed in pull requests:

```text
/workflow-docs check
/workflow-docs publish
/workflow-docs restore
```

To write the first pages, ask the agent to set up the docs: it follows the skill's `init` steps (survey, choose pages, write them).

`publish` only adds or updates pages it wrote, unless you name one with `--adopt`, and never deletes one. `restore`
undoes the last publish.

With `"criteria": true` in the config, `check` also holds the wiki to a contract: Home is free-form and each feature page
is a short PRD: Problem, up to 6 requirements (`criteria_max`) marked Unreviewed or Reviewed with a
date, Non-goals, Success metrics, and Tests: each requirement's regression rows as Given/When/Then scenarios with their
last result. Only the owner reviews a PRD (`/workflow-docs review PAGE`); after that Problem, Requirements, Non-goals and
Success metrics are locked until the owner un-reviews it. `/workflow-docs prd NAME "<idea>" --paths A,B` drafts a new feature's PRD.

Upgrading a repo whose pages still have Summary and Criteria:

1. Preview: `python3 prd.py convert` (in `skills/workflow-docs/scripts`) prints one line per page and writes nothing.
2. Convert: `python3 prd.py convert --write`: Summary becomes Problem, Criteria Requirements (ids and Reviewed stamps
   kept), and each page gets `Review: **Unreviewed**` and placeholder Non-goals and Success metrics.
3. Write the drafts: replace each placeholder with what the feature deliberately won't do and one to three measurable
   lines on how you know it works.
4. Rewrite each regression row's description (column 6 of `.loop/regression.tsv`) as `Given ..., when ..., then ...`.
5. Render: `python3 criteria.py render`.
6. Check: `python3 docs.py check` prints `DOCS OK`.

Rollback is reverting that commit.

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

- DOC-1: PRD template. Example, from the stale-found test: given a wiki page behind the code it covers, when the docs check runs, then the page is reported as stale; and, from the format-bullets test, a requirement with no sub-bullet fails the check naming the page and Requirements.
- DOC-2: The PRD is mine. Example, from the review-dated test: given a criterion, when it is reviewed, then it is marked Reviewed with the date. Also: `criteria.py revise DOC-4 --text "New wording" --why "the owner asked" --owner-record o30`. Also: `criteria.py retire DOC-6 --as merged:DOC-1 --why "same rule" --owner-record o30`. Also: `criteria.py migrate --page Documentation --owner-record o30`. Also: `goal.py pr`. Also: `goal.py finding GOAL "DOC-1 gap" --requirement DOC-1`. Also: `criteria.py guard`.
- DOC-24: Every requirement names what it follows (v2.0 planned). The README's principle tables show each requirement's Follows cell, its tool or standard, a link to its source and its verdict, for example adapted from GitHub CODEOWNERS for DOC-2. Example: a requirement row with an empty Follows cell fails the docs check.

### Skill: workflow-docs
- **Say:** "Check the docs"
- **Command:** `/workflow-docs check`

### Command: docs.py
- **Command:** `python3 skills/workflow-docs/scripts/docs.py check [--base REF] [--own]` (also `docs.py audit`, `docs.py automation`, `docs.py criteria PAGE`, `docs.py publish`, `docs.py sync`)
- **Dry run:** `docs.py audit --dry-run` and `docs.py publish --dry-run` say what they would do; `check` writes nothing.
- **Reads:** `.loop/docs.tsv`, `.loop/config.json`, `docs/wiki/` and the git history of the paths each page describes.
- **Writes:** `audit` fixes the mechanical trouble (Tests tables, generated blocks); `publish` copies the pages to the GitHub wiki.
- **Exit codes:** 0 only when nothing is left; 1 when any problem line is printed.

### Command: audit.py restamp
- **Command:** `python3 skills/workflow-docs/scripts/audit.py restamp SLUG PAGE...`
- **Dry run:** none: it prints one `RESTAMPED PAGE` line per page it changes, and nothing when no page qualifies.
- **Reads:** the named pages and the git state of their files.
- **Writes:** one line per named page in `.loop/kept/<slug>.tsv`, committed as `Kept: <slug>`; no page is edited.
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

<!-- kept results-render@e8ceb262e -->
