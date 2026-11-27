#!/usr/bin/env python3
# reads: skills/workflow-regression/scripts/regression.py dev/toy/lvl_fixture.py
"""v110-lvl-relevel lines 3 and 4: the one re-levelling keeps every row with one level, its old word and a reason, and
L0 times adding to over 45 seconds are refused with the total. The L0, nightly, covered and defect rules, offline."""
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.dont_write_bytecode = True
from lvl_fixture import REG, Repo, check, done, row  # noqa: E402


def fixture():
    rows = [row("fast", command="test -f data/a"), row("fast2", command="test -f data/b"),
            row("netword", command="curl -s example.test"), row("toyword", command="git init x"),
            row("opaque", command='bash "$SCRIPT"'), row("deep", command="bash dev/d1.sh"),
            row("shallow", command="bash dev/s1.sh"), row("slow", command="test -f data/c"),
            row("notime", command="test -f data/d"), row("skipped-here", command="test -f data/e"),
            row("known-red", command="test -f data/f"), row("guard", command="test -f data/g", goal="GRD-6.1"),
            row("n-fits", level="nightly"), row("n-marked", level="nightly"), row("n-cut", level="nightly"),
            row("n-own-limit", level="nightly"), row("n-unmeasured", level="nightly"),
            row("done-c", level="covered", command="by fast and n-marked"),
            row("done-d", level="covered", command="by guard"),
            row("bug-pull", category="defect", link="https://github.com/o/r/pull/5"),
            row("bug-finding", category="defect", link="finding:flaky-thing"),
            row("bug-bare", category="defect", link="#7"),
            row("bug-two", category="defect",
                link="[#8](https://github.com/o/r/issues/8); https://github.com/o/r/issues/5")]
    rows += [row("bulk%02d" % i, command="test -f data/bulk%d" % i) for i in range(12)]
    repo = Repo(rows, None, ["requirement\tGRD-6\tsecurity\tfixture", "label\tsecurity\tsecurity\tfixture",
                             "label\tprivate\tprivate\tfixture", "label\tprivacy\tprivate\tfixture"])
    for name, text in {"dev/s1.sh": "bash dev/s2.sh\n", "dev/s2.sh": "bash dev/s3.sh\n", "dev/s3.sh": "true\n",
                       "dev/d1.sh": "bash dev/d2.sh\n", "dev/d2.sh": "bash dev/d3.sh\n", "dev/d3.sh": "bash dev/d4.sh\n",
                       "dev/d4.sh": "true\n"}.items():
        repo.write(name, text)
    times = {"fast": 0.2, "fast2": 0.3, "netword": 0.1, "toyword": 0.1, "opaque": 0.1, "deep": 0.1, "shallow": 0.1,
             "slow": 7.0, "skipped-here": 0.2, "known-red": 0.2, "guard": 0.1, "n-fits": 100, "n-marked": 3,
             "n-cut": 300, "n-own-limit": 500}
    times.update(("bulk%02d" % i, 4.9) for i in range(12))
    repo.write("times.tsv", "".join("%s\t%s\n" % kv for kv in times.items()))
    repo.write(".loop/regression-limits.tsv", "n-marked\tnightly\twhy\nn-own-limit\t600\twhy\n")
    repo.write(".loop/regression-skips.tsv", "skipped-here\tmac only\n")
    repo.write(".loop/regression-known.tsv", "known-red\twhy\n")
    repo.write(".loop/regression-relevel-input.tsv", "done-c\tfast,n-marked\ndone-d\tguard\nbug-bare\town 7\n")
    repo.commit()
    repo.labels({"repos/o/r/issues/5": ["security-fix"], "repos/o/r/issues/8": ["PRIVACY", "bug"],
                 "repos/{owner}/{repo}/issues/7": ["bug"]})
    return repo


ARGS = ("relevel", "--times", "times.tsv", "--row-limit", "300")
repo = fixture()
table = repo.read(".loop/regression.tsv")
status, said = repo.run(*ARGS, "--dry-run")
check(status == 0 and repo.read(".loop/regression-relevel.tsv") is None and "DRY RUN" in said, "a dry run writes nothing",
      said)
status, said = repo.run(*ARGS)
got, rows = repo.entries(), repo.rows()
status2, said2 = repo.run("levels", "--check")
check(status == 0 and status2 == 0 and "valid" in said2, "relevel writes a valid record", said + said2)
check(list(got) == list(rows) and repo.read(".loop/regression.tsv") == table,
      "every row keeps one entry, in table order, and the table is unchanged", said)
check(bool(got) and all(e["level"] in ("L0", "L1", "L2") and e["old"] == rows[k]["level"] and e["reason"]
                        for k, e in got.items()), "each entry has one level from L0 to L2, the old word and a reason")


def level(key):
    return got.get(key, {}).get("level"), got.get(key, {}).get("risk")


check(level("fast")[0] == "L0" and level("fast2")[0] == "L0" and level("shallow")[0] == "L0",
      "a fast row with no network or toy repository, scripts followed three deep, is L0", said)
for key, why in (("netword", "a network word"), ("toyword", "a toy repository"), ("opaque", "a call that can't be followed"),
                 ("deep", "a script four deep"), ("slow", "5 seconds or more"), ("notime", "no measured time"),
                 ("skipped-here", "a skip-list time"), ("known-red", "a known-red time"), ("guard", "a tagged row")):
    check(level(key)[0] == "L1", "%s keeps %s at L1" % (why, key), "%s\n%s" % (level(key), said))
zero = [e for e in got.values() if e["level"] == "L0"]
total = sum(float(e["seconds"] or 0) for e in zero)
check(zero and total <= 45 and len([e for e in zero if e["id"].startswith("bulk")]) == 9,
      "L0 takes the fastest rows while the total stays at 45 s or less", "%s %s" % (total, said))
check([level(k)[0] for k in ("n-fits", "n-marked", "n-cut", "n-own-limit", "n-unmeasured")] ==
      ["L1", "L2", "L2", "L1", "L1"], "nightly: L2 when marked or cut at its limit, else L1", said)
check(level("done-c")[0] == "L2" and level("done-d") == ("L1", "none"), "a covered row takes its covers' highest level",
      said)
check(level("bug-pull") == ("L1", "security") and "repos/o/r/issues/5" in repo.calls(),
      "a pull request address is read like an issue address", repo.calls())
check(level("bug-two") == ("L1", "private") and level("bug-bare")[1] == "none" and level("bug-finding")[1] == "none",
      "every link is read, the strongest tag wins; own numbers read this repository; a finding reads nothing", said)
check(repo.calls().count("repos/o/r/issues/5") == 2, "one read per address in a run (dry run and run: two)", repo.calls())
written = (repo.read(".loop/regression-relevel.tsv") or "") + (repo.read(".loop/regression-risk.tsv") or "")
check(written and "github.com" not in written and "o/r" not in written and "security-fix" not in written,
      "no link, repository name or label text is written")

# done line 4: more than 45 L0 seconds is refused with the total
lines = (repo.read(".loop/regression-relevel.tsv") or "").split("\n")
lines = ["\t".join(c[:5] + ["4.9"] + c[6:]) if len(c) == 8 and c[0].startswith("bulk") and c[2] == "L0" else
         "\t".join(c) for c in (x.split("\t") for x in lines)]
repo.write(".loop/regression-relevel.tsv", "\n".join(lines).replace("\t4.9\t", "\t6.0\t"))
status, said = repo.run("levels", "--check")
status2, said2 = repo.run("run", "fast")
check(status == 2 and "LEVELS_L0_OVER" in said and "add up to 5" in said and status2 == 2,
      "L0 times over 45 seconds are refused, naming the total", said)
repo.git("checkout", "-q", "--", ".")
repo.close()

# a later run fills only what is missing, and never gives L0
repo = fixture()
repo.run(*ARGS)
repo.commit("levelled")
first = repo.entries()
repo.table(list(repo.rows().values()) + [row("later", command="test -f data/z")])
repo.write("times.tsv", (repo.read("times.tsv") or "") + "later\t0.1\n")
status, said = repo.run(*ARGS)
got = repo.entries()
check(status == 0 and got.get("later", {}).get("level") == "L1" and all(got.get(k) == v for k, v in first.items()),
      "a second relevel fills only the missing row, at L1", said)
repo.close()

# defect evidence that can't be read: every failure listed at once, nothing written, no address printed
for answers, why in (({"error": "HTTP 404: Not Found"}, "not found"),
                     ({"error": "HTTP 401: Bad credentials; try gh auth login"}, "not signed in"),
                     ({"error": "HTTP 403: API rate limit exceeded"}, "rate limited"),
                     ({"error": "HTTP 403: Resource not accessible"}, "no access"),
                     ({"error": "something odd"}, "unreadable answer")):
    repo = fixture()
    repo.labels({"repos/o/r/issues/5": answers, "repos/o/r/issues/8": answers})
    before = repo.snapshot()
    status, said = repo.run(*ARGS)
    check(status != 0 and why in said and "bug-pull" in said and "bug-two" in said and repo.snapshot() == before
          and "github.com" not in said, "%s: both defect rows listed, nothing written" % why, said)
    repo.close()
repo = fixture()
tools = os.path.join(repo.top, "tools")
os.mkdir(tools)
for name in ("git", "sh"):
    os.symlink(shutil.which(name), os.path.join(tools, name))
status, said = repo.run(*ARGS, PATH=tools)
check(status != 0 and "no gh tool" in said, "no gh tool is told apart", said)
repo.labels({})
status, said = repo.run(*ARGS, "--risk-for", "bug-pull=security", "--risk-for", "bug-two=none", "--risk-for",
                        "bug-bare=private")
check(status != 0 and "LEVELS_NEEDS_OWNER" in said and repo.read(".loop/regression-relevel.tsv") is None,
      "--risk-for none needs an owner record; nothing partial is written", said)
status, said = repo.run(*ARGS, "--risk-for", "bug-pull=security", "--risk-for", "bug-two=private", "--risk-for",
                        "bug-bare=private")
got = repo.entries()
check(status == 0 and got.get("bug-pull", {}).get("risk") == "security" and
      "given\tbug-two\tprivate\tgiven with --risk-for" in (repo.read(".loop/regression-risk.tsv") or ""),
      "--risk-for raises without an owner record and pins the tag", said)
repo.close()

repo = Repo([row("a")], None, None)
repo.commit()
status, said = repo.run("relevel")
check(status != 0 and "regression-risk.tsv" in said and "--times" in said and "--row-limit" in said,
      "every missing prerequisite is listed at once", said)
repo.close()
sys.exit(done())
