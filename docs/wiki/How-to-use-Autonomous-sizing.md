<!-- workflow-docs -->
# How to use Autonomous sizing

## What it's for

Autonomous sizing: the loop sizes each goal and picks its checks itself. It is written, not built: goal v110-cbs-asz builds it. Reviewed approves the wording; availability is shown separately. This page says what is true today and goes when the feature is built.

### What's delivered

| Component | Kind | What it is | How a user uses it |
|---|---|---|---|
| `workflow-delivery` | Skill | The skill that will carry ASZ-1; not built yet (goal v110-cbs-asz). | Nothing to run yet: ASZ-1 is written, not built. |

### System diagram

```text
[Skill: workflow-delivery | the agent session] --ASZ-1: planned, not built yet--> (the owner)

Legend: a box is Kind, Component and where it runs; --text--> a flow of data or control; (text) a part outside the table.
```

## How to reach or run it

Nothing is built yet, so there is nothing to say or run. Goal v110-cbs-asz builds ASZ-1; until it merges, this page and the feature page [Autonomous-sizing](Autonomous-sizing) hold the whole description.

Each requirement and how it is delivered:

- ASZ-1: Autonomous sizing: the loop sizes each goal and picks its checks itself. Written, not built; goal v110-cbs-asz builds it.

### Skill: workflow-delivery
- **Say:** none
- **Command:** `/workflow-delivery step SLUG STEP`

## URLs and deployments

- Wiki: [Autonomous-sizing](https://github.com/jcl2018/agent-workflow-template/wiki/Autonomous-sizing)
- Releases: https://github.com/jcl2018/agent-workflow-template/releases

## Links

- PRD page: [Autonomous-sizing](Autonomous-sizing)
- Backlog: [Backlog](https://github.com/jcl2018/agent-workflow-template/milestones)
