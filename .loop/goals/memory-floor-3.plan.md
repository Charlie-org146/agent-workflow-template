# memory-floor-3: plan

Checked against the code: `.loop/config.json` line 42 holds `"min_free_memory_gb": 3.5` once; `skills/workflow-setup/scripts/settings.py` registers the shipped default 4 (not touched); `dev/toy/test-auto-owner-words.py` line 49 hard-coded 3.5 and the GRD-12 row `config-memory-key-once` greps its label.

Build steps:
1. `.loop/config.json`: 3.5 to 3.0 (owner record o39, cited in the commit).
2. Toy line 49 checks that the key is held once and is a positive number, not a value, so putting the floor back to 3.5 needs no edit (the operation session approved this as in scope).
3. Row `config-memory-key-once` grep string follows the new label.

Test for the done line: `python3 -I` is not needed; run `python3 dev/toy/test-auto-owner-words.py` (passes at 3.0) and the row `config-memory-key-once`. It was seen failing on the old toy at 3.0 (the check at 3.5 failed with the config at 3.0).

What could break: any other reader of the floor (board_status reads it with default 3.5, only as a fallback); the lane is long because a config change touches about 891 rows until config-lane (#4321) lands.

Out of scope: the shipped default, the Guardrails page, putting the floor back to 3.5 after v1.0.0.
