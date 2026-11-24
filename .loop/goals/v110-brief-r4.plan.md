# Plan v110-brief-r4

## Implementation plan

Two text files, written from the brief the owner approved (o924, the text) with the revision number the owner chose (o928). No code, no lane.

Provenance: the source copies the brief part of the draft the owner was shown on 2026-11-24 and answered yes to (ledger o924), with only the heading's revision number changed to 4 (o928). A diff of the source body against that draft must show only that one changed line.

1. `.loop/sources/frozen-source-v1.1.0-rev4.md`: first line "v1.1.0 brief (minor, revision 4), as the owner was shown it and froze it (o924, o928)", a blank line, then the brief text, from the line "# v1.1.0 brief (minor, revision 4)" through the "- Done when: ..." line. The draft's two header lines above it are left out.
2. `docs/release-brief-1.1.0.md` as revision 4, in revision 2's shape: heading "# v1.1.0 brief (minor, revision 4)", the same lines and the 16 tasks, ending with `Frozen: <sha256 of the committed source file> o924 o928 2026-11-24`.

Bytes: both files use LF line endings and end with exactly one trailing newline. The hash is taken from the committed source file with `shasum -a 256` and with `python3 -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" FILE`; both must print the same value or the goal stops. No `.gitattributes` is added.

Order: before committing either file, run `python3 skills/workflow-delivery/scripts/private.py hook message <file>` on both; a non-zero result stops the goal. Commit the source first, hash it, then write the brief with the hash, scan it, commit it.

## Stops

A failed diff against the shown draft, a failed private scan or a hash mismatch stops the goal with one plain message to operation-mac. Every stop goes to operation-mac as one message.

## Evidence log

The goal's runs folder (`.git/loop/runs`) holds `v110-brief-r4.evidence.txt`, never committed: both hashes, the private-scan result for each file (the result only, never a matched text), the `docs.py check` line, the source-vs-draft diff result, the `git diff --stat` and the clock time from `TZ=America/Los_Angeles date` for each entry.

## Checks

- `docs.py check` passes.
- Both hash commands match each other and the Frozen line.
- `git diff --stat` against main shows only the two files and the goal's own files.
- The private scan passes on both files, and a scan of the changed text finds no service-repo name.

## Plan review

The reviewer step is this plan's red team: a fresh subagent that reads the `notify.py plan-review` input and replies in its format, recorded with `notify.py plan-record`.

## Risks

- A text mismatch between the draft and the source (the diff above).
- A stale hash if the source changes after hashing; the source is not touched after its commit.
