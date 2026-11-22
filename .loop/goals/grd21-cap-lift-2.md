# Temporarily raise the package file cap to 200 (owner o718, GRD-21): the package is published by website upload, and a later minor revises GRD-21

- Slug: grd21-cap-lift-2
- Touches: dev/package.py, dev/toy, docs/wiki, docs, .loop/regression.tsv, README.md
- ETA: 90 active minutes (the owner's budget, o762)

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

Review of this redo: the code is byte-identical to the first goal's reviewed head, and the one delta that the first goal's passes had not seen (453c5e83e..bf57f9287, 5 files) got a fresh full-depth pass here: Testing, Maintainability, Security and adversarial reviewers, 0 critical, 15 informational, none fixed (a fix would change the code and need its own full review; accepted by the operation under top's TD897). Plan and review are recorded condensed, carried over from grd21-cap-lift, with the depth set to condensed by the operation (TD895).

Three bypasses of the package-limits table check, reproduced by the adversarial pass and tracked in [#5784](https://github.com/Charlie-org146/agent-workflow-template/issues/5784): (1) the exemption regex is a closed word list, so a non-agent row reading "9 GB (obsolete limit)" or "Obsolete, waived", or "No longer applies" with a non-breaking space, passes; (2) the Skills-per-pack guard is case- and whitespace-sensitive and not required, so a differently cased label, "at most 200 files, at most 9999 files", or a deleted row passes; (3) the agent-upload row's MAX_FILES check reads only the first match, so "200 files (MAX_FILES), 9000 files (MAX_FILES)" passes. None lets a 201st file, a looser dated figure, or a "no longer applies" on another dated row through. The other informational findings: the opening-words message is built at two sites, the bare "n/a" in the regex has no word boundary, the buyer's-agent and website figures in the agent-upload row and the "202 entries" text are not tied to their own rows, "at most 200 besides SKILL.md" is loose (198 is exact with 2 SKILL.md files), docs/ROADMAP.md repeats the literal 200, one control's replace() hits the first match in the document, plan-sizes no longer pins the number independently, and the internal id o718 is in a public doc.
