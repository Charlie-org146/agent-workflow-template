<!-- workflow-docs -->
# How to use Deliver first

## What it's for

Deliver first: a goal goes from plan to merge without waiting for the owner, unless it is a safety class. It is written, not built: goal v110-dlf-1 builds it. Reviewed approves the wording; availability is shown separately. This page says what is true today and goes when the feature is built.

### What's delivered

| Component | Kind | What it is | How a user uses it |
|---|---|---|---|
| `workflow-delivery` | Skill | The skill that will carry DLF-1; not built yet (goal v110-dlf-1). | Nothing to run yet: DLF-1 is written, not built. |

### System diagram

```text
[Skill: workflow-delivery | the agent session] --DLF-1: planned, not built yet--> (the owner)

Legend: a box is Kind, Component and where it runs; --text--> a flow of data or control; (text) a part outside the table.
```

## How to reach or run it

Nothing is built yet, so there is nothing to say or run. Goal v110-dlf-1 builds DLF-1; until it merges, this page and the feature page [Deliver-first](Deliver-first) hold the whole description.

Each requirement and how it is delivered:

- DLF-1: Deliver first: a goal waits for me once, at its start. Written, not built; goal v110-dlf-1 builds it.

### Skill: workflow-delivery
- **Say:** none
- **Command:** `/workflow-delivery step SLUG STEP`

## URLs and deployments

- Wiki: [Deliver-first](https://github.com/jcl2018/agent-workflow-template/wiki/Deliver-first)
- Releases: https://github.com/jcl2018/agent-workflow-template/releases

## Links

- PRD page: [Deliver-first](Deliver-first)
- Backlog: [Backlog](https://github.com/jcl2018/agent-workflow-template/milestones)
