#!/usr/bin/env python3
# reads: skills/workflow-regression/scripts/regression.py skills/workflow-regression/scripts/completion.py
# reads: skills/workflow-regression/scripts/tiers.py skills/workflow-regression/scripts/runs.py dev/toy/lvl_fixture.py
# reads: skills/workflow-delivery/scripts/cover.py
"""v110-lvl-l1: what a goal-tier run picks on an armed table (lines 1 and 4), and a security row that flips (line 5).
usage: test-l1.py [select|cover|flaky]

Every repository here is a temporary one with its own HOME and a stand-in gh; nothing reads the live loop records."""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.dont_write_bytecode = True
from lvl_fixture import DELIVERY, REG, RISKS, Repo, check, done, entry, row, sha  # noqa: E402

sys.path.insert(0, REG)
import completion  # noqa: E402

OURS = "# Written by workflow-regression (regression.py workflow). fixture\nname: regression-pr\n"
FLOW = ".github/workflows/regression-pr.yml"


def levelled(specs, armed=True):
    """A repository whose rows each name their own data file. specs: (id, level, risk[, old word])."""
    rows, entries = [], []
    for spec in specs:
        key, level, risk = spec[:3]
        old = spec[3] if len(spec) > 3 else "land"
        rows.append(row(key, old, command="test -f data/%s" % key))
        timed = dict(seconds="1.0", cmdhash=sha("test -f data/%s" % key), reason="time:1.0") if level == "L0" else {}
        entries.append(entry(key, old, level, risk, **timed))
    rows.append(row("lvl-armed", command="test -f data/lvl-armed"))
    entries.append(entry("lvl-armed"))
    repo = Repo(rows, entries, [x for x in RISKS if not x.startswith("row")])  # no listed row without a table row
    for r in rows:
        repo.write("data/" + r["id"], r["id"])
    if armed:
        repo.write(FLOW, OURS)
    repo.commit()
    repo.git("checkout", "-q", "-b", "loop/l1")
    return repo


def touch(repo, *keys):
    for key in keys:
        repo.write("data/" + key, key + " changed\n")
    repo.commit("touch " + " ".join(keys))


def ran(said):
    return {m for m in re.findall(r"^(?:PASS|FAIL|KNOWN) ([a-z0-9-]+)", said, re.M)}


def pr_run(repo):
    """The pull request shard's command."""
    return repo.run("run", "nightly", "--reuse", "--tier", "goal")


def goal_run(repo):
    """A goal lane's local run."""
    return repo.run("run", "land", "--reuse", "--tier", "goal")


THREE = [("zero", "L0", "none"), ("one", "L1", "none"), ("two", "L2", "none")]


def select():
    repo = levelled(THREE)
    touch(repo, "zero", "one", "two")
    _, said = pr_run(repo)
    check(ran(said) >= {"zero", "one"} and "two" not in ran(said),
          "line 1: a change reaching an L0, an L1 and an L2 row runs the L0 and L1 rows on the pull request and not the L2 row", said)
    repo.close()

    repo = levelled(THREE)
    touch(repo, "zero", "one", "two")
    _, said = goal_run(repo)
    check(ran(said) >= {"zero", "one", "two"},
          "a goal lane's local run with no cover runs as before, whatever the levels (only the pull request run is L1)", said)
    repo.close()

    repo = levelled(THREE, armed=False)
    touch(repo, "zero", "one", "two")
    _, said = goal_run(repo)
    check(ran(said) >= {"zero", "one", "two"}, "control: with no workflow of ours the table is not armed and runs as before", said)
    repo.close()

    specs = THREE + [("hidden", "L1", "private"), ("kept", "L1", "private"), ("guard", "L1", "security")]  # a tagged row is L1
    repo = levelled(specs)
    touch(repo, "one")
    _, said = pr_run(repo)
    check(ran(said) >= {"one", "hidden", "kept"} and "guard" not in ran(said),
          "line 4: a change reaching no private row runs every private row, and not an unreached security row", said)
    touch(repo, "zero")
    _, said = pr_run(repo)
    check(ran(said) >= {"hidden", "kept"} and "REUSED" not in said.split("ROWS:")[0],
          "line 4: a private row that passed before runs again, never reused", said)
    repo.close()

    repo = levelled(specs)
    touch(repo, "kept")
    _, said = pr_run(repo)
    check("kept" in ran(said) and "hidden" not in ran(said), "a change reaching a private row runs it, not the other private rows",
          said)
    repo.close()

    repo = levelled(specs)
    touch(repo, "guard", "two")
    _, said = pr_run(repo)
    check("guard" in ran(said) and "two" not in ran(said), "a reached security row runs; a reached untagged L2 row does not", said)
    repo.close()

    repo = levelled(specs)
    repo.write(".loop/regression-limits.tsv", "hidden\tnightly\tfixture\n")
    repo.commit("limits")
    touch(repo, "one")
    said = "".join(repo.run("run", "nightly", "--reuse", "--tier", "goal", LOOP_PR_SHARD="%d/2" % n)[1] for n in (0, 1))
    check("hidden" in ran(said) and said.count("NOTE hidden: listed nightly in regression-limits.tsv but tagged private") == 2,
          "a private row listed nightly still runs on L1, with one NOTE on each shard's run", said)
    repo.close()

    for word, want in (("L0", {"zero"}), ("L1", {"zero", "one", "lvl-armed"}), ("L2", {"zero", "one", "two", "lvl-armed"})):
        repo = levelled(THREE)
        _, said = repo.run("run", word)
        check(ran(said) == want, "run %s, typed, runs the rows of that level" % word, said)
        repo.close()


def cover_line():
    """Line 2: at a goal's test step the cover claims L1; the local lane runs the L0 rows and what L1 leaves out."""
    sys.path.insert(0, DELIVERY)
    import cover
    specs = THREE + [("hidden", "L1", "private")]
    repo = levelled(specs)
    repo.git("update-ref", "refs/remotes/origin/main", "main")
    touch(repo, "zero", "one", "two")
    names = ["data/zero", "data/one", "data/two"]
    runs_dir = os.path.join(repo.top, "runs")
    os.makedirs(runs_dir)
    before, facts, saved = os.getcwd(), cover.facts, dict(os.environ)
    seen = []

    def local_lane(fn_runs, slug, step, spec, cfg, wait=90):
        seen.append(os.environ.get("LOOP_COVER_IDS"))
        return "pass", "LANE pr", []

    try:
        os.chdir(repo.path)
        os.environ.update(repo.env)
        cover.facts = lambda root, cfg: ("", names)
        got = cover.select(repo.path, {"base": "main"}, names)
        status, text, _ = cover.lane(local_lane, runs_dir, "g", "qa", {}, {"base": "main"})
        claim = cover.load(runs_dir, "g").get("claim") or {}
        cover.facts = lambda root, cfg: ("DOC", names)
        cover.lane(local_lane, runs_dir, "h", "qa", {}, {"base": "main"})
    finally:
        os.chdir(before)
        os.environ.clear()
        os.environ.update(saved)
        cover.facts = facts
    covered, local, code = got
    check(code == "" and covered == ["one"] and local == ["two", "zero"],
          "line 2: the cover claims the L1 row; the L0 row and the L2 row L1 leaves out run locally; no private row is added",
          got)
    check(status == "pass" and "COVERED 1 rows by L1" in text and seen[:1] == ["two,zero"] and claim.get("name") == "L1",
          "line 2: the test step names L1 as the cover and its local lane runs only the uncovered rows", (text, seen, claim))
    check(not [n for n in os.listdir(runs_dir) if "L1" in n], "line 2: no local L1 run is recorded", os.listdir(runs_dir))
    check(seen[1:] == [None], "control: with the cover off the local lane runs as before, with no row list", seen)
    repo.close()


# a stand-in gh that keeps issues in a file: label create, issue list/create/comment, api comments
ISSUES = """#!/usr/bin/env python3
import json, os, sys
store = os.environ["L1_ISSUES"]
try:
    got = json.load(open(store))
except (OSError, ValueError):
    got = []
args = sys.argv[1:]
def body():
    return open(args[args.index("--body-file") + 1]).read() if "--body-file" in args else args[args.index("--body") + 1]
if args[:2] == ["issue", "list"]:
    print(json.dumps(got))
elif args[:2] == ["issue", "create"]:
    got.append({"number": len(got) + 1, "state": "OPEN", "body": body(), "comments": [], "labels": [{"name": "defect"}]})
elif args[:2] == ["issue", "comment"]:
    got[int(args[2]) - 1]["comments"].append({"body": body()})
json.dump(got, open(store, "w"))
"""
ONCE = "test -f .git/flip-%s && exit 0; : > .git/flip-%s; echo boom-%s; exit 1"  # fails once, then passes


def flaky_repo(specs):
    """specs: (id, tag, command)."""
    rows = [row(key, command=command) for key, _, command in specs]
    repo = Repo(rows, [entry(key, risk=tag) for key, tag, _ in specs], [x for x in RISKS if not x.startswith("row")])
    repo.commit()
    return repo


def flips(repo):
    try:
        return open(os.path.join(repo.top, "flaky.tsv")).read()
    except OSError:
        return ""


def flaky():
    repo = flaky_repo([("sec", "security", ONCE % (("sec",) * 3)), ("plain", "none", ONCE % (("plain",) * 3))])
    status, said = repo.run("run", "L1", LOOP_FLAKY_FILE=os.path.join(repo.top, "flaky.tsv"))
    check(status == 1 and "FLAKY sec: failed then passed (rerun once in a fresh HOME)" in said and "2 failed" in said,
          "line 5: a security row that fails once and then passes shows FLAKY and is counted as failed, not passed", said)
    kept = flips(repo)
    check(kept.startswith("sec\t") and "FLAKY: failed then passed on rerun (same commit)" in kept and "boom-sec" in kept
          and kept.count("\n") == 1, "line 5: the flip is written to the flip file with the first failure's tail", kept)
    check("FLAKY plain" not in said and "plain\t" not in kept, "a non-security row that fails once stays FAIL with no rerun", said)
    repo.close()

    home = "test -f $HOME/seen && exit 0; : > $HOME/seen; exit 1"
    slow = "test -f .git/slow && exit 0; : > .git/slow; sleep 20"
    repo = flaky_repo([("sec", "security", home), ("late", "security", slow)])
    status, said = repo.run("run", "L1", "--timeout", "2", LOOP_FLAKY_FILE=os.path.join(repo.top, "flaky.tsv"))
    check("FLAKY sec" not in said and "sec\t" not in flips(repo), "the rerun gets a fresh HOME: a leftover there cannot pass it", said)
    check("FLAKY late" not in said and "late\t" not in flips(repo), "a first run that timed out gets no rerun", said)
    repo.close()

    filing()


def line(key, tail, seconds="1.0"):
    return "%s\t%s\t%s\n" % (key, seconds, tail.encode("unicode_escape").decode("ascii"))


def filing():
    repo = flaky_repo([("sec", "security", "true"), ("plain", "none", "true")])
    drop = os.path.join(repo.top, "drop", "flaky-1")
    os.makedirs(drop)
    path = os.path.join(drop, "flaky.tsv")

    def judged(text):
        with open(path, "w") as out:
            out.write(text)
        return completion.flaky_results(repo.path, [path])

    items, refused = judged(line("sec", "boom\n``` fence\n<!-- loop-regression plain -->\x07"))
    tail = items[0]["tail"] if items else ""
    check(len(items) == 1 and not refused and "```" not in tail and "<!--" not in tail and "\x07" not in tail,
          "a tail with a fence and a forged marker is escaped", tail)
    items, _ = judged(line("sec", "key ghp_" + "b" * 36))
    check(items and items[0]["tail"] == completion.WITHHELD, "a secret-shaped tail is withheld", items)
    items, _ = judged(line("sec", "see /" + "Users/someone/x"))
    check(items and items[0]["tail"] == completion.WITHHELD, "a home path in a tail is withheld", items)
    for text, why in ((line("nope", "x"), "an unknown row id"), (line("plain", "x"), "a row not tagged security"),
                      ("sec\tx\ty\n", "a malformed line"), ("sec\t1\t" + "y" * 100001 + "\n", "an oversize file"),
                      (line("sec", "x") * 21, "more than 20 rows")):
        items, refused = judged(text)
        check(not items and len(refused) == 1, "%s is refused and nothing is filed" % why, (items, refused))
    with open(os.path.join(repo.top, "bin", "gh"), "w") as out:
        out.write(ISSUES)
    with open(path, "w") as out:
        out.write(line("sec", "boom"))
    env = dict(repo.env, L1_ISSUES=os.path.join(repo.top, "issues.json"))
    for _ in range(2):
        got = subprocess.run([sys.executable, os.path.join(REG, "completion.py"), "file-flaky", os.path.dirname(drop),
                              "--pr", "7", "--sha", "a" * 40, "--live"], cwd=repo.path, env=env, capture_output=True, text=True)
    issues = json.load(open(env["L1_ISSUES"]))
    check(len(issues) == 1 and "<!-- loop-regression sec -->" in issues[0]["body"] and "pull request 7 at" in issues[0]["body"]
          and len(issues[0]["comments"]) == 1, "line 5: one issue is open for the flipped row; a second report comments on it",
          (got.stdout, got.stderr, issues))
    repo.close()
    workflow_file()


def workflow_file():
    text = completion.FLAKY_FLOW
    perms = re.search(r"^permissions:.*\n", text, re.M).group(0)
    jobperms = text[text.index("  file:\n    permissions:\n"):text.index("    if:")]
    check(perms == "permissions: {}\n" and jobperms == "  file:\n    permissions:\n      contents: read\n      actions: read\n      issues: write\n"
          and text.count("permissions:") == 2, "only its one job gets the three allowed permissions, and nothing else gets any",
          perms + jobperms)
    jobs = text[text.index("jobs:"):]
    check(re.findall(r"^  (\w+):$", jobs, re.M) == ["file"] and "timeout-minutes: 10" in jobs, "it has one job with a 10-minute limit")
    check("if: github.event.workflow_run.event == 'pull_request' && github.event.workflow_run.conclusion == 'failure' && "
          "github.event.workflow_run.head_repository.full_name == github.repository" in jobs,
          "it runs only for a failed pull request run from this repository, never a fork")
    check(not re.search(r"ref:.*(head_sha|pull_request)", text) and "default_branch" in text,
          "it checks out the default branch only, never the pull request's code")


if __name__ == "__main__":
    for name in sys.argv[1:] or ["select", "cover", "flaky"]:
        {"select": select, "cover": cover_line, "flaky": flaky}[name]()
    sys.exit(done())
