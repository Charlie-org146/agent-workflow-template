# Plan: go-app-sessions
1. graph.py `app_only(cfg)`; watch.py `start_round` holds instead of launching under it; `runs()` skips non-dicts.
2. settings.py: register `workers` (trim a long description to stay under the size cap); set it here; regenerate Home,
   START.md and the README block.
3. dev/toy/test-go-app-sessions.py, rows go-app-holds-goal, go-background-default, runs-skips-non-dict (each seen red).
Out of scope: mend.py's restart, the HEAD_MOVED exits of #4004.
