v1.1.0 Not frozen

## Release brief draft: v1.1.0 (minor, the dry run)

Rewritten at 23:17 on your words: write DOC-27 and DOC-28, migrate the format and mark the existing features Unreviewed, then implement the two and pass their test cases. The service repo's migration (H1) was added at 23:58 on your words.

### What this release is about (to be in your words)

The new way of working, first in the template. The two features are written into the repo, every existing requirement moves into the feature format and is marked Unreviewed, and the checks that enforce the two features are built, with every one of their test cases passing.

### Features in this release

- DOC-27, the feature standard.
- DOC-28, release kinds and briefs.

### Goals in this release

T1 Write DOC-27 and DOC-28 into the repo

- DOC-27 and DOC-28 are added to the Documentation page as new features through the requirements tool's add path, word for word from this page, both Unreviewed.
- This brief is added as a file, marked "not frozen" until you freeze it.
- The template's config is left as it is on main.
- Docs only: no other file changes.

Done when

- The docs check and the private-name scan pass.
- DOC-27 and DOC-28 read word for word as on this page.

T2 Migrate every existing requirement into the feature format, and mark it Unreviewed

- Every live requirement becomes a feature on the page where it already is, keeping its ID and every word. Its lines become that feature's requirements.
- Each requirement shows its metric from the page's existing Success metrics, or "metric missing", and its test, or "test missing". Each feature shows its references, or "reference missing".
- Every existing feature is marked Unreviewed. Each old mark is kept in the report with its date and record.
- No page is rebuilt: the front page, the How-to-use pages and the figures stay as they are.
- Features with more than five requirements are listed "to split".

Done when

- 27 of 27 migrated with ID, page and every word unchanged, shown by text hashes before and after.
- Outside those entries, every page is byte-identical, and the counts of test links, revision rows and references are unchanged.
- 0 Reviewed marks remain, and every old mark is in the report.
- A second run leaves an empty diff.

T3 Implement DOC-27 and DOC-28, and pass every one of their test cases

- Every test case on this page for DOC-27 and DOC-28 becomes a real test, linked to its requirement.
- The docs check enforces DOC-27 on features: the sections and their order, at most five requirements, one metric and at least one test case each, the Reference section and its tags, the milestone, and a Reviewed mark only from your typed record naming that ID.
- The release tool enforces DOC-28: three kinds, a frozen brief before a major or minor, no edit after the freeze, new work only from the brief, a patch never adds a feature, and the gate for each kind.
- Runs after T1 and T2 are merged, on their result. It can be frozen only once you've reviewed DOC-27 and DOC-28 by ID, because a goal is frozen only on a Reviewed feature (DEL-19).

Done when

- Every DOC-27 and DOC-28 test case runs and passes.
- The template's own pages pass the new docs check. Until you act on them, these are reported, not failed: missing metrics, tests and references; existing features listed "to split"; and the page-rebuild items (the How-to-use pages and the left-over figures), which wait for a later brief.
- No existing test turns red.

H1 Migrate the service repo's requirements into features, in place, all Unreviewed

- Added to v1.1.0 on your words at 23:58. Runs after T1 and T2 merge, through the service repo's own goal path.
- Every the service repo requirement becomes a feature on the page where it already is, keeping its ID and every word, marked Unreviewed. Each old mark is kept in the report with its date and record.
- Missing metrics, tests and references are marked missing. No README text you approved is changed; any line that would have to change is listed, not changed.
- No page is rebuilt. The service repo #1237 stays stopped; its defects stay in its issue.

Done when

- Every the service repo requirement migrated with ID, page and every word unchanged, shown by hashes before and after.
- Outside those entries, every page is byte-identical, and nothing is lost.
- A second run leaves an empty diff.

### Not in this release

The service repo #1237, the page rebuild for the service repo, v2.0.0 and everything stopped tonight (template-only #5687, the known-red fixes, the test-lane fixes, the row cuts), the 3-minute merge, named routines, the trace and header redesigns, the rest of the scan sites, the push-hook change, and the page rebuild (the new front page, removing the How-to-use pages and the left-over figures). They go on the "next" list.

### Done when

- T1, T2, T3 and H1 meet their done lines and are merged, on your words at 23:58.
- v1.1.0 is tagged through the minor path.

A closed GitHub milestone named "v1.1" already exists from an older plan, so this brief's milestone needs its own name, for example "v1.1.0 dry run".
