#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-health/scripts/health.py skills/workflow-health/scripts/table.py skills/workflow-health/scripts/file.py
# reads: skills/workflow-health/scripts/issues.py skills/workflow-health/scripts/report.py skills/workflow-health/scripts/automation.py
# reads: dev/toy/fakegh/fake.py
"""HLT-3 and HLT-4 (issue 4658): the findings table, and every filed issue tagged with its feature or Other.

A throwaway repo with findings in four groups (requirements, docs, freshness's issue read, size) and the fake gh
(dev/toy/fakegh/fake.py, called in place of gh, so it runs on Windows too). check prints one FINDINGS table with the
feature, group, rule, severity, finding and issue columns, every row a docs.tsv page or Other; file, with feature_labels
false, tags each issue feature:<Page> or feature:Other and prints the table again naming the issues it filed; the digest
(dry run) shows that same table. usage: test-health-table.py [--table|--labels] (one half only)"""
import contextlib
import io
import json
import os
import re
import runpy
import subprocess
import sys
import tempfile

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(here, "..", ".."))
scripts = os.path.join(root, "skills", "workflow-health", "scripts")
fake = os.path.join(here, "fakegh", "fake.py")
failed, calls, real_run = [], [], subprocess.run
COLUMNS = "| Feature | Group | Rule | Severity | Finding | Issue |"


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def gh(argv, **kw):
    args, i = [], 1
    while i < len(argv):
        if argv[i] == "--body-file":
            with open(argv[i + 1], encoding="utf-8") as f:
                args += ["--body", f.read().rstrip(chr(10))]
            i += 2
        else:
            args.append(argv[i])
            i += 1
    calls.append(" ".join(args))
    kw.pop("capture_output", None)
    kw.pop("text", None)
    return real_run([sys.executable, fake] + args, capture_output=True, text=True, **kw)


def patched(argv, *a, **kw):
    return gh(argv, **kw) if argv and argv[0] == "gh" else real_run(argv, *a, **kw)


def git(*args):
    real_run(("git",) + args, check=True, capture_output=True, text=True)


def run_script(repo, name, *args):
    """A health script in REPO, in this process (so its gh calls reach `patched`); its stdout."""
    out = io.StringIO()
    sys.argv, sys.path[:0] = [os.path.join(scripts, name)] + list(args), [scripts]
    for mod in ("health", "file", "issues", "report", "defects", "groups", "table", "rules", "automation", "rounds", "workflows"):
        sys.modules.pop(mod, None)
    os.chdir(repo)
    with contextlib.redirect_stdout(out):
        try:
            runpy.run_path(sys.argv[0], run_name="__main__")
        except SystemExit:
            pass
    sys.path.pop(0)
    os.chdir(here)
    return out.getvalue()


def rows_of(text):
    """The rows of the last findings table in TEXT."""
    block = text.split("FINDINGS (")[-1] if "FINDINGS (" in text else ""
    return [line for line in block.splitlines() if line.startswith("| ") and line != COLUMNS]


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="\n") as f:
        f.write(text)


subprocess.run = patched
only = sys.argv[1] if len(sys.argv) > 1 else ""
os.environ.pop("LOOP_HEALTH_GH_FIXTURE", None)
os.environ.pop("GH_TOKEN", None)
os.environ.pop("GITHUB_TOKEN", None)
with tempfile.TemporaryDirectory() as tmp:
    repo, d = os.path.join(tmp, "repo"), os.path.join(tmp, "gh")
    os.makedirs(d)
    os.environ.update(FAKE_GH_DIR=d, LOOP_HEALTH=os.path.join(tmp, "none.json"))
    write(os.path.join(repo, ".loop", "config.json"), json.dumps({"base": "main", "feature_labels": False}))
    write(os.path.join(repo, ".loop", "docs.tsv"), "Calc\tskills/calc\nGhost\tghost.py\nHome\tREADME.md\n")
    write(os.path.join(repo, "docs", "wiki", "Calc.md"),
          "<!-- workflow-docs -->\n# Calc\n\n## Summary\n\nCalc adds numbers.\n\n## Criteria\n\n- REL-1: **Reviewed 2026-01-01** calc adds.\n")
    write(os.path.join(repo, "skills", "calc", "scripts", "near.py"), "# pad\n" * 3400)
    write(os.path.join(repo, "skills", "x", "scripts", "near.py"), "# pad\n" * 3400)
    git("init", "-q", "-b", "main", repo)
    for key, value in (("user.email", "t@example.test"), ("user.name", "t"), ("core.autocrlf", "false")):
        git("-C", repo, "config", key, value)
    git("-C", repo, "add", "-A")
    git("-C", repo, "commit", "-qm", "Findings in several groups")
    groups = "requirements,docs,freshness,size"

    if only != "--labels":
        out = run_script(repo, "health.py", "check", "--group", groups)
        print(out)
        lines = out.splitlines()
        rows = rows_of(out)
        check(sum(1 for l in lines if l.startswith("FINDINGS")) == 1 and COLUMNS in lines,
              "one FINDINGS table with the feature, group, rule, severity, finding and issue columns")
        heads = [n for n, l in enumerate(lines) if l.startswith("== ")]
        check(lines[1].startswith("groups run: ") and heads and lines.index(COLUMNS) < heads[0], "the table follows the header, before the groups")
        cells = [[c.strip() for c in r.strip("|").split(" | ")] for r in rows]
        check(len({c[1] for c in cells}) >= 3, "findings from at least three groups in the one table (%s)" % sorted({c[1] for c in cells}))
        check(cells and all(c[0] in ("Calc", "Ghost", "Other") for c in cells), "every row names a feature page or Other")
        check(any(c[0] == "Calc" and c[1] == "Size" and "calc" in c[4] for c in cells)
              and any(c[0] == "Other" and c[1] == "Size" and "x" in c[4] for c in cells), "a finding about a page names it, one about none says Other")
        bad = [l for l in lines if re.match(r"^(WARN|FAIL|UNREAD) ", l)]
        check(len(rows) == len(bad), "one row per WARN, FAIL and UNREAD finding (%d rows, %d findings)" % (len(rows), len(bad)))
        check(all(len(c) == 6 and c[5] for c in cells), "every row has all six cells")

    if only != "--table":
        before = run_script(repo, "health.py", "check", "--group", groups)  # the tick: check, then file, one report
        calls.clear()
        filed = run_script(repo, "health.py", "file", "--group", "size,docs")
        print(filed)
        made = [c for c in calls if c.startswith("label create feature:")]
        created = [c for c in calls if c.startswith("issue create")]
        check(any("feature:Calc " in c for c in made) and any("feature:Other " in c for c in made), "both feature labels are made first, with feature_labels false")
        check(created and all("--label feature:" in c for c in created), "every filed issue carries a feature label (%d filed)" % len(created))
        check(any("calc" in c and "--label feature:Calc" in c for c in created) and any("--label feature:Other" in c for c in created),
              "a Calc finding is tagged feature:Calc, one about no page feature:Other")
        cells = [[c.strip() for c in r.strip("|").split(" | ")] for r in rows_of(filed)]
        check(cells and all(re.fullmatch(r"#\d+", c[5]) for c in cells if c[1] in ("Size", "Docs")), "file's table names the issue it filed for each finding")
        report = os.path.join(tmp, "report.txt")
        write(report, before + "\n" + filed)
        os.environ["HEALTH_REPORT"] = report
        digest = run_script(repo, "automation.py", "digest")
        os.environ.pop("HEALTH_REPORT")
        print(digest)
        split = lambda r: r.rstrip(" |").rpartition(" | ")[::2]  # noqa: E731  (row without its Issue cell, the Issue cell)
        issue = dict(split(r) for r in rows_of(filed))
        want = ["%s | %s |" % (split(r)[0], issue.get(split(r)[0], split(r)[1])) for r in rows_of(before)]
        check("### Findings" in digest.splitlines() and rows_of(digest) == want and len(want) > len(rows_of(filed))
              and any(r.endswith("| not filed |") and "| Requirements |" in r for r in want),
              "the digest shows the same table: check's, every group kept, with the issues file just filed")


    os.chdir(here)
subprocess.run = real_run
if not failed:
    print("PASS: health-table: every finding in one feature table, every issue tagged")
sys.exit(1 if failed else 0)
