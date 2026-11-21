Fixes #5674: every push or GitHub-write site now runs the private-name scan before it writes. Scans are only added; none is weakened, no allow-list entry is added, and no code here reads a private-name list (the scan does).

## Sites

| Site | What is scanned | Refusal | Toy case (test-scan-push-sites.py) |
| --- | --- | --- | --- |
| fit.py `pr_open` | PR title and body, plus the branch diff against the base, before `git push` and `gh pr create` | `private.refusal` text through `g.no`: "REFUSED: a private name would be pushed ... (PRIVATE_NAME)"; no push, no PR | planted name in the body, planted name in the title, clean PR still pushes and opens |
| autorelease.py `label_part` | the `release:<part>` label, before `gh label create` and `gh pr edit` | `check` fails the state with the scan's refusal; no label, no edit | a list line naming `release:major` refuses; a clean list still labels |
| merge.py `merge_pr` | the PR title and head branch (what the merge commit message is built from), read with `gh pr view` | a failed result carrying "REFUSED: ... (PRIVATE_NAME)" that the caller already turns into `release_error`; no `gh pr merge`. An unreadable PR also refuses | planted name in the title, planted name in the branch, unreadable PR, clean PR still merges |
| review.py `promote` | the state report, which carries the closed-issue titles (the release notes), before the report file, tag, branch, push and `gh release create` | exits "REFUSED: ... (PRIVATE_NAME)"; nothing changed | planted closed-issue title refuses with no tag, push, release or file; clean notes still promote |
| review.py `revert` | the revert branch name and the base name, before the push and `gh pr create` | exits "REFUSED: ... (PRIVATE_NAME)" | planted base name refuses before any push or PR; clean base still opens the PR |
| machines.py `batch_assemble` | the batch text plus the merged tree against the base (scan run in the temp worktree), before the push of `batch/<id>` | prints the refusal and returns no kept goals (every member merges alone); nothing pushed | a member commit holding the name leaves no `batch/<id>` on origin; a clean batch is pushed |
| machines.py `batch` | the draft PR title and body, before `gh pr create` | prints the refusal and "BATCH_PRIVATE: no pull request opened", exit 1 | a goal name holding the name opens no PR; clean goals open the draft |
| operate.py `apply` | the re-stamp commit against `origin/<base>`, before the push to the goal's branch | the scan's refusal is reported as the NOTE that the re-stamp could not be pushed; the branch is unchanged | a re-rendered page holding the name leaves the branch where it was; a clean re-stamp is pushed |

## Notes

- The pattern is the one the other push sites use: `autorelease.private_check` (or `private.scan` plus `private.refusal` in fit.py), run before the write.
- `operate.py` now loads autorelease through one helper, `autorelease()`, which `wiki_only` and `apply` share.
- Size: prose trims only (docstrings and comments), no code reformatted. Before and after, in bytes: fit.py 19641 to 19827, autorelease.py 18983 to 18993, merge.py 18990 to 18985, review.py 18988 to 18973, machines.py 18927 to 18978, operate.py 20455 to 20476.
- Regression row `defect-5674-scan-every-push-site` runs `test-scan-sites.sh` and the new toy; seen red with a break that removes the merge scan call.
