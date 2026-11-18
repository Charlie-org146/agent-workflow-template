# dev/package.py passes on main again: the package is back within its 100-file limit and every shipped command is disclosed in listing.json, so sync-propose (#4967) goes green

- Slug: package-size-listing
- Touches: not declared
- ETA: 290 active minutes (estimate 232m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. listing.json discloses the commands done, handover, pending, reply, snapshot, take and turn exactly as they exist, with no behaviour change
2. The package holds 100 files or fewer by cutting files, never by raising the 100-file cap; the PR names each file cut and why; if no sensible cut exists, the goal stops and reports so the cap question goes to the owner
3. After merging the latest main (three-level-ops and the regroups merge first), dev/package.py passes, test-sync-update.sh propose (sync-propose) passes, and #4967 closes with that run as evidence

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
1. Run `python3 dev/package.py`.
   Expect: it prints PASS with the file count (103 now) and no FAIL line.
2. Run `python3 -c "import json;print(len(json.load(open('listing.json'))['commands']))"` and compare with the seven new names.
   Expect: done, handover, pending, reply, snapshot, take and turn are all in listing.json's commands.
3. Run `bash dev/toy/test-sync-update.sh propose`.
   Expect: it exits 0 (the sync-propose row).
