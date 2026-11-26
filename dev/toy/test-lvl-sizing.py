#!/usr/bin/env python3
# reads: skills/workflow-delivery/scripts/sizing.py dev/toy/lvl_fixture.py
"""v110-lvl-relevel line 5: a size table whose size leaves out L1 is refused when the settings are read, naming the size
and L1."""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.dont_write_bytecode = True
from lvl_fixture import DELIVERY, Repo, check, done  # noqa: E402

sys.path.insert(0, DELIVERY)
import sizing  # noqa: E402

READ = "import sys; sys.path.insert(0, sys.argv[1]); sys.dont_write_bytecode = True; import sizing; sizing.read_table()"


def with_levels(size, value):
    table = json.loads(json.dumps({s: sizing.DEFAULTS[s] for s in ("small", "medium", "large")}))
    table[size]["levels"] = value
    return table


def read(table):
    """The settings read the loop makes, from the base branch's .loop/config.json."""
    repo = Repo(risks=None)
    repo.write(".loop/config.json", json.dumps({"base": "main", "checks_by_size": table}))
    repo.commit()
    got = subprocess.run([sys.executable, "-c", READ, DELIVERY], cwd=repo.path, env=repo.env, capture_output=True,
                         text=True)
    repo.close()
    return got.returncode, got.stdout + got.stderr


status, said = read(with_levels("medium", ["L0"]))
check(status != 0 and "SIZING_BAD_LEVELS" in said and "medium" in said and "L1" in said,
      "a size that leaves out L1 is refused, naming the size and L1", said)
check(said.count("SIZING_BAD_LEVELS size") == 1 and said.count("REFUSED") <= 1, "the read refuses once", said)
for value, name, word in ((["L1", "L2"], "leaves out L0", "L0"), (["L0", "L1", "L3"], "names L3", "L3"),
                          ("L0,L1", "is not a list", "not a list")):
    status, said = read(with_levels("large", value))
    check(status != 0 and "SIZING_BAD_LEVELS" in said and "large" in said and word in said, "a list that %s is refused" % name,
          said)
status, said = read(with_levels("small", ["L0", "L1"]))
check(status == 0, "control: a size listing L0 and L1 is read", said)
table, why = sizing.validate(with_levels("small", ["L0", "L1"]))
check(why == "" and "levels" not in table["small"], "the levels list is not read as a check", why)
table, why = sizing.validate({s: sizing.DEFAULTS[s] for s in ("small", "medium", "large")})
check(why == "" and table.get("levels") == {"small": ["L0", "L1"], "medium": ["L0", "L1"], "large": ["L0", "L1", "L2"]},
      "with no levels key: small and medium run L0 and L1, large L0, L1 and L2", table.get("levels") if table else why)
sys.exit(done())
