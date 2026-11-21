# Design: adoption-count-fix

## Problem

`follows()` and `adoption()` in `skills/workflow-docs/scripts/sections.py` read one tag per Follows bullet. A bullet that names two sources, each with its own tag (`[A](url): adapted; [B](url): adopted`), therefore counts one tag for both, and the Adoption share on the front pages is wrong for HLT-2, REG-4 and MCH-1. The README text is right; the counter is wrong.

## Approaches

**A. Split the bullets in the README.** One source per bullet, so the old counter reads them correctly. Cost: small. Risk: it changes Follows lines, which the goal forbids, and the next two-source bullet breaks the counter again. Rejected.

**B. Make the counter read each source's own tag (chosen).** `follows()` splits a bullet at `; ` only when the text before the split is itself a complete `source: tag` pair, and only outside brackets and parentheses, so a `; ` inside a link or a source name does not split and an untagged bullet is never split. `adoption()` stays the adopted share over all sources. Cost: about 20 lines in one script. Risk: a wrong split on odd link text, which the toy covers with negative controls. Chosen because it fixes the cause once and changes no requirement text.

## What each done line needs

1. A toy with a two-source bullet (adapted and adopted) returning 50, single-source bullets (adopted, adapted, planned, own) returning their main values, and negative controls for a semicolon inside a link or source name and for an unknown tag. Lives in `dev/toy/test-follows-adoption.py`.
2. `criteria.py render` rewrites only Adoption cells and headline lines in README, Home and Principles. After the merge of main it changes only HLT-2 (33 to 25 percent) and MCH-1 (25 to 20 percent) plus the two headlines that average them. `render --check` and `docs.py check` pass.
3. The diff is `sections.py` (under 19,000 bytes), the re-rendered front pages, the toy and this goal's records. No requirement text, tag or Follows line changes; the private scan is clean.

## Open questions

None for the owner. Operation ruled that MCH-1 stays at 20 percent with no change to its requirement text.
