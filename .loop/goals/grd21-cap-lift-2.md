# Temporarily raise the package file cap to 200 (owner o718, GRD-21): the package is published by website upload, and a later minor revises GRD-21

- Slug: grd21-cap-lift-2
- Touches: dev/package.py, dev/toy, docs/wiki, docs, .loop/regression.tsv, README.md
- ETA: 360 active minutes (estimate 288m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given dev/package.py, then MAX_FILES is 200, a package of 200 files passes its file check and a 201st file fails it
2. Given docs/wiki/How-to-use-Guardrails.md's package-limits table, then the agent-upload row says it no longer applies because the package is published by website upload, our figure is 200 against the buyer's agent's 200 and the website's 1,000, none of ours is looser than the limit that applies, and the change is marked temporary until a later minor revises GRD-21 (o718)
3. Given dev/toy/test-package-caps.py, dev/toy/test-package-headroom.py and the row package-caps-held, then each checks against 200 and keeps its negative control: a 201st file fails
4. Given GRD-20 and GRD-21's requirement text and review marks, then neither changes
5. Given the whole change, then the docs check, package check and private-name scan pass and no other regression row changes result

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->

## PR notes

What this changes: dev/package.py MAX_FILES goes from 100 to 200, and the package-limits table in How-to-use-Guardrails says the agent-upload file row no longer applies, because the package is published by website upload. Ours is 200 against the buyer's agent's 200 and the website's 1,000, so none of ours is looser than the limit that applies. It is a temporary change, marked as such in the table. It merges as a patch. Owner o718 (word for word): "Raise MAX_FILES to 200 for now (GRD-21): publish by website upload; revise GRD-21 in a later minor".

GRD-20 and GRD-21 requirement text and review marks are unchanged.

Negative controls, each still failing one file over the cap: the caps toy (a 201st file fails), the static toy (201 and 205 files fail with "at most 200 allowed"), the gate toy (a package of cap plus one fails), the tracked toy (loose-file controls now MAX_FILES + 10), and the table check (a looser figure, a missing or undated row, a drifted figure, and an exemption on any row but the agent-upload row all fail). Row plan-sizes now reads the cap from dev/package.py instead of a hard-coded 100. Row text of 284, 348, 435, 666 and 667 now says 200; docs/ROADMAP.md changes in its Size sentence only.

Redone as grd21-cap-lift-2 from main abe55bdf7 on the owner's word (o762: "grd21-cap-lift may be redone as grd21-cap-lift-2 from main, with the same done lines and a 90-minute budget"); the same content as the first goal's reviewed head, whose PR #5771 is closed by the operation session. The first goal's review ran three passes, the last a zero-edit pass with no findings.

Open for the owner (not decided here):
- The agent-upload pre-flight guard is lost while the row says it no longer applies (owner decision o718), and "temporary" has no expiry date: both are for the later minor that revises GRD-21.
- Not changed by order: dev/test-package.sh:19 (unwired), skills/workflow-health/references/commands.md:330, and the reasons in .loop/regression-known.tsv.
- Baseline reds on main, not caused here: package-headroom-held and package-rows-tracked (skills/workflow-health/scripts/report.py is 19,986 bytes), plus trim-package-98 and rel-major-refused in .loop/regression-known.tsv.
- Coverage: each lane ran 62 of 641 selected rows within its 15-minute budget, all passing; 578 are left to the scheduled full suite. The idea and qa steps ran condensed; autoplan's guard refused, so plan ran by hand with plan-ceo-review and plan-devex-review; the review did not converge in three passes and the last was a zero-edit pass with no findings; /verify was not run before committing.
