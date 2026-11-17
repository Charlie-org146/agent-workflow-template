# hotfix-4892 plan

Checked: govern_hook.py line 38 imports reply_hook; the only `__import__` is in remember() (line 272); checkin.py calls govern_hook.remember().
Steps: (1) replace `__import__("reply_hook").write(` with `reply_hook.write(`. Test: row quiet-plain-import-4892 (defect, seen red); package-passes and package-passes-3800 pass. (2) Verify by hand in the goal file.
Could break: nothing else touches remember(); no new import cycle (reply_hook is already imported at module load).
Out of scope: fit.py, lanekit.py, guards.py sizes (trim-scripts-19k, #4653); regression-known.tsv lists none of these rows.
