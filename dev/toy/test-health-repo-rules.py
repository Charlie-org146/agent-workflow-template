#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-health/scripts/health.py skills/workflow-health/scripts/enforce.py skills/workflow-health/scripts/controls.py
# reads: skills/workflow-health/scripts/report.py skills/workflow-health/scripts/rules.py skills/workflow-health/scripts/defects.py
# reads: skills/workflow-setup/scripts/settings.py
"""HLT repo rules: a repo extends health with .loop/health-rules.json, sets default thresholds and turns a default rule off.

Each case builds a throwaway git repo, writes the repo's own rules and runs the real health.py (and settings.py) on it:
run (rows land in their group with their feature), control (a rule's break makes Controls see it fail), refuse (a rule with
no break exits 2), off (a default turned off shows its reason, one without a reason stays on and is UNREAD), setup (fill-repo
writes the file once and keeps an edited one). usage: test-health-repo-rules.py [CASE ...] [--break]
CASE is one of run, control, refuse, off, retired,
long-skill, long-skill-4171, long-skill-3983, long-skill-3815, long-skill-1403 or setup (default all). --break leaves the rules file out of every repo, to see the rows red."""
import json
import os
import subprocess
import sys
import tempfile

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(here, "..", ".."))
health = os.path.join(root, "skills", "workflow-health", "scripts", "health.py")
settings = os.path.join(root, "skills", "workflow-setup", "scripts", "settings.py")
breaking = "--break" in sys.argv
cases = [a for a in sys.argv[1:] if not a.startswith("--")]
run_it = lambda name: not cases or name in cases
py = sys.executable
failed = []
ENV = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1", GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid",
           GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.invalid", LOOP_HEALTH=os.devnull, HOME=tempfile.gettempdir(), USERPROFILE=tempfile.gettempdir())


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def sh(args, cwd):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, env=ENV, timeout=300)


def repo(folder, rules=None, off=None, config=None):
    sh(["git", "init", "-q", "-b", "main"], folder)
    for rel, text in {".loop/config.json": json.dumps(dict({"base": "main"}, **(config or {}))),
                      ".loop/regression.tsv": "# id\tlevel\tcommand\n", "flag": "1"}.items():
        os.makedirs(os.path.dirname(os.path.join(folder, rel)), exist_ok=True)
        with open(os.path.join(folder, rel), "w") as handle:
            handle.write(text)
    if (rules is not None or off is not None) and not breaking:
        with open(os.path.join(folder, ".loop", "health-rules.json"), "w") as handle:
            json.dump({"rules": rules or [], "off": off or {}}, handle)
    sh(["git", "add", "-A"], folder)
    sh(["git", "commit", "-q", "-m", "toy"], folder)


def words(code):
    return [py, "-c", code]


def rule(name, group, code, brk="pass", **more):
    return dict({"name": name, "group": group, "command": words(code), "fix": "fix " + name, "break": words(brk)}, **more)


def rows(folder, groups):
    done = sh([py, health, "check", "--json", "--group", groups], folder)
    try:
        return json.loads(done.stdout)["rows"], done
    except ValueError:
        return [], done


def find(found, name):
    return next((r for r in found if r["subject"] == name or r["rule"] == name), None)


with tempfile.TemporaryDirectory() as tmp:
    if run_it('run'):
        # run: one rule per state, in a default group and in the repo group, each with its feature
        a = os.path.join(tmp, "a")
        os.makedirs(a)
        repo(a, [rule("r-pass", "docs", "print('fine')", feature="Docs"), rule("r-warn", "repo", "import sys;sys.exit(2)", feature="Health"),
                 rule("r-fail", "security", "import sys;sys.exit(1)", feature="Health"), rule("r-unread", "hygiene", "import sys;sys.exit(7)")])
        found, _ = rows(a, "docs,security,hygiene,repo")
        got = {n: find(found, n) for n in ("r-pass", "r-warn", "r-fail", "r-unread")}
        check(all(got.values()) and [(got[n]["state"], got[n]["family"]) for n in got] ==
              [("PASS", "docs"), ("WARN", "repo"), ("FAIL", "security"), ("UNREAD", "hygiene")],
              "a repo rule runs in the report with its group and its exit as PASS, WARN, FAIL or UNREAD")
        check(bool(got["r-warn"]) and got["r-warn"].get("feature") == "Health" and got["r-pass"].get("feature") == "Docs",
              "a repo rule's row carries its feature")
        # refs: an id listed under a page's ### Retired resolves through its marker; an id no page defines or retires still fails
        r = os.path.join(tmp, "refs")
        os.makedirs(os.path.join(r, "docs", "wiki"))
        for name, body in (("One", "## Requirements\n\n- AB-1: **Unreviewed** Live.\n  - It lives.\n\n## Revisions\n\n### AB-1\n\n| rev | date | text | why | record |\n|---|---|---|---|---|\n| r1 | 2026-11-19 | Live <br> History names AB-7. | why | o1: \"x\" |\n\n### Retired\n\n- AB-3: moved to AB-1\n"),
                           ("Home", "# Home\n\n| Requirement | Text |\n|---|---|\n| AB-1 | the row names AB-8 |\n"),
                           ("Two", "## Requirements\n\n- AB-2: **Unreviewed** Also live. See AB-3 and AB-9.\n  - It lives.\n")):
            with open(os.path.join(r, "docs", "wiki", name + ".md"), "w") as handle:
                handle.write("# %s\n\n%s" % (name, body))
        repo(r)
        found, _ = rows(r, "consistency")
        dangling = {x["subject"] for x in found if x["rule"] == "refs" and x["state"] == "FAIL"}
        check("AB-3" not in dangling and "AB-9" in dangling,
              "a retired id resolves through its moved-to marker, and an id no page defines or retires still fails refs")
        check("AB-7" not in dangling and "AB-8" in dangling,
              "an id only in a Revisions row (history) passes refs, and an id in a Home row still fails")
    if run_it('control'):
        # control: the break runs on a copy, and the control fires only when the command then fails
        b = os.path.join(tmp, "b")
        os.makedirs(b)
        repo(b, [rule("works", "repo", "import os,sys;sys.exit(0 if os.path.exists('flag') else 1)", "import os;os.remove('flag')"),
                 rule("noop", "repo", "print('ok')", "pass")])
        found, _ = rows(b, "controls")
        works, noop = find(found, "works"), find(found, "noop")
        check(bool(works) and works["state"] == "PASS" and bool(noop) and noop["state"] == "FAIL" and "cannot fire" in noop["detail"],
              "a rule whose break makes it fail passes its control; one whose break changes nothing is reported as unable to fire")
        check(os.path.exists(os.path.join(b, "flag")), "the break ran on a copy: the repo's own files are untouched")
    if run_it('refuse'):
        # refuse: no break
        c = os.path.join(tmp, "c")
        os.makedirs(c)
        repo(c, [dict(rule("nobreak", "repo", "pass"), **{"break": None})])
        done = sh([py, health, "check", "--group", "repo"], c)
        check(done.returncode == 2 and "nobreak" in done.stdout and "no break command" in done.stdout,
              "a repo rule with no break makes health refuse (exit 2) naming the rule")
    if run_it('off'):
        # off: a default turned off shows its reason; an empty reason leaves the rule on and is UNREAD
        d = os.path.join(tmp, "d")
        os.makedirs(d)
        repo(d, [], off={"hooks": "CI runs no git hooks", "nightly": ""})
        found, _ = rows(d, "security,freshness,repo")
        off = find(found, "hooks")
        check(bool(off) and off["state"] == "INFO" and off["family"] == "security" and "turned off: CI runs no git hooks" in off["detail"],
              "a default rule turned off prints its reason in its own group")
        bare = find(found, "nightly")
        check(any(r["state"] == "UNREAD" and r["subject"] == "nightly" and r["family"] == "repo" for r in found) and bool(bare) and bare["family"] == "freshness",
              "a default turned off with no reason stays on and is reported UNREAD")
    if run_it('retired'):
        # retired (principle 5, o988): an off entry naming a retired rule is INFO, never UNREAD; unknown and malformed stay UNREAD
        g = os.path.join(tmp, "g")
        os.makedirs(g)
        repo(g, [], off={"scripts": "old", "rows-cap": "", "nosuch": "x", "hooks": 5})
        found, _ = rows(g, "security,size,repo")
        ret = [r for r in found if r["subject"] in ("scripts", "rows-cap")]
        check(len(ret) == 2 and all(r["state"] == "INFO" and "retired rule; nothing to turn off; the entry can go" in r["detail"] for r in ret),
              "an off entry naming a retired rule gives one INFO row, not UNREAD, with or without a reason")
        check(any(r["state"] == "UNREAD" and r["subject"] == "nosuch" for r in found) and any(r["state"] == "UNREAD" and r["subject"] == "hooks" for r in found),
              "an unknown or malformed off entry is still UNREAD")
        done = sh([py, os.path.join(root, "skills", "workflow-health", "scripts", "controls.py"), "run", "skill-lines"], root)
        check(done.returncode == 0 and done.stdout.count("\n") == 1 and "retired by principle 5" in done.stdout,
              "controls.py run on a retired rule prints one line and exits 0")
        done = sh([py, health, "check", "--group", "size"], g)
        check(done.returncode != 2 and "size: no rules (retired by principle 5)" in done.stdout and "PASS size" not in done.stdout,
              "--group size runs: the empty group says why and counts no passed check")
    # issues 4172, 4171, 3983, 3815 and 1403, as principle 5 settles them (o988): health once filed a size finding on each
    # skill's SKILL.md at that length; it files none
    for case, issue, skill, count in (("long-skill", "4172", "release", 150), ("long-skill-4171", "4171", "docs", 155),
                                      ("long-skill-3983", "3983", "regression", 151), ("long-skill-3815", "3815", "regression", 151),
                                      ("long-skill-1403", "1403", "docs", 155)):
        if not run_it(case):
            continue
        h = os.path.join(tmp, case)
        os.makedirs(h)
        repo(h)
        os.makedirs(os.path.join(h, "skills", "workflow-" + skill))
        with open(os.path.join(h, "skills", "workflow-" + skill, "SKILL.md"), "w") as handle:
            handle.write("line\n" * count)
        found, _ = rows(h, "size,security")
        check(bool(found), "health runs on a repo whose %s SKILL.md has %d lines" % (skill, count))
        check(bool(found) and not [r for r in found if r["rule"] == "skill-lines" or (r["family"] == "size" and r["state"] in ("FAIL", "WARN"))],
              "a %s SKILL.md of %d lines gets no size finding (issue %s)" % (skill, count, issue))
    if run_it('setup'):
        # setup: fill-repo writes the file once and keeps an edited one
        f = os.path.join(tmp, "f")
        os.makedirs(f)
        repo(f)
        sh([py, settings, "fill-repo", "--repo", f], f)
        target = os.path.join(f, ".loop", "health-rules.json")
        first = json.load(open(target)) if os.path.exists(target) else {}
        with open(target, "w") as handle:
            json.dump({"rules": [], "off": {"hooks": "kept"}}, handle)
        sh([py, settings, "fill-repo", "--repo", f], f)
        check(first.get("rules") == [] and first.get("off") == {} and "_comment" in first and json.load(open(target))["off"] == {"hooks": "kept"},
              "setup writes an empty commented .loop/health-rules.json once and keeps an edited one")
        held = json.load(open(os.path.join(f, ".loop", "config.json")))
        check(not {"health_script_bytes", "health_skill_lines"} & set(held), "setup writes neither retired size setting (o988)")

print("ALL PASS" if not failed else "%d FAILED" % len(failed))
sys.exit(1 if failed else 0)
