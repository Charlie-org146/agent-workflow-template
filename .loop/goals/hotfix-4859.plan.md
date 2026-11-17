# hotfix-4859 plan

Claims checked against the code: `skills/workflow-setup/scripts/settings.py` `fill_private` writes `~/.workflow-loop/repos`; `dev/toy/reap.sh` redirects LOOP_FLOW and LOOP_HEALTH only and snapshots the real folder with `dev/toy/homeguard.py`; `dev/toy/test-defect.sh` called `setup.py` with the real HOME. All exist as described.

## Build steps
1. In `dev/toy/test-defect.sh`, after reap.sh is sourced: `real_home=$HOME; export HOME=$(mktemp -d); export USERPROFILE="$HOME"; toy_on_exit 'rm -rf "$HOME"'`. (Done.)
2. Add case `home-sandbox` (HOME differs from the real one; setup wrote `repos` under the sandbox) and list it in `cases`. (Done.)
3. Add defect row `home-sandbox-4859` (land, category defect, linked to #4859) and see it red with `regression.py red --break`. (Done.)
4. Run the six rows. The toy skips on native Windows, so the Windows run uses a `uname` shim that says Linux; CI is the authority.

## Tests per done line
1. HOME line: row `home-sandbox-4859`, seen red against the old toy, green now.
2. The three rows pass on CI; the old toy against a non-temp HOME gave `LEAK: ... added repos`, the new one gave none.
3. The three other rows are named in the PR body; none is in `regression-known.tsv`.

## What could break
A case that needed the real HOME (git identity, gh login). The toy uses fakegh and its own git config, and the shimmed run of the cases showed no new failure.

## Out of scope
Fixing judge-key-old (file.py:108), doc19-item-missing and link-unread-never-pass: a different cause each, to be named in the PR for their own hotfix goals.
