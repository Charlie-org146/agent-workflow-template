# migrate-features: design

Goal G1 of the v1.1.0 brief. The spec for the feature shape is DOC-27 on the owner's draft page; this goal uses it as a spec only and adds no requirement text. The 27 live requirements become features in place.

## What exists on main (read, not assumed)

- 27 requirement lines on 11 feature pages (`- ID: **Reviewed DATE** title <!-- reviewed HASH -->`, or `**Unreviewed**` for SET-10), 121 sub-bullet lines in all, 26 of the 27 Reviewed. Pages: Automation, Check-in-and-board, Delivery, Documentation, Guardrails, Health, Integrations, Machines, Operation, Regression, Setup.
- A requirement's text is `unit(title, sub-bullets)` in `pageformat.py`. Three places depend on it staying exactly as it is: the head Revisions row of that ID (`revcheck`), the `reviewed HASH` seal (`LOCKED`), and the Complete text columns that README, Home and Principles generate. So a marker written as a sub-bullet would force a new Revisions row and a new front-page table, which the done lines forbid (revision rows and front pages stay as they are).
- `subs()` in `criteria.py` stops at the first blank line, and `blocks()` skips indented lines. A marker block that follows a blank line is therefore outside the requirement's text for the hashes, the Revisions row, the README tables and the 20-word title rule, and it still renders under the entry in markdown. Prototyped on one entry in a scratch edit and reverted: `docs.py check` DOCS OK and `criteria.py render --check` TABLES OK with the old Reviewed mark replaced by Unreviewed and one blank-separated marker line added.
- Tests link by requirement ID (`regression.tsv` goal column): 25 of 27 IDs have rows (counts 1 to 57); DOC-26 and INT-1 have none. Success metrics are 2 or 3 free-text bullets per page, and only OPS-1's bullet names a requirement ID. References are the Follows cell of each requirement's row in the Principles table. Old marks and their records are the latest `review` row per ID in the shared reviews log.

## Shape of a migrated feature (the recommended answer)

Per entry, after its last sub-bullet, one blank line and one marker block, written between two fixed comment lines so a re-run replaces it:

```
- DOC-2: **Unreviewed** title
  - the entry's own lines, byte for byte
  - ...

  <!-- feature markers v1 -->
  - Reference: <Follows cell, verbatim> | reference missing
  - Line 1: metric <"Success metric N of this page" when that bullet names the ID> | metric missing; test <N linked rows, see Tests> | test missing
  - Line 2: ...
  <!-- /feature markers -->
```

Rules, each a fixed function of the page and nothing judged:

- A line's metric is a Success metric bullet only when the bullet names the ID; otherwise `metric missing`. Nothing is written into the Success metrics section. The owner's own count says no line has a linked metric yet; this makes that visible instead of guessing.
- A line's test is the count of regression rows linked to the ID (tests link per requirement, not per line, so every line of an ID shows the same count); zero rows is `test missing`. No test link, row or Tests table changes.
- A feature's reference is its Follows cell from the Principles table, verbatim; an empty cell is `reference missing`.
- Features with more than five lines are listed `to split` in the report (the owner counts 9; the migration counts by the same rule and reports the number it gets). Nothing is split.
- Every Reviewed mark is cleared: `**Reviewed DATE**` becomes `**Unreviewed**` and the trailing `<!-- reviewed HASH -->` goes. Each is listed in the report with the date, the seal and the record (the latest review row for the ID). The report is the only place the old marks survive.

## Where it lives

- `docs/migrations/features-v1.py`: one script, python standard library only, under 19,000 bytes, run from the repo root. It reads the pages, the Principles table, `regression.tsv` and the reviews log if present; it writes the 11 feature pages and the report. It takes no secret and no network.
- `docs/migrations/features-v1-report.md`: per ID, the page, the text hash before and after (sha256 of `unit(...)`, equal by construction and checked), the mark cleared with date, seal and record, lines, metric, test and reference results, and the `to split` list.
- No new regression row is planned. One toy test is added under `dev/toy` if the plan finds the script cannot be proven by running it on a copy; any row added is said in the PR notes.

## Re-run safety

The marker block is replaced between its two comment lines, never appended; a mark that is already `Unreviewed` is left alone; the report is rewritten from the same inputs, and its old-mark table is kept from the existing report when no Reviewed mark is left to read. A second run therefore leaves an empty diff, proven by running it twice on a scratch copy and diffing.

## How each done line is proven

1. 27 ID, page and text hashes before and after, listed in the report, equal. 2. A byte comparison of every other file against main: only the 11 feature pages, the report and the script differ; Home, README, Principles, How-to-use pages, figures and Tests are identical. 3. Counts of test links (rows per ID), Revisions rows and Follows references before and after are equal; every line shows a metric and a test result and every feature a reference result. 4. Zero `**Reviewed` marks remain; the report lists every cleared mark and the `to split` features. 5. Run twice: empty diff; the goal stops at the pull request.

## Risks

- A later checker (T3) will define the final marker shape; this goal's block is a stand-in the owner may rewrite, which is why it sits between two comment lines.
- A hidden consumer of the page text other than the ones read here (health, wiki publish, sync) may care about the new lines; the plan runs the docs check, the tables check, `wiki.py prepare` and the health check on the migrated copy before the build is trusted.
- Clearing the marks edits requirement lines without a Revisions row, because the text is unchanged; the existing check treats that as allowed (verified in the prototype).
