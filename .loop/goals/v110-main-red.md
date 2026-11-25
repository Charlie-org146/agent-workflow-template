# Make the four rows that are red on main pass on main in the clean env, by finding and fixing each cause, with no row loosened, skipped or added to a known list (owner o1015, ledger o961; done lines and the regression.yml full-history change approved by owner o1026, ledger o966; issues #5870, #5871, #5872, #5895; a patch, no version task)

- Slug: v110-main-red
- Touches: dev/toy, .loop/regression.tsv, .github/workflows/regression.yml
- ETA: 450 active minutes (estimate 357m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given main, when the row tasks-rows-only-added runs in the clean env, then it passes.
2. Given main, when the row guards-null-report-nofiles runs in the clean env, then it passes.
3. Given main, when the row full-auto-no-new-file runs in the clean env, then it passes.
4. Given main, when the row codex-key-commands runs in the clean env, then it passes.
5. Given the package, when the goal's checks run, then every script stays under 20,480 bytes, no test is loosened, no row turns red, and committed text never names the service repo.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
