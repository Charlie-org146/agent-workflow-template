# doc-sections: one fixed set of sections for README, Home and every wiki page

Goal: .loop/goals/doc-sections.md (frozen done lines 1 to 5; DOC-25, owner record o483). Status: design, condensed.

## What is on main (v1.0.111, read 2026-11-19)

- README: title and link, seven principle sections each with a table and its own diagram (principle-NN.svg), then Requirements by feature. No System design section.
- Home: the same, plus "System diagram", "Settings" and "Automation" (README has none of the three).
- Principles page: one diagram per principle, plus principles-overview.svg (how the principles connect).
- docs/wiki/flows holds 53 figures; 3 Part 1 rows say "none yet" (DOC-24, DEL-21, HLT-2).
- The existing check is pageformat.frontdoor (18,994 of 19,000 bytes): it compares the principle names, sentence and table, flow links, and the Requirements by feature section. It cannot grow.

## Design

1. Requirement: add DOC-25 to Documentation.md, Principles.md and README/Home principle 1 tables, text word for word from the approved draft; Follows names MD043 (adapted) and C4 system context; use the next free ID if DOC-25 is taken.
2. README and Home share one section list: title and one-paragraph introduction, System design, one section per principle (sentence and table, no diagram), Requirements by feature. The System design section shows one figure, built on principles-overview.svg redrawn as a C4 system context view. Home's Settings and Automation move to the Setup and Automation How-to-use pages.
3. Figures: every Part 1 row links its own flows/<ID>.svg, including the 3 "none yet" rows and principle 8's rows.
4. Check: a data file lists the ordered headings per page kind (README, Home, feature, How-to-use, Principles, Tests, Roadmap). A small stdlib check, in a new script so pageformat.py does not grow, fails on a missing, extra, renamed or out-of-order heading and on README and Home differing in sections, a principle's sentence or its table; frontdoor's figure test already fails a row with no flow link, and a new control proves it.
5. PyMarkdown md043 was tried (v0.9.42, throwaway venv, since deleted) and not adopted: one literal list per scan, no per-level wildcard, no cross-file comparison, 8 third-party packages in a stdlib-only package. The check adapts md043's design instead. Notes: shared notes folder, doc-sections-md043-try.md.

## Order and risk

- Plan and figures first; README.md and Home.md edits wait for principle-8-readme on main, then merge main (floor step) and build on it. No goal.py pr before the chain.
- Size: new script small; touched scripts at or under 19,000 bytes and no larger than main. Net regression rows 0 apart from the new controls (5 negative controls: missing, extra, renamed, out of sync, row with no figure).
- Open: how the 3-4 heading lists treat variable tails (### DEL-n); the plan decides (trailing-any marker in the data file).
