<!-- workflow-docs -->
# How to use Checks by size

## What it's for

Checks by goal size: one table says which checks each size of goal runs. It is written, not built: goal v110-cbs-asz builds it. Reviewed approves the wording; availability is shown separately. This page says what is true today and goes when the feature is built.

### What's delivered

| Component | Kind | What it is | How a user uses it |
|---|---|---|---|
| `workflow-delivery` | Skill | The skill that will carry CBS-1; not built yet (goal v110-cbs-asz). | Nothing to run yet: CBS-1 is written, not built. |

### System diagram

```text
[Skill: workflow-delivery | the agent session] --CBS-1: planned, not built yet--> (the owner)

Legend: a box is Kind, Component and where it runs; --text--> a flow of data or control; (text) a part outside the table.
```

## How to reach or run it

Nothing is built yet, so there is nothing to say or run. Goal v110-cbs-asz builds CBS-1; until it merges, this page and the feature page [Checks-by-size](Checks-by-size) hold the whole description.

Each requirement and how it is delivered:

- CBS-1: Checks by goal size: one table says which checks each size runs. Written, not built; goal v110-cbs-asz builds it.

### Skill: workflow-delivery
- **Say:** none
- **Command:** `/workflow-delivery step SLUG STEP`

## URLs and deployments

- Wiki: [Checks-by-size](https://github.com/jcl2018/agent-workflow-template/wiki/Checks-by-size)
- Releases: https://github.com/jcl2018/agent-workflow-template/releases

## Links

- PRD page: [Checks-by-size](Checks-by-size)
- Backlog: [Backlog](https://github.com/jcl2018/agent-workflow-template/milestones)
