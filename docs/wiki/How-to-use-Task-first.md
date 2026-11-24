<!-- workflow-docs -->
# How to use Task first

## What it's for

Task first: the operation schedules the owner's tasks ahead of fixes to its own tools. It is written, not built: goal v110-tsk-1 builds it. Reviewed approves the wording; availability is shown separately. This page says what is true today and goes when the feature is built.

### What's delivered

| Component | Kind | What it is | How a user uses it |
|---|---|---|---|
| `workflow-monitoring` | Skill | The skill that will carry TSK-1; not built yet (goal v110-tsk-1). | Nothing to run yet: TSK-1 is written, not built. |

### System diagram

```text
[Skill: workflow-monitoring | the operation session] --TSK-1: planned, not built yet--> (the owner)

Legend: a box is Kind, Component and where it runs; --text--> a flow of data or control; (text) a part outside the table.
```

## How to reach or run it

Nothing is built yet, so there is nothing to say or run. Goal v110-tsk-1 builds TSK-1; until it merges, this page and the feature page [Task-first](Task-first) hold the whole description.

Each requirement and how it is delivered:

- TSK-1: Task first: the operation schedules my tasks ahead of fixes to its own tools. Written, not built; goal v110-tsk-1 builds it.

### Skill: workflow-monitoring
- **Say:** none
- **Command:** `/workflow-monitoring operate`

## URLs and deployments

- Wiki: [Task-first](https://github.com/jcl2018/agent-workflow-template/wiki/Task-first)
- Releases: https://github.com/jcl2018/agent-workflow-template/releases

## Links

- PRD page: [Task-first](Task-first)
- Backlog: [Backlog](https://github.com/jcl2018/agent-workflow-template/milestones)
