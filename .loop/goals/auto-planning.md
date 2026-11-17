# The operation session plans releases itself: monitor.py plan triages the backlog into releases, sets each goal's estimate, hard ETA, token budget, machine and agent profile from past runs, settings and machine memory, cross-checks the plan on a second agent through agent-routing, and sends the owner one plan to approve (issue #4779)

- Slug: auto-planning
- Touches: skills/workflow-monitoring/scripts/monitor.py, skills/workflow-delivery/scripts/routing.py, skills/workflow-monitoring/SKILL.md, skills/workflow-monitoring/references/commands.md, docs/wiki/Monitoring.md, dev/toy, .loop/regression.tsv
- ETA: 265 active minutes (estimate 211m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a queue with goals that name no release, when monitor.py plan runs, then it prints one plan in which each such goal has a release, an estimate, a hard ETA, a token budget, a machine, an agent profile and a one-line reason, and it starts no goal and writes no run record or queue line.
2. Given a pending plan, when monitor.py plan approve runs with an owner-words record, then each queue line gains the release, machine and agent of the plan with any line edits (SLUG key=value) applied over it, and the plan is marked approved; without a record, with no pending plan, or with an unknown slug it refuses and changes nothing.
3. Given two machines with different free memory and goals of mixed size (a Windows-only goal, a Mac-lane goal, small and large goals), when the plan runs, then the Windows-only goal lands on the PC, the Mac-lane goal on the Mac, the rest on the machine with the most memory left after the goals already given to it, and small goals take the cheap agent profile and large ones the heavy one, each with its reason.
4. Given a goal that already has a run record, a pool entry, a machine field in the queue, or a place in the peer machine's plan file, when the plan runs, then that goal is left out as already started, so no goal is started twice, and the plan ends with the message to send to the other machine's operation session.
5. Given a routes config that names a second agent for the plan step, when monitor.py plan --check runs, then that agent's notes print under Cross-check; and when that agent is not installed or can't write, the check runs on Claude with one AGENT_FALLBACK line and the plan still prints.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
