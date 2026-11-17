# Design: machine-email-phone

Goal: v2.0 machine-coordination (#4787), email-first (#4785) and phone-first (#4805) in one pull request (owner record o20).
Status: APPROVED (unattended, recommended answers; the owner reviews at the pull request).

## Premises
1. The pieces already exist in part: pods and `foreign` goals (MON-15), a per-repo `merge.lock`, a pr queue (`graph.pr_queue`), a session-start fallback to a background process (MON-2), email-notify (`notify.py`) and owner-words records (`sessions.py owner-words`). This goal extends them; it adds no second system.
2. Machines share only git (the remote) and the owner's mail. So anything crossing machines travels as a git ref or a mail, never a shared folder.
3. Size is the binding constraint: the package holds 97 files (cap 100) and graph.py, pool.py, sessions.py and goal.py sit within about 100 bytes of the 19000-byte cap. New logic goes in notify.py (9.9 KB) and one new script, `machines.py`; the hooks into capped scripts must shrink them or stay under 50 bytes.
4. A peer's message or a mail reply is never the owner's approval for a safety-class step; the reply parser accepts only numbered options of a mail this loop sent, and risky classes keep needing typed words.

## Approaches
A. Minimal: three small commands, no shared ref (snapshot printed text, handover by copying a file). Cheap, but nothing crosses machines without the owner carrying files, so "nothing runs twice" cannot hold.
B. (recommended) Git refs as the shared channel. `machines.py` stores a handover bundle and the merge turn as refs under `refs/loop/` on the repo's remote, with compare-and-swap pushes; `notify.py` grows numbered-option mails and a reply reader; `sessions.assign` goes straight to the background worker once the app has refused a start; a desk checklist command lists and runs every desk-only step. Medium effort, low risk, reuses all of the above.
C. Ideal: a small coordination service. Rejected: new always-on infrastructure, and the owner has none.

## Design (B)
### machine-coordination (#4787)
- `machines.py snapshot`: one JSON object per machine: machine name, pod, each goal (slug, status, step, pr, owner machine, moved_to), free slots, the pr turn it holds. `machines.py lines`: reads this machine's snapshot and any peer snapshots (a peer's snapshot arrives as `SNAPSHOT {json}` text or from `refs/loop/snapshot/<machine>`) and returns one Machine line per machine; checkin.py draws both lines from it, so a goal shows once, under its owning machine.
- `machines.py handover SLUG --to MACHINE`: refuses a goal that is not this machine's, a worker that is still running, or a goal at pr. It pushes `loop/<slug>`, writes the goal record, goal file and owner words as one bundle blob under `refs/loop/handover/<slug>` and pushes that ref, then marks the local run `moved` (`moved_to`, no worker, no session) so no worker starts here again. `machines.py accept SLUG` (the other machine) fetches the ref, writes the run record as its own, and binds a worker (`sessions.assign` path). A second accept of the same bundle is refused (nothing runs twice).
- One merge order per repo: `graph.pr_queue` delegates to `machines.pr_queue`, which keeps the local queue and adds a cross-machine turn, `refs/loop/pr-turn`, taken with `git push --force-with-lease`; `turn` returns the holder's slug while another machine holds it, `free` releases it. Stale turns expire after `LOOP_MERGE_LOCK_SECONDS`. No remote means local order only.
### email-first (#4785)
- `notify.py` events gain a numbered-options body (`1. <recommended> (recommended)`, `2. ...`) and a stable mail id (`Re: [loop <id>]` token in the subject). Both machines send through the one mailer and one send budget: the budget file is `refs/loop/mail-budget` (a counter blob per day, `mail_budget` setting, default 20) and a machine over the budget sends nothing and says so.
- `notify.py reply TEXT --id ID`: maps "1", "1 recommended", "approve" to the option, records it with `sessions.py owner-words --source owner`, and prints the action. Safety-class options (destructive, money, security, private data; the existing `auto.CLASSES`) are refused with "needs your own typed words" unless the reply text itself contains the option's required words. Mail is read by the operation session's own mail tool, never by these scripts.
- A merged release produces one mail already (event `released`); it now carries the options of any open question in the same mail.
### phone-first (#4805)
- `sessions.assign`: when the session tool fails, hangs or reports a refusal, the goal starts a background worker through `agent_command` (the default), and the refusal is remembered for `LOOP_SESSION_REFUSED_MINUTES` (30) so the next goals skip the doomed start. No setting is needed to get this.
- `dev/desk.py` (outside the package): lists every desk-only setup step once (trust worktree and project folders, permission mode, tool pre-approvals, private-name list, mail.env, Codex login), runs the ones that can be run, and ends with a phone-only start check; the report says what is left at the desk.

## Tests (fake mailer, toy repos, no real mail, no secrets)
Handover moves a goal and the old machine shows it moved with no worker; a second accept is refused; two machines contend for the pr turn; snapshot lines show a goal once; a needs-you item and a release produce one mail with numbered options through a fake mailer and one budget; "1 recommended" is recorded with --source owner and a money option is refused; a refused session start goes to the background and is remembered; desk.py lists every step.

## Verify by hand
Handover on a toy repo; read a mail body from the fake mailer; run `desk.py plan`.

PENDING: none (every choice took the recommended answer).
