<!-- workflow-docs -->
# How to use Cheap checks

## What it's for

Cheap checks: the cheapest form that does the job, and checks that find nothing are flagged. It is written, not built: goal v110-chp-1 builds it. Reviewed approves the wording; availability is shown separately. This page says what is true today and goes when the feature is built.

### What's delivered

| Component | Kind | What it is | How a user uses it |
|---|---|---|---|
| `workflow-monitoring` | Skill | The skill that will carry CHP-1; not built yet (goal v110-chp-1). | Nothing to run yet: CHP-1 is written, not built. |

### System diagram

```text
[Skill: workflow-monitoring | the operation session] --CHP-1: planned, not built yet--> (the owner)

Legend: a box is Kind, Component and where it runs; --text--> a flow of data or control; (text) a part outside the table.
```

## How to reach or run it

Nothing is built yet, so there is nothing to say or run. Goal v110-chp-1 builds CHP-1; until it merges, this page and the feature page [Cheap-checks](Cheap-checks) hold the whole description.

Each requirement and how it is delivered:

- CHP-1: Cheap checks: the cheapest form that does the job, and retire checks that find nothing. Written, not built; goal v110-chp-1 builds it.

### Skill: workflow-monitoring
- **Say:** none
- **Command:** `/workflow-monitoring operate`

## URLs and deployments

- Wiki: [Cheap-checks](https://github.com/jcl2018/agent-workflow-template/wiki/Cheap-checks)
- Releases: https://github.com/jcl2018/agent-workflow-template/releases

## Links

- PRD page: [Cheap-checks](Cheap-checks)
- Backlog: [Backlog](https://github.com/jcl2018/agent-workflow-template/milestones)
