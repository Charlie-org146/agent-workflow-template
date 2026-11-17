# email-notify: design

## Problem

The owner has to watch the operation session's Claude Code window to learn that something needs them or that a goal
landed. They asked (o77) for an email instead: one when a check-in shows a new Needs-you item, a goal that stopped or
passed its ETA, or a goal merged and released. It is off by default, set per machine, and sent through the health
round's mailer, and the address never reaches a tracked file, log or issue.

## Approaches

1. **Inside checkin.py.** The check-in already knows every event. Cost: checkin.py is at 18,974 of the 19,000-byte
   cap, and the check-in is documented as read-only; sending mail from it breaks that and every caller (the reply hook,
   `expected()`) would risk a send. Risk: high.
2. **A new `notify.py` that operate.py calls once per pass, after it prints the check-in (chosen).** operate.py saves
   the check-in text it just printed to `<git common dir>/loop/checkin.txt` and runs `notify.py send`. notify.py reads
   the Needs-you items from that text and the run records for stopped, past-ETA and released goals. It sends each new
   event through mail.py's own `settings`, `secrets` and `deliver`, with the variables from `mail.env`, the schedule's
   address file outside the repo (`rounds.mail_path`). Cost: one new script of about 6 KB and about 250 bytes in
   operate.py (18,564 now). Risk: low. The check-in stays read-only, and with notification off, notify.py returns
   before it reads anything.

## Choice

Approach 2. It keeps the mailer in one place (mail.py: one sender, one scrub, one retry rule), keeps checkin.py
read-only and under its cap, and can be tested on its own with a local SMTP server (mail.py already supports
`DIGEST_SMTP_TEST_PORT` with `smtp_host` localhost).

### Events and their keys

The sent keys are kept in `<git common dir>/loop/notified.json`, which is machine-local and untracked.

| Event | Source | Key | Mail names |
|---|---|---|---|
| Needs you | each numbered item under `Needs you` in checkin.txt | `needs:` + the item with digits made `#` | the goal (first slug in the item) and the item, which holds the action |
| Stopped | run status `stopped` or `failed` | `stopped:<slug>:<attempt>` | the goal, its finding and "resume it or retire it" |
| Past ETA | `auto.eta_left(eta_seen) == 0` | `eta:<slug>:<eta minutes>` | the goal and "pick ship now, extend once or defer" |
| Released | status `done` with `release_version` | `released:<slug>:<version>` | the goal, its PR and the version; "nothing to do" |

- A repeat sends nothing because its key is already in the file. Digits become `#` so that "silent for 31m" and
  "silent for 61m" are one event.
- First run on a machine (no file yet): every current key is recorded as a baseline and nothing is sent, so turning it on
  does not mail some 150 old releases. It prints `NOTIFY: baseline N events`.
- A key is written as `mailing` before the send and `mailed` after it. A refused send removes the key (the next pass
  retries). An unknown outcome keeps it, so nothing is mailed twice, as in mail.py.
- One mail per event. The subject is `Loop: <kind> <slug> (<repo>)`, and the body is the action line, with no address in
  it.

### Setting

`notify_email` is a **private** setting in `~/.workflow-loop/flow.json` (per machine; `.loop/config.json` is shared by
both machines), default `false`. It is a TABLE row in settings.py, so it appears in the Private settings part of
`references/settings.md` and in `settings.py show`. settings.py is at 19,272 bytes, already over the 19,000 cap, so
the build trims it to 19,000 or less with the new row.

Off (or no flow file): `notify.py send` prints nothing and sends nothing. On, with no `mail.env`: it prints
`NOTIFY: not set up (MAIL_NOT_SET_UP)` once per pass and sends nothing.

### Address

The address and keys are read from `mail.env` only, then passed to mail.py's functions in memory. Every printed line
goes through `mail.scrub`, and notified.json holds only keys (slugs, step text, versions), never an address.

## What each done line needs

1. A toy test (`dev/toy/test-email-notify.py`) builds a temp repo with a check-in holding a Needs-you item, a stopped
   run record and a released run record, plus a local SMTP server. It shows that notification on gives three mails,
   each naming its goal and action; a second run gives none; and notification off gives none. Each gets a regression
   row under MON-5.
2. A MON-5 sub-bullet on docs/wiki/Monitoring.md, the `notify_email` row in settings.py and references/settings.md (off
   by default), and a test row for the default. MON-5 is Reviewed, so changing its sub-bullets needs `criteria.py
   unreview MON-5` with the owner's words. The wording goes to the owner through operation-pc, and MON-5 is reviewed
   again only with their words.
3. `notify_email: true` in this PC's `~/.workflow-loop/flow.json` (outside the repo), shown by `settings.py show` as
   local. A milestone to-do on v1.2 for the Mac: "set notify_email true in the Mac's flow.json".

## Open questions

- PENDING: owner words to unreview MON-5, approve the new sub-bullet's wording and review it again (o77 covers
  email-notify, not MON-5).
- This PC has no `mail.env`, so mail cannot go out until the owner writes one (the address and a sender key are theirs to
  enter). It is listed as an owner to-do, not something the goal can do.
