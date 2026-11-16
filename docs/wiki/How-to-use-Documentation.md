<!-- workflow-docs -->
# How to use Documentation

## What it's for

Keeps the wiki and README in one enforced format (feature pages are PRDs with no Usage section;.

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
| "Keep the repo's copy of the Thermis PRD in step with Notion" | Syncing is opt-in per PRD. The owner sets that page's PRD source, the third column of its `.loop/docs.tsv` row, to `url:<link>` or `mcp:<server>:<resource>`; the sync then adopts it into the repo's copy, and after that either side can change a requirement. A page with no source stays in the repo and raises no signal. |
| "Has the Notion PRD changed?" | A dry run lists each difference as a DELTA with the page, the id, which side changed and both texts, writes nothing, and says not connected when no connector is set. |
| "Use the Notion text for TH-2" | The sync writes only that requirement into the repo's copy and closes the delta's issue; saying "Keep the repo's text for TH-2" instead writes the repo's text to Notion through the connector. Every other requirement is left as it was. |
| "What is out of step?" | Health and the check-in list each open delta, with its issue, as an inconsistency until one side's text is accepted. |

## URLs and deployments

- Wiki: [Documentation](https://github.com/jcl2018/agent-workflow-template/wiki/Documentation)
- Milestone: [Documentation](https://github.com/jcl2018/agent-workflow-template/milestone/3)
- Releases: https://github.com/jcl2018/agent-workflow-template/releases

## Links

- PRD page: [Documentation](Documentation)
- Backlog: [Backlog: Documentation](https://github.com/jcl2018/agent-workflow-template/milestones)

<!-- kept how-to-use-docs@80ac1484 -->
