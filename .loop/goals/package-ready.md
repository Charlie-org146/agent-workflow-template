# The package builds again so the release by tag can run (Operation TD372; GRD-20 and SET-10; Agensi's figures stay as they are, so the 100-file cap is never raised). release.yml run 44735383659 on the merge of 5456 failed at the package step: REFUSED 40 rule failures, no ZIP built: Size 104 files of at most 100; skills/workflow-monitoring/scripts/layers.py does not run alone; 7 commands not in listing.commands (done, handover, pending, reply, snapshot, take, turn); 31 hosts not in listing.network (nx.dev, semver.org, sre.google and others); since 5455 the tree has 105 files (the owner allowed that 105th file once, not a raised cap). This goal brings the shipped package to 100 files or fewer by merging or moving real files (never by reformatting, GRD-20), makes layers.py run alone, and declares the 7 commands in listing.commands and the hosts in listing.network exactly as the package already uses them: disclosure of what is already there, adding no new access; any host it is unsure is really used is listed in the pull request, not declared. It touches dev/package.py's listing and skill files, not regression.tsv or the wiki pages; if a trim needs a test row it builds it and pushes after rows-600-b. Lane prep and the caps guard before the push; no local lane. The release of everything merged since v1.0.112 happens on the first push to main after it lands

- Slug: package-ready
- Touches: dev/package.py, skills
- ETA: 460 active minutes (estimate 368m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given python3 dev/package.py on this branch, then it builds the ZIP with no rule failure: 100 files or fewer, every command in listing.commands, every host in listing.network, every script runs alone
2. Given the files merged or moved to reach 100, then each merge or move keeps the code it holds (no reformat-only trim), the scripts stay under their size caps, and the regression rows that cover them still pass
3. Given listing.network and listing.commands, then each added entry is one the package already uses (its file and line named in the pull request), any host not clearly used is listed instead of declared, and the docs check passes

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
