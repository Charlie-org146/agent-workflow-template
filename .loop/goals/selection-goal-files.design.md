# Design: selection-goal-files

Problem: a change to .loop/goals/<slug>.md or .loop/kept/<slug>.tsv selects every row whose script reads the wide .loop/ folder (824 of 1,235 land rows on a record-only diff), so a typical pull request runs far more rows than its code reaches.

Approaches: (1) a per-row skip list of record files; (2) treat the record folders as no-code in lanes.touches and select only rows whose command or declared `# reads:` name the file or a folder inside the records. Chosen: 2, one rule in the shared selector, so plan() and affected() agree.

Done lines: 1 a record-only diff selects fewer than 20 rows and no root runner; 2 a row naming a record file is still selected and real code beside it still selects its rows; 3 lanes.py and lanes_cli.py no larger than main, a toy proves 1 and 2 with a negative control.

Open questions: none.
