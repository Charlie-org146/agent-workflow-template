# workflow-docs criteria: the PRD page

With `"criteria": true` in `.loop/config.json`, every feature page (each page in `.loop/docs.tsv` but Home, which is
free-form, and a guide: a how-to page with the line `<!-- workflow-docs guide -->` under the marker, kept fresh but
with no PRD, Home row or README section, and not stale on a `.loop/config.json` change) is a short PRD and `check` enforces it, from the rules block of `references/template.md`:

the title, `Milestone:` and `Review:` lines, then `## Problem`, `## Requirements` (up to
`criteria_max` lines like `- DEL-3: **Unreviewed** what must hold`; take the next free id from `criteria PAGE`, never
reuse or renumber one), `## Non-goals`, `## Success metrics` and `## Tests`, which only `criteria.py render` writes.
The full list, and the lines `check` prints: `references/commands.md` (The PRD page).

**The PRD is the owner's.** Only the owner reviews it, and only when their own words say so (`--user`):

```bash
python3 scripts/criteria.py review <PAGE|ID> [...] --user [--date YYYY-MM-DD]
python3 scripts/criteria.py unreview <PAGE|ID> [...] --user
python3 scripts/criteria.py render [--check] [--tables]
```

Run from a session with no terminal, `review` and `unreview` refuse `--user` unless `LOOP_OWNER_WORDS` holds the
owner's own message that said to, quoted exactly; each change is logged with those words in `.git/loop/reviews.tsv`.

A record in `.git/loop/owner-words.tsv` is the owner's own words too: only the operation session writes it
(`sessions.py owner-words "TEXT" --ids A,B`), and a worker never does. Pass `--owner-record ID` with `--user` and the
record's words are used, so don't ask the owner for them again. A record covers only the IDs and pages it lists, once for
`review` and once for `unreview`; any other ID, or a second use, is refused with nothing changed.

An argument like `DEL-3` is a requirement; any other is a page. Every argument is checked before anything is written.
`review PAGE` locks the PRD: after it, an edit shows as `LOCKED` or `CHANGED`; `references/commands.md` (Review
locks) has the rules and how the owner edits a reviewed requirement. Never review or unreview on a goal's own initiative.

**Tests follow on their own.** Write each new regression row's description as one scenario,
`Given <context>, when <action>, then <outcome>.`; what `audit`, `sync` and `cut` do with them: `references/commands.md`.

**New and old pages.** `python3 scripts/prd.py new NAME "<idea>" --paths A,B` drafts a new feature's PRD and
`prd.py convert --write` turns old Summary/Criteria pages into PRD pages; what each leaves to do: `references/commands.md`.

**Where a PRD lives, and topics.** A feature's PRD source is `page` (the default), `url:<link>` or `mcp:<server>:<resource>`,
set in the optional third column of `.loop/docs.tsv`; that page holds `PRD: <source>` and its generated sections only. Agents
read the PRD from the source and never copy it into the repo; its ids drive the Tests tables and health. The check reads it
fresh (`LOOP_PRD_READER`, given the source, reaches an MCP connector such as Notion's) and reports `UNREAD`, never a pass,
when it cannot. The `topics` setting adds a Topic column to Home and `render` groups the rows by it. `sync` (DOC-17) keeps
the repo's copy of an external PRD, `.loop/prd/PAGE.md`, in step: it prints `DRIFT` for each requirement added, removed or
changed, rewrites only a copy it wrote, never writes to the source, and prints `not connected` without a connector.
