# Plan: v1-go-no-go

1. Record the short-check results (health.py check, dev/package.py, docs.py check, entry.py lag, unique ids).
2. Run the flow steps in condensed depth and open the pull request.
3. release.py cut v1-go-no-go --bump major creates the draft v1.0.0; send operation the link and results.

Out of scope: publishing v1.0.0, merging, the full regression suite (run afterwards, one lane at a time).
