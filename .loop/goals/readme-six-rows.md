# Five tests aim at the approved README text (TD434; issues 5512 to 5516; operation-top under owner delegation DOC-2, o486; TD415 rule). The approved rewrite (#5499) consolidated wiki text these rows grep: pods-docs (MON-15's moved-to line now names MCH-1, not MCH-4), budgets-agree and aut7-budget-agrees (REG-7's budget text left How-to-use-Regression; REG-7 folded into DEL-17), del-16-on-page (Setup's SET-10 text was replaced) and adoption-golden (SET-6 now reads moved to SET-1, so its [SET-11] link is gone). Each test is aimed at the APPROVED text that says the same thing, at the same strength: no check loosened, no Reviewed wording changed, no row dropped. If a test guards something the approved README no longer says anywhere, it is not changed: the worker lists it with the sentence to operation-mac

- Slug: readme-six-rows
- Touches: .loop/regression.tsv, dev/toy
- ETA: 460 active minutes (estimate 368m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given the five rows on this branch, then each passes and checks the approved text that carries the same fact, and for each a negative control shows the check still fails when that fact is removed from the page
2. Given this goal's diff, then only the five rows' commands or their toys and the goal's record files change, no wiki or README text changes, no row is added or removed, and docs.py check and criteria.py render --check pass
3. Given any of the five whose fact the approved README no longer states, then it is left unchanged and named in the pull request with the missing sentence, for operation-top

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
