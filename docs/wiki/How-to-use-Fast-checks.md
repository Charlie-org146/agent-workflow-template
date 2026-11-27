<!-- workflow-docs -->
# How to use Fast checks

## What it's for

Fast checks: skip what a later check covers, and time-limit the rest. It is written, not built: goal v110-skp-1 builds it. Reviewed approves the wording; availability is shown separately. This page says what is true today and goes when the feature is built.

### What's delivered

| Component | Kind | What it is | How a user uses it |
|---|---|---|---|
| `workflow-delivery` | Skill | The skill that will carry SKP-1; not built yet (goal v110-skp-1). | Nothing to run yet: SKP-1 is written, not built. |

### System diagram

```text
[Skill: workflow-delivery | the agent session] --SKP-1: planned, not built yet--> (the owner)

Legend: a box is Kind, Component and where it runs; --text--> a flow of data or control; (text) a part outside the table.
```

## How to reach or run it

Nothing is built yet, so there is nothing to say or run. Goal v110-skp-1 builds SKP-1; until it merges, this page and the feature page [Fast-checks](Fast-checks) hold the whole description.

Each requirement and how it is delivered:

- SKP-1: Fast checks: skip what a later check covers, and time-limit the rest. Written, not built; goal v110-skp-1 builds it.

### Skill: workflow-delivery
- **Say:** none
- **Command:** `/workflow-delivery step SLUG STEP`

## URLs and deployments

- Wiki: [Fast-checks](https://github.com/jcl2018/agent-workflow-template/wiki/Fast-checks)
- Releases: https://github.com/jcl2018/agent-workflow-template/releases

## Links

- PRD page: [Fast-checks](Fast-checks)
- Backlog: [Backlog](https://github.com/jcl2018/agent-workflow-template/milestones)

<!-- Still true at v110-main-red: the scheduled regression job's full-history checkout changes nothing on this page. -->
