# Clear known-red rows doc19-readme-links, hlt2-twelve-groups, migration-robustness and prd-repo-green (Operation TD596): each row fails on main today for a reason this goal finds and fixes at its root, in the product or in the toy, without weakening any check; each row then passes on this branch run alone twice, and its known line is removed in this goal. Refs the issues the known list names for these rows

- Slug: kr-docs
- Touches: skills, dev/toy, .loop/regression.tsv, .loop/regression-known.tsv, docs/wiki
- ETA: 255 active minutes (estimate 204m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given each of the rows doc19-readme-links, hlt2-twelve-groups, migration-robustness and prd-repo-green, then it passes on this branch run alone twice outside any sandbox, with its root cause named in the pull request body
2. Given each fix, then no assertion is weakened or skipped, any changed expectation is checked at least as strictly, and the nearest toys for every touched script pass as on main or better
3. Given this goal's diff, then the known lines for doc19-readme-links, hlt2-twelve-groups, migration-robustness and prd-repo-green are removed from .loop/regression-known.tsv, only the scripts, toys, rows and pages the fixes need change, the docs check passes and the private scan is clean

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->

## PR notes

Refs #4992 (doc19-readme-links), #5326 (hlt2-twelve-groups), #5323 (migration-robustness) and, for the row left red, the known list's note that prd-repo-green fails on clean main.

Written with the file tool under o685.

### doc19-readme-links (retired: its rule is gone; known line and row removed)
- Cause: the row's toy case (a README with a two-row How-to-use table is reported) was deleted in 1b6f34164 because DOC-5 was retired and the README rules became DOC-23, and that commit removed the row. The row came back later, in the requirements consolidation and the goal-cell repoint, with its goal cell turned into DOC-25, but the toy case never did, so the row required a PASS line `test-how-to-kinds.py` has not printed since. The toy passes (13 PASS lines, exit 0); only that line is absent.
- Why remove, not re-add a case: the behaviour is gone. DOC-25 says the README and Home have exactly the fixed sections, and `pageformat.frontdoor` reports a section after the principles ("no section after the principles"). The earlier goals known-red-w3-deploy-links and known-red-waves-batch already decided the row stays removed (known-red-waves-batch's done line 2, and its check `grep -c '^doc19-readme-links' .loop/regression.tsv`). Nothing is weakened: DOC-25 keeps its non-defect rows (format-frontdoor and the rest).
- Proof: the row no longer exists (0 matches in regression.tsv and regression-known.tsv); `render --check` and `docs.py check --own` pass.

### hlt2-twelve-groups (toy)
- Cause: the health PRD toy still described eight principles. Six principles condensed from the earlier eight (24c3c9847), so the report prints `PRINCIPLE 1` to `PRINCIPLE 6`, with References and Honesty inside principles 1 and 2 and only Attention (principle 6) unread in a toy repo; the principle names changed too. The principle map also says `AB-9 is listed but not live` for a stale row now. Six checks in part h2 failed on those expectations.
- Fix: the toy expects exactly six PRINCIPLE lines in order and none for 7 or 8, principle 6 UNREAD for its missing Attention group with References and Honesty shown inside principles 1 and 2, the six new names, and the new stale-row wording. Each check is at least as strict as before; the product is untouched.
- Proof: `regression.py run hlt2-twelve-groups` passed twice; test-health-prd.sh h2 and h6 ALL PASS.

### migration-robustness (product)
- Cause: `render.py read` opened files as strict UTF-8, so a binary `.loop/regression.tsv` (the toy writes `\xff\xfe\x00bad`) raised UnicodeDecodeError inside `sections.fresh`, and the migration check ended `INTERNAL ERROR (MIG_INTERNAL)` instead of a named gap. The second failing part, two checks at once, printed no verdict for the run that crashed and passed once the crash was gone.
- Fix: `read` treats an undecodable or unreadable file as absent, as it already did for a missing one. render.py is 18,830 bytes.
- Proof: `test-migration.sh robustness` ALL PASS (it failed on the corrupt-tsv case before: seen red); `regression.py run migration-robustness` passed three times.

### prd-repo-green (NOT cleared; known line stays)
- The row needs `tree-once.sh` to print two PASS lines; the docs-check line passes. The health line fails on three traceability FAILs that are repo state: #88 (a merged pull request named only in adopt-closing-keywords' Verify-by-hand example), and #5635 and #5638 (closed with no defect row).
- They are exactly what v2fix-bundle-2 fixes (the #88 row relinked as issues/88, plus defect rows for #5635 and #5638), and its branch shows no traceability FAIL. So this goal adds no rows for them and leaves the row's known line in place. The row clears once v2fix-bundle-2 is on main; this goal then merges main and re-runs the row before its PR.

### Rows
Net rows: -1 (694 to 693): doc19-readme-links is removed; nothing was added.

### Nearest toys
The 15 toys that name render.py pass or fail exactly as on main (same FAIL lines): test-home-stale.sh, test-docs-format.sh, test-docs-issues.sh, test-settings-table.sh, test-apply-rerender.py and test-defects-a.py fail the same way on main; the other nine pass. test-health-prd.sh h2 and h6, test-migration.sh robustness and lag-line, and test-how-to-kinds.py pass.
