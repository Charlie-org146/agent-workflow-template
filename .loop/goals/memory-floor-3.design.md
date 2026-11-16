# memory-floor-3: design

Problem: lanes start only at or above `min_free_memory_gb` of free commit memory, and this repo's `.loop/config.json` holds 3.5. Today's free memory is about 3.2 GB, so no lane starts. The owner chose (record o39, Guardrails) to lower the floor to 3.0 until v1.0.0 is released, then put it back.

Approaches:
1. Change the one value in `.loop/config.json` from 3.5 to 3.0. Cost: one line. Risk: a lane at 3.0 GB may run slower or fail on memory; the owner accepted it.
2. Change the shipped default in the settings registry. Cost: wider, and the owner said the shipped default stays 4. Rejected.

Chosen: approach 1, because it meets the done line exactly and touches only this repo's config.

Done line 1 needs: `"min_free_memory_gb": 3.0` in `.loop/config.json`, no other change, the shipped default in `skills/workflow-setup/scripts/settings.py` untouched, and the commit citing o39.

Open questions: none. The follow-up that puts the floor back to 3.5 after v1.0.0 is tracked by the operation session. Any config change touches about 891 regression rows until config-lane (#4321) lands, so the lane is long; nothing is changed to work around that.
