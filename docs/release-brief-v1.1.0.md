v1.1.0 Frozen 2026-11-21 10:52

## v1.1.0 brief (minor, re-frozen 2026-11-21 10:52)

Replaces the 23:58 brief · your words: "I want the 1.1 to only handle these three ... so that at the end of 1.1 we can know how to we can spawn multiple tasks and show the progress"

- **What it's about** (your words): only the goal loop, tasks and releases, plus the documentation part, so that at the end of v1.1.0 you can spawn several tasks and see their progress.
- **Tasks, in order:**
  1. **The three features' text**: DEL-19 (revised), DEL-23 (new) and DOC-28 (revised) written into the docs exactly as on this page, with your review marks. DOC-27 is already on main.
  2. **Today's work as tasks**: every piece of work now in flight (the template feature migration, the #5727 fix, the file-limit change, the implementation, and v1.2.0's tasks) gets a task brief in the DEL-23 format, and the board shows the task list by name with each task's goals and progress.
  3. **The template feature migration** (already built and tested; finished under its frozen done lines).
  4. **The implementation**: the docs check enforces DOC-27 and the DEL-19 goal format; the release tool enforces the revised DOC-28 (the brief lists tasks, and a feature task merges only once a brief names it); the task list and briefs enforce DEL-23. Every test case passes, and no existing test turns red.
- **Patches alongside** (bug fixes, no brief needed): the #5727 smoke-test fix and the file limit raised to 200 (o718, o719).
- **Not in it:** the service repo feature migration (the service repo #1240 stays in draft with its hold, for a later brief); scheduling; the page rebuild; v1.2.0's three features (that brief stays frozen and runs after v1.1.0).
- **Done when:** every DOC-27, DEL-19, DEL-23 and DOC-28 test case passes; the board shows every task by name with its goals and progress; at least two tasks have run side by side in the new format; v1.1.0 is tagged through the minor path.
