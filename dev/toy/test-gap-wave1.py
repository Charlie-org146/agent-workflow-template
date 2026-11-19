#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-regression/scripts/lanes_cli.py skills/workflow-regression/scripts/runs.py skills/workflow-regression/scripts/regression.py skills/workflow-monitoring/scripts/replan.py skills/workflow-monitoring/scripts/board_status.py skills/workflow-health/scripts/file.py skills/workflow-health/scripts/automation.py skills/workflow-health/scripts/defects.py skills/workflow-setup/scripts/settings.py skills/workflow-docs/scripts/prdcopy.py
"""gap-wave1-small (OPS-16.6, GRD-12, INT-8, DOC-19, GRD-5.1): three small README gaps.

1. The memory floor defaults to 3 GB in every reader, and a set value (repo or machine-local) still wins.
2. milestones_source is a known setting (checked, not flagged by the migration check), and a repo's own image links are inside the repo.
3. A GH_TOKEN or GITHUB_TOKEN in the environment never turns on a write; only --live does.

usage: test-gap-wave1.py"""
import argparse
import contextlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sk = os.path.join(root, "skills")
for part in ("workflow-regression", "workflow-monitoring", "workflow-health", "workflow-setup", "workflow-docs", "workflow-delivery"):
    sys.path.insert(0, os.path.join(sk, part, "scripts"))
sys.dont_write_bytecode = True
os.environ["LOOP_ROLE"] = "worker"
for var in ("GH_TOKEN", "GITHUB_TOKEN", "GITHUB_ACTIONS", "LOOP_FREE_GB", "LOOP_MACHINE", "DIGEST_RUN"):
    os.environ.pop(var, None)
import board_status  # noqa: E402
import defects  # noqa: E402
import lanes_cli  # noqa: E402
import prdcopy  # noqa: E402
import replan  # noqa: E402
import runs  # noqa: E402
import settings  # noqa: E402

fails = 0
SINK = io.StringIO()


def check(name, ok, extra=""):
    global fails
    print(("PASS: " if ok else "FAIL: ") + name + ("" if ok else "  " + str(extra)))
    fails += 0 if ok else 1


def text_of(*parts):
    with open(os.path.join(sk, *parts), encoding="utf-8") as handle:
        return handle.read()


def quiet(call, *args):
    with contextlib.redirect_stdout(SINK), contextlib.redirect_stderr(SINK):
        return call(*args)


def exits(call, *args):
    try:
        quiet(call, *args)
    except SystemExit as stop:
        return stop.code if stop.code is not None else 0
    return None


# 1. the memory floor
literals = []
for where in (("workflow-monitoring", "scripts", "replan.py"), ("workflow-monitoring", "scripts", "board_status.py"),
              ("workflow-regression", "scripts", "lanes_cli.py"), ("workflow-health", "scripts", "file.py"), ("workflow-setup", "scripts", "settings.py")):
    body = text_of(*where)
    literals += re.findall(r"min_free_memory_gb\"?,\s*(?:REPO,\s*)?([0-9.]+)[,)]", body)
    literals += re.findall(r"^\s+need = ([0-9.]+)$", body, re.M)
default = dict((k, d) for k, _, d, _ in settings.keys(settings.REPO)).get("min_free_memory_gb")
check("every reader's default floor is 3 GB, as the settings table says (%s, table %s)" % (literals, default),
      default == 3 and len(literals) >= 7 and set(literals) == {"3"})
tmp = tempfile.mkdtemp(prefix="gap-wave1-")
os.makedirs(os.path.join(tmp, ".loop"))


def config(**held):
    with open(os.path.join(tmp, ".loop", "config.json"), "w") as handle:
        json.dump(held, handle)


def lane_waits(free, **held):
    """True when wait_memory gives up (it waited the whole 0.05s); False when it let the lane run at once."""
    os.environ.update(LOOP_FREE_GB=str(free), LOOP_MEMORY_WAIT_SECONDS="0.05")
    config(**held)
    return exits(lanes_cli.wait_memory, tmp) is not None


def goals_held(free, **held):
    os.environ.update(LOOP_FREE_GB=str(free), LOOP_MACHINE="8,%s,,," % free)
    return bool(replan.memory_hold(held)), board_status.allowed(held) == 0


lane_default = (lane_waits(3.2), lane_waits(2.5))
os.remove(os.path.join(tmp, ".loop", "config.json"))
os.environ.update(LOOP_FREE_GB="3.2", LOOP_MEMORY_WAIT_SECONDS="0.05")
no_file = exits(lanes_cli.wait_memory, tmp) is None  # no config file at all: still the 3 GB default, so 3.2 GB runs
check("a lane waits under 3 GB and runs at 3.2 GB when the key is unset (%s) and with no config file (%s)" % (lane_default, no_file),
      lane_default == (False, True) and no_file)
check("the operation holds no goal at 3.2 GB and holds them at 2.5 GB with the key unset (%s %s)" % (goals_held(3.2), goals_held(2.5)),
      goals_held(3.2) == (False, False) and goals_held(2.5) == (True, True))
check("a set value still wins: a floor of 5 holds a lane and the goals at 3.2 GB, a floor of 1 runs a lane at 2.5 GB",
      lane_waits(3.2, min_free_memory_gb=5) and goals_held(3.2, min_free_memory_gb=5) == (True, True) and not lane_waits(2.5, min_free_memory_gb=1))
for var in ("LOOP_FREE_GB", "LOOP_MACHINE", "LOOP_MEMORY_WAIT_SECONDS"):
    os.environ.pop(var, None)

# 2. milestones_source and the repo's own image links
home = os.path.join(tmp, ".loop", "config.json")
GOOD = ["", "url:https://example.org/ms", "mcp:notion:" + "ab12" * 8, "mcp:other:page-1"]
BAD = ["plain words", "url:", "mcp:notion:abc", "mcp:notion:" + "xyz!" * 8, "mcp:notion:" + "ab12" * 9, 5]
known = dict((k, d) for k, _, d, _ in settings.keys(settings.REPO)).get("milestones_source", "absent")


def fill(value):
    config(**{"milestones_source": value} if value != "" else {})
    got = exits(settings.fill_repo, home)
    return got, json.load(open(home)).get("milestones_source")


kept = [fill(v) for v in GOOD]
refused = [fill(v)[0] for v in BAD]
check("milestones_source is a known setting, empty by default, that keeps a good value and refuses a bad one (%s, %d refused)" % ([k[1] for k in kept], sum(1 for r in refused if r)),
      known == "" and all(code is None for code, _ in kept) and kept[2][1] == GOOD[2] and kept[0][1] == "" and all(code for code in refused))
placed = []
cfg = {k: d for k, _, d, _ in settings.keys(settings.REPO) if k not in ("regression_runs", "milestones_source")}
for extra in ({}, {"milestones_source": "mcp:notion:" + "ab12" * 8}):
    placed.append([c for c in (lambda out: (defects.gaps_settings(root, dict(cfg, **extra), lambda *a: out.append(a)), out)[1])([])])
unknown = []
defects.gaps_settings(root, dict(cfg, not_a_setting=1), lambda *a: unknown.append(a))
check("the migration check flags neither a set nor an unset milestones_source, and still flags an unknown key (%s %s)" % (placed, unknown),
      placed == [[], []] and len(unknown) == 1 and "not_a_setting" in unknown[0][1])
png = "https://github.com/me/proj/blob/main/docs/a.png?raw=true"
own = [png, "https://github.com/me/proj/raw/main/img/b.svg", "https://github.com/me/proj/blob/main/x.jpg"]
other = ["https://github.com/other/proj/blob/main/docs/a.png?raw=true", "https://github.com/me/proj/blob/main/src/a.py",
         "https://github.com/me/proj/blob/main/src/a.py?x=.png", "https://github.com/me/proj/issues/3", "https://github.com/me/proj-two/blob/main/a.png"]
stand = lambda url: len(prdcopy.stands_alone("P", "See " + url + " here.", "me/proj"))
check("the repo's own image links stand, and another repo's image, a source file, a query that only ends in .png and an issue do not (%s %s)"
      % ([stand(u) for u in own], [stand(u) for u in other]), all(stand(u) == 0 for u in own) and all(stand(u) == 1 for u in other))
check("the repo's README link and its milestones still stand, and an outside site still fails",
      stand("https://github.com/me/proj/blob/main/README.md") == 0 and stand("https://github.com/me/proj/milestones") == 0
      and stand("https://example.org/a.png") == 1)

# 3. a token never turns on a write
calls = []


class Done(subprocess.CompletedProcess):
    pass


def fake(args, **kw):
    calls.append(list(args))
    return Done(args, 0, "[]", "")


real_run = subprocess.run
WRITE = ("create", "comment", "edit", "close", "pin", "reopen", "delete")


def writes():
    return [c for c in calls if c[:1] == ["gh"] and (any(w in c for w in WRITE) or "-X" in c or "POST" in c or "PATCH" in c)]


def digest(live, token):
    import automation
    del calls[:]
    os.environ.pop("GH_TOKEN", None)
    os.environ.pop("GITHUB_TOKEN", None)
    token and os.environ.update(GH_TOKEN="x", GITHUB_TOKEN="x")
    subprocess.run = fake
    try:
        said = io.StringIO()
        with contextlib.redirect_stdout(said):
            code = automation.cmd_digest(argparse.Namespace(root=tmp, owner="", live=live))
    finally:
        subprocess.run = real_run
        os.environ.pop("GH_TOKEN", None)
        os.environ.pop("GITHUB_TOKEN", None)
    return code, said.getvalue(), len([c for c in calls if c[:1] == ["gh"]]), len(writes())


config(base="main")
none = digest(False, True)
yes = digest(True, False)
check("the digest with a token and no --live makes no gh call, and with --live and no token it writes (token: %s %s; live: %s %s)" % (none[2], none[1].strip().splitlines()[-1], yes[2], yes[3]),
      none[0] == 0 and none[2] == 0 and "DRY RUN: no --live" in none[1] and yes[2] > 0 and yes[3] > 0)


def owed(live, token):
    del calls[:]
    token and os.environ.update(GH_TOKEN="x")
    subprocess.run = fake
    runs.gh = lambda *a, body=None: fake(("gh",) + a)
    got = argparse.Namespace(id="row", runner="Mac", live=live)
    try:
        quiet(runs.owed_record, tmp, got, lambda: "2026-11-19", lambda r: {"row": {"seen_red": ""}})
        quiet(runs.notrun_todo, tmp, "slug", ["row"], live)
    finally:
        subprocess.run = real_run
        os.environ.pop("GH_TOKEN", None)
        os.remove(os.path.join(tmp, ".loop", "regression-owed.tsv")) if os.path.exists(os.path.join(tmp, ".loop", "regression-owed.tsv")) else None
    return len(writes())


check("a to-do issue is opened only with --live, never by a token alone (token only: %d writes; --live: %d)" % (owed(False, True), owed(True, False)),
      owed(False, True) == 0 and owed(True, False) > 0)
READ = re.compile(r"environ(?:\.get)?[(\[]\s*[\"'](?:GH_TOKEN|GITHUB_TOKEN)")
leaks = [name for name in ("regression.py", "runs.py", "automation.py")
         if READ.search(text_of("workflow-health" if name == "automation.py" else "workflow-regression", "scripts", name))]
check("no write switch in regression.py, runs.py or automation.py reads GH_TOKEN or GITHUB_TOKEN (%s)" % leaks, not leaks)
check("a token is read only by regression.py's own help text, never to decide a write",
      "a token in the environment writes nothing" in text_of("workflow-regression", "scripts", "regression.py"))
print("PASS: the three gaps are closed" if not fails else "FAILED %d" % fails)
sys.exit(1 if fails else 0)
