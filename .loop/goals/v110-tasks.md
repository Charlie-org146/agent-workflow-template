# Capture today's work as tasks in DEL-23's format, and show the task list by name

- Slug: v110-tasks
- Touches: .loop/tasks, skills/workflow-monitoring, dev/toy, .loop/regression.tsv, docs, README.md
- ETA: 300 active minutes (estimate 239m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given the work in flight (v110-text, v110-tasks, migrate-features-2, the v1.1.0 implementation, fix-5727-smoke-env-2, grd21-cap-lift, v120-text, v120-del3, v120-del22, v120-set1, and the parked service-repo migration), then each has one task brief file under .loop/tasks/. Each brief holds: its name; the feature it serves; its purpose and done-when lines quoted from its frozen release brief (v1.1.0 o721, v1.2.0 o715; for a patch, its issue); its release; its goals; and its source record. Nothing is written beyond what those briefs say.
2. Given .loop/tasks/, then one task list is generated from the briefs and run records. It shows every task by name with its state (queued, running, waiting, done or replaced), its goals and its ETA.
3. Given a task that names another, then the list shows it waiting until that one is done. Two tasks with no dependency can both show running.
4. Given the check-in and the live board, then both show the task list by name, with each task's goals and progress. No task is shown only by a short id.
5. Given the package, then no new file is added under skills/: the release-gate check still forbids one until the implementation task lands o719's change. Docs, package and private-name checks are green, no existing row changes, and committed text never names the service repo.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
