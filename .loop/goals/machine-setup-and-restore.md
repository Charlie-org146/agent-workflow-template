# machine-setup-and-restore: one command brings a new machine or account to a working operation session (#4780; owner "start these", 2026-11-17)

- Slug: machine-setup-and-restore
- Touches: not declared
- ETA: 270 active minutes (estimate 216m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a fresh clone on a new machine, when setup machine runs, then the operation session, its scheduled tasks and the peer link exist, and the output names only the owner-only items left.

## Verify by hand

1. In a scratch folder run `python3 dev/machine.py apply --home <empty folder> --repo <a clone> --peer pc`.
   Expect: lines DONE operation-session and DONE peer-link, and a final "owner steps" list naming the mail files, private names, logins, permission mode and app registration.
2. Run `python3 dev/machine.py backup <folder outside any repo> --home <that home>`, then `restore` into another empty home.
   Expect: BACKED UP and RESTORED lines; no mail.env, mail-to or private-names file in either folder.
3. Run `python3 dev/machine.py check --home <empty folder>`.
   Expect: GAP lines for operation-session and peer-link, each with a fix.
