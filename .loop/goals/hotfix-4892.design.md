# hotfix-4892 design

Problem: `dev/package.py` flags `__import__("reply_hook")` in govern_hook.py's `remember()` (line 272), so package-passes-3800 and package-passes fail. The module already has `import reply_hook` at line 38.

Approaches: (1) keep `__import__` and allow it in the scan: weakens the safety gate. (2) call `reply_hook.write(...)` through the existing import: one line, same behaviour.

Chosen: 2. Scope was narrowed by the operation session: the delivery scripts' 19,000-byte trim stays with trim-scripts-19k (#4653), so scripts-a-delivery-under-19000 stays known red.

Done lines: (1) the one-line change; dev/package.py passes; setup.py --reply-hook installs reply_hook.py and govern_hook.py, both unchanged apart from this line. (2) defect row quiet-plain-import-4892 (dev/toy/test-quiet-import.py), seen red with the old line put back.
Open questions: none.
