# email-notify: plan

## Claims checked against the code

- `skills/workflow-health/scripts/mail.py` has `settings(root)`, `secrets(mode, test)`, `deliver(mode, keys, subject,
  text, page, opts)`, `scrub(text)` and `Stop`. Its top level only imports and sets environment variables, so it is safe
  to import. `secrets` reads `os.environ`, so notify.py loads mail.env into its own process environment before calling it.
- `skills/workflow-health/scripts/rounds.py` has `mail_path(home)` (`LOOP_MAIL_ENV` or `<home>/mail.env`),
  `mail_mode(path)` and `to_html(text)`. The schedule home is `LOOP_SCHEDULE_HOME` or `~/.workflow-loop/schedule`
  (`workflows.home`). It is copied as a one-line expression, because importing workflows.py is not needed.
- `workflows.MAIL_SECRETS` names the six variables a mail.env may hold. notify.py takes only those.
- `skills/workflow-monitoring/scripts/operate.py` `one_pass` prints the check-in with
  `print(graph.localize(script("checkin.py", cwd=top)[1].rstrip()))` and has `folder = <common>/loop` in scope.
- `live_board.load(root)` gives the run records. `auto.eta_seen` and `auto.eta_left` (0 once passed) give the hard ETA.
  A merged and released run has `status: done` and `release_version`.
- `skills/workflow-setup/scripts/settings.py` TABLE holds PRIVATE rows, and `reference()` writes them to
  `skills/workflow-setup/references/settings.md`. `resolve()` shows a private key's local value. The file is 19,272
  bytes, so it must be trimmed.
- MON-5 on `docs/wiki/Monitoring.md` is Reviewed (sealed). `criteria.py unreview MON-5 --user --owner-record ID` lifts
  the seal, and `review` reseals it.

## Build steps

1. **notify.py** (new, `skills/workflow-monitoring/scripts/notify.py`, at most about 7 KB):
   `notify.py send [--checkin FILE] [--root DIR]` and `notify.py status`.
   - Reads `notify_email` from the flow file (`LOOP_FLOW` or `~/.workflow-loop/flow.json`). If it is not `true`, it
     exits 0 and prints nothing.
   - Collects events: Needs-you items parsed from the check-in text (numbered lines between `Needs you` and
     `Coming up`); stopped or failed runs; runs past their hard ETA; runs done with `release_version`. A run owned by
     another pod is skipped (`graph.foreign`).
   - State: `<common>/loop/notified.json` maps each key to `mailing`/`mailed`. With no file, it writes a baseline of the
     current keys and prints `NOTIFY: baseline N events, nothing sent`.
   - mail.env: missing → `NOTIFY: not set up (MAIL_NOT_SET_UP)`; wrong mode → `MAIL_ENV_MODE`. In both cases it sends
     nothing and records nothing, so the events go out once it is set up. (The baseline still applies: the first
     run that can send skips the old events.)
   - Each new event: mark it `mailing`, `deliver`, then `mailed`; a refused send drops the key. Each send prints
     `NOTIFY: sent <kind> <slug>`, scrubbed through `mail.scrub`.
2. **operate.py**: in `one_pass`, keep the check-in text, print it, write it to `<folder>/checkin.txt`, run
   `notify.py send` and print any output. It must stay at or under 19,000 bytes.
3. **settings.py**: add `("notify_email", PRIVATE, False, "Flow file: true mails you each new check-in event (Needs
   you, a stopped or past-ETA goal, a release) through mail.py, with mail.env's address; per machine.")`. Trim it to
   19,000 bytes or less by shortening the docstrings and comments, without changing behavior. Then regenerate
   `references/settings.md` with `settings.py reference --write`.
4. **Monitoring page**: only with the owner's words, `criteria.py unreview MON-5 --user --owner-record <id>`, add the
   sub-bullet, then `criteria.py review MON-5 --user --owner-record <id>` once the owner approves the wording. Until then
   the page is not changed, and the goal waits under Needs you at that step.
5. **Commands reference**: add one line for `notify.py` to `skills/workflow-monitoring/references/commands.md`, so
   the command-reference check stays complete.
6. **Tests**: `dev/toy/test-email-notify.py` (header `# windows: ok`, `# reads:` notify.py mail.py operate.py
   settings.py). It uses a temp repo, a temp HOME, `LOOP_FLOW`, `LOOP_MAIL_ENV` and an in-process local Cloudflare stub
   on `DIGEST_MAIL_API`.
   - on: a check-in with one Needs-you item, a stopped run and a released run → three mails, each subject naming its
     slug and each body its action;
   - repeat: the same input → no mail;
   - off: `notify_email` false → no mail and no state file;
   - first run (no state file) → baseline, no mail;
   - the address never appears in stdout or notified.json;
   - the settings reference lists `notify_email` as private, default `false`.
   Rows in `.loop/regression.tsv` (land, MON-5): `notify-new-events`, `notify-repeat-quiet`, `notify-off-quiet`,
   `notify-baseline`, `notify-no-address`, `notify-setting-default`. Each is seen failing before the change (notify.py
   absent) with `regression.py red`.
7. **This PC**: set `notify_email: true` in `~/.workflow-loop/flow.json` (mode kept), check it with `settings.py show`
   (layer local), and leave a v1.2 milestone to-do issue for the Mac.
8. **Verify by hand** in the goal file.

## What could break

- operate.py's pass: notify.py failing must never stop the pass. It runs through `script()`, which captures the exit
  code, and its output is only printed.
- Size caps: operate.py (18,564 + about 250), settings.py (it must lose about 450 bytes) and notify.py (new, under 19,000).
- Command-reference and settings-reference checks: both are updated in steps 3 and 5.
- Package leak scan: no address or private name goes in a fixture (it uses `example.test`).

## Out of scope

- A mail for each check-in or a digest of check-ins; HTML styling beyond `rounds.to_html`.
- Writing mail.env on this PC: the address and sender key are the owner's to enter.
- The Mac's setting: a milestone to-do only.

PENDING: owner words to unreview MON-5, approve the new sub-bullet wording and review it again
PENDING: the owner writes mail.env on this PC so mail can be delivered
