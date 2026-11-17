# machine-email-phone: v2.0 machine-coordination, email-first and phone-first in one goal (#4787, #4785, #4805; owner o20)

- Slug: machine-email-phone
- Touches: not declared
- ETA: 275 active minutes (estimate 219m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. machine-coordination (#4787): each goal has one owning machine and a handover command moves it (branch pushed, record copied, old machine marks it moved, new machine binds a worker) so nothing runs twice; each repo has one merge order across machines; SNAPSHOT is structured and a check-in draws both machine lines from it.
2. email-first (#4785): a new Needs-you item and a merged release each produce one mail with numbered options and a recommendation, through one mailer and one send budget for both machines; a reply like "1 recommended" is recorded as owner words with --source owner and acted on, while destructive, money, security and private-data steps still need the owner own typed words; shown with a fake mailer in tests.
3. phone-first (#4805): starting a worker never needs the desktop app (a background worker through agent_command is the default when no app session can start), and onboarding lists and runs every desk-only setup step once, up front.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->

1. Run `python3 skills/workflow-setup/scripts/setup.py desk run` from the repo.
   Expect: each desk-only step prints once with how to do it, then `desk check` prints a GAP line per open step, and DESK OK after `desk done` for each.
2. In two clones of one repo on two machines (both with `machine_sync` true in the flow file), run `python3 skills/workflow-monitoring/scripts/machines.py handover SLUG --to mac` on one, then `machines.py take SLUG` on the other.
   Expect: the first record shows `moved` with no worker; the second prints `TAKEN SLUG: worker ...`; a second `take` is refused.
3. With `notify_email` true and a fake or test mailer, run `python3 skills/workflow-monitoring/scripts/notify.py send` on a check-in with a new Needs-you item, then `mailbox.py reply QID "1 recommended"`.
   Expect: one mail with numbered options and a recommendation; the reply prints `RECORDED ... as the owner's words`.
