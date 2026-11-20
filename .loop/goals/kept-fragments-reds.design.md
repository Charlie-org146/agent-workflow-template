# Design: kept-fragments-reds

Seven rows went red at v1.0.110 from #5380 (kept fragments). Causes, read from CI run 44676371830 and reproduced locally:

1. `audit.py keep()` commits `.loop/kept/<slug>.tsv` with plain git, so a runner with no git identity refuses ("Author identity unknown").
2. `dev/toy/test-how-to-use.py` still committed after `audit.relock`, which now commits the fragment itself (old behaviour).
3. `operate.py wiki_only()` refuses a head that adds `.loop/kept/<slug>.tsv`, so merge.py would refuse every How-to-use re-stamp head.

Older red left out: the toy README has had no Settings block since bc69d9e72 (apply-rerender-blocks, -hand-edit).
Done lines are frozen and met by the plan.
