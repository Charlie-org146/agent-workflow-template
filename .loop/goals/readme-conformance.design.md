# Design: readme-conformance

## Problem

The consolidated README (requirements-consolidate) is the single source of truth for v2.0, and the v2.0 gate waits on zero gaps. Nobody knows today which of its 226 bullets main already does, which it half does and which it does not, nor how the 38 issues moved to v2.0 relate to those bullets. Without that table no goal can be planned against the README and the tag has no ETA.

## Approaches

1. **One long manual read.** One session reads the README and the code in order. Cheap to start, but 226 bullets across twelve features is a long serial read, one reader's misses go unnoticed, and the evidence quality varies with fatigue. Risk: a missed gap passes the gate.
2. **Parallel read-only passes by feature, then a hand check.** Six reviewers each take a feature group, read code, tests and pages, and fill a fixed row (status, evidence, what is missing, issues, closing idea, size flag). I merge them, re-check every disagreement and a sample by grep, add the rows the README tip changed since the first pass, then cluster the gaps and map the issues. Cost: more tokens; risk: a confident but wrong row, covered by the grep check and by taking the stricter status where passes disagree. **Chosen.**

## Choices

- Table unit is the distinct bullet (the same bullet shows under up to four features), keyed by requirement row and ordinal.
- `done` needs code plus a test row or a page; a red, known-red or not-run row is no passing test.
- Gaps are grouped into clusters that could each be one goal, PC-friendly and small first, each flagged for scripts at or over the 19,000-byte line (12 shipped scripts are over it now).
- Built on the pushed tip (fc691448), to be re-run as a delta after requirements-consolidate merges.
- Output is two files under `.loop/`; no shipped file, no requirement text, no regression row.

## What each done line needs

1. `.loop/readme-gap-table.md`: one row per bullet, a status, evidence, and a closing cluster for each gap; the cluster list with size flags; the rows the consolidation PR closes.
2. `.loop/readme-issues-map.md`: all 38 issues mapped to a bullet (or none) with a state and a reason, and a close list that goes to operation-top in one message.
3. `git diff --stat origin/main` shows only `.loop/` files; `docs.py check` passes; `regression.tsv` is unchanged.

## Open questions

- None that block the table. Findings the owner must decide (README versus owner records o86, o104, o90; the missing board skill; the Backlog milestones) are listed in the table and the close list, not here.
