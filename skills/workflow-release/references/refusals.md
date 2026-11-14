# workflow-release refusals

Each refusal says `REFUSED:` and a fix. Common ones:

| Refusal | Fix |
|---|---|
| Checks have not passed | Finish the goal with `workflow-delivery` |
| No complete steps under `## Verify by hand` | Give every numbered step an `Expect:` line, and commit it |
| Pages are stale | Update them with `workflow-docs`, commit, and run the release again |
| A batch goal, no `--user` | Wait for the human's own `cut <slug>` |
| On the wrong branch | Switch to `loop/<slug>` in the goal's worktree |
| Uncommitted changes | Commit or set them aside |
| Tag already exists | Ask the user which version to use |

`release.py show <slug>` prints the `release` field, and the version and draft URL after a cut.
