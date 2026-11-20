#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-release/scripts/release.py skills/workflow-release/scripts/merge.py skills/workflow-release/scripts/wiki.py skills/workflow-docs/scripts/milestones.py
"""docs-gate-scope (DEL-5, DOC-19): merge.py's wiki gate refuses only on pages the goal changed and on stale generated blocks and
tables. A DOC-19 or DOC-4 finding on a page the goal leaves alone is printed as a FINDING and filed once as an issue on that
feature's "Backlog: X" milestone (never twice while one is open). A link to the repo's own published sites (public_origins in
.loop/config.json or scripts/public-origins.json) or its own README is not a LINKS finding; every other outside link still is.

Builds a throwaway repo with a goal branch, and fakes gh by replacing merge.run. usage: test-docs-gate-scope.py"""
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(root, "skills", "workflow-release", "scripts"))
sys.path.insert(0, os.path.join(root, "skills", "workflow-docs", "scripts"))
os.environ["LOOP_ROLE"] = "worker"
import merge  # noqa: E402
import milestones  # noqa: E402
import release  # noqa: E402
import wiki  # noqa: E402

fails = 0


def check(name, ok, extra=""):
    global fails
    print(("PASS: " if ok else "FAIL: ") + name + ("" if ok else "  " + extra))
    fails += 0 if ok else 1


def git(*args):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "core.autocrlf=false"] + list(args),
                          cwd=repo, capture_output=True, text=True)


def write(path, text):
    full = os.path.join(repo, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", newline="\n") as handle:
        handle.write(text)


def commit(message):
    git("add", "-A")
    git("commit", "-q", "-m", message)


LINES = [
    "LINKS B: DOC-19 line 3 holds 'https://example.org/x', outside this repo. Fix: say it in words",
    "HOME Home: DOC-4 no system diagram. Fix: add a diagram block",
    "HOWTO How-to-use-A: DOC-19 the System diagram has no box for 'Command: a.py'. Fix: add it",
    "LINKS skills/x/SKILL.md: DOC-19 line 2 holds 'https://example.org/y', outside this repo. Fix: say it in words",
]
GENERATED = [
    "REWRITE Tests: STALE 1 commits since the page: abc123 a change",
    "WOULD FIX docs/wiki/Tests.md: re-render the Tests table",
    "WOULD FIX START.md: regenerate it (entry.py write)",
    "REWRITE A: STALE 1 commits since the page: abc123 a change",
    "HOWTO How-to-use-A: DOC-18 the title is '# How to use A'. Fix: use that title",
]
PAGE = "<!-- workflow-docs -->" + chr(10) + "# %s" + chr(10) + "The goal changed this page." + chr(10)
repo = tempfile.mkdtemp(prefix="docs-gate-scope-")
git("init", "-q", "-b", "main")
write(".loop/config.json", "{}\n")
write(".loop/docs.tsv", "A\ta.txt\n")
write("a.txt", "one\n")
for name in ("A", "B", "Home", "How-to-use-A"):
    write("docs/wiki/%s.md" % name, "<!-- workflow-docs -->\n# %s\nText.\n" % name)
write("skills/x/SKILL.md", "A skill doc.\n")
commit("pages")
git("update-ref", "refs/remotes/origin/main", "main")
git("checkout", "-q", "-b", "goal")
write("c.txt", "the goal's own work\n")
commit("the goal adds c.txt, no wiki page")


def gate(lines, filer=None):
    said, filed = io.StringIO(), []
    note = lambda top, page, texts: filed.append((page, list(texts))) or "filed " + page
    with contextlib.redirect_stdout(said):
        kept = release.untouched(repo, "origin/main", list(lines), filer or note)
    return kept, filed, said.getvalue()


kept, filed, said = gate(LINES)
check("a goal that changes no wiki page is not refused for DOC-19 or DOC-4 findings on other pages (kept: %s)" % kept, kept == [])
check("and each such page is filed once, by its own name: %s" % [p for p, _ in filed],
      sorted(p for p, _ in filed) == ["B", "Home", "How-to-use-A", "skills/x/SKILL.md"] and said.count("FINDING ") == 4)
check("and a page with several findings is one issue carrying them all",
      gate(LINES + [LINES[0].replace("line 3", "line 5")])[1][0] == ("B", [LINES[0], LINES[0].replace("line 3", "line 5")]))
kept, filed, said = gate(GENERATED + LINES[:0])
check("a stale generated block or table, a stale page and a DOC-18 line are still refused (kept: %d of %d)" % (len(kept), len(GENERATED)),
      kept == GENERATED and not filed)
# merge.py's apply re-renders other pages' Tests tables on the goal's branch; those pages are still not the goal's
write("docs/wiki/Home.md", "<!-- workflow-docs -->\n# Home\nText.\n## Tests\nre-rendered\n")
write("docs/wiki/How-to-use-A.md", "<!-- workflow-docs -->\n# How-to-use-A\nText.\n## Tests\nre-rendered\n")
commit("Wiki: re-render and re-stamp pages for goal")
kept, filed, said = gate(LINES)
check("a page only the loop's own re-render commit changed still counts as untouched, and is filed (kept: %s)" % kept,
      kept == [] and sorted(p for p, _ in filed) == ["B", "Home", "How-to-use-A", "skills/x/SKILL.md"])
write("docs/wiki/B.md", "<!-- workflow-docs -->\n# B\nThe goal changed this page.\n")
commit("the goal changes page B")
write("docs/wiki/Home.md", "<!-- workflow-docs -->\n# Home\nText.\n## Tests\nre-rendered again\n")
commit("Wiki: re-render and re-stamp pages for goal")
kept, filed, said = gate(LINES)
check("a finding on a page the goal changed is still refused (kept: %s)" % kept, kept == LINES[:1])
check("while the pages it left alone are filed (%s)" % [p for p, _ in filed], sorted(p for p, _ in filed) == ["Home", "How-to-use-A", "skills/x/SKILL.md"])
write("skills/x/SKILL.md", "A skill doc the goal edited.\n")
commit("the goal changes a skill doc")
check("a finding in a skill doc the goal changed is refused too", gate(LINES)[0] == [LINES[0], LINES[3]])
write("docs/wiki/Café.md", PAGE % "Café")
commit("the goal adds a page with a non-ASCII name")
cafe = "LINKS Café: DOC-19 line 2 holds 'https://evil.io', outside this repo. Fix: say it in words"
check("a finding on a changed page with a non-ASCII name is refused, not read as untouched", gate(LINES + [cafe])[0] == [LINES[0], LINES[3], cafe])
write("docs/wiki/A.md", PAGE % "A")
commit("the goal changes feature page A")
check("a How-to-use finding is refused when the goal changed its feature page", LINES[2] in gate(LINES)[0])
git("checkout", "-q", "main")
kept, filed, said = gate(LINES)
check("on the base branch itself every finding still counts and nothing is filed (kept: %d)" % len(kept), kept == LINES and not filed)
git("checkout", "-q", "goal")

# wiki.pending asks release.untouched, and prepare (no filer) prints the finding as left for health
saved = release.docs_trouble
release.docs_trouble = lambda *a, **k: list(LINES + GENERATED[3:4])
out = io.StringIO()
with contextlib.redirect_stdout(out):
    lines = wiki.pending(repo, {})
release.docs_trouble = saved
check("wiki.pending keeps only what the goal changed or generated (%s)" % lines,
      [l.split(":")[0] for l in lines] == ["LINKS B", "HOWTO How-to-use-A", "LINKS skills/x/SKILL.md", "REWRITE A"])
check("and prints the other findings as left for health when no filer is given", "FINDING Home: not touched by this goal; left for health" in out.getvalue())


# the issue: one per page, none while one is open, on the feature's backlog milestone
class Done:
    def __init__(self, out="", code=0):
        self.stdout, self.returncode = out, code


def fake(open_titles, fail=False, list_fails=False):
    calls = []

    def run(args, cwd=None, **kw):
        calls.append(args)
        if fail or (list_fails and args[:3] == ["gh", "issue", "list"]):
            return Done("", 1)
        if args[:3] == ["gh", "issue", "list"]:
            return Done("\n".join(open_titles))
        if args[:3] == ["gh", "issue", "create"]:
            return Done("https://github.com/o/r/issues/77\n")
        return Done("")
    return calls, run


real = merge.run
title = "Docs: How-to-use-Release has DOC-19/DOC-4 findings"
calls, merge.run = fake([])
said = merge.file_issue(repo, "How-to-use-Release", ["a", "b"])
made = [c for c in calls if c[:3] == ["gh", "issue", "create"]]
check("an untouched How-to-use page opens one issue on its feature's Backlog milestone (%s)" % said,
      len(made) == 1 and made[0][made[0].index("--milestone") + 1] == "Backlog: Release" and made[0][made[0].index("--title") + 1] == title
      and "filed https://github.com/o/r/issues/77" == said and any(c[:4] == ["gh", "api", "-X", "POST"] for c in calls))
calls, merge.run = fake([title, "another"])
said = merge.file_issue(repo, "How-to-use-Release", ["a"])
check("no second issue is opened while one is open (%s)" % said, not [c for c in calls if c[:3] == ["gh", "issue", "create"]] and "open" in said)
calls, merge.run = fake([])
merge.file_issue(repo, "Home", ["a"])
merge.file_issue(repo, "skills/x/SKILL.md", ["a"])
mine = [c[c.index("--milestone") + 1] for c in calls if c[:3] == ["gh", "issue", "create"]]
check("Home and a skill doc go on the Documentation backlog (%s)" % mine, mine == ["Backlog: Documentation"] * 2)
calls, merge.run = fake([title], list_fails=True)
said = merge.file_issue(repo, "How-to-use-Release", ["a"])
check("an issue list that fails opens no issue, so a later create cannot double one (%s)" % said, not [c for c in calls if c[:3] == ["gh", "issue", "create"]])
calls, merge.run = fake([], fail=True)
check("a gh that fails files nothing and never raises", merge.file_issue(repo, "Home", ["a"]) == "no issue filed (gh)")


def boom(args, cwd=None, **kw):
    raise OSError("no gh")


merge.run = boom
check("a missing gh files nothing and never raises", merge.file_issue(repo, "Home", ["a"]) == "no issue filed (gh)")
merge.run = real

# a repo's own published sites and its README are inside the repo
page = "Demo: https://demo.example.org/app and https://demo.example.org#top and https://github.com/me/proj#install and " \
       "https://github.com/me/proj/blob/main/README.md#usage and https://github.com/me/proj/."
sites = ("https://demo.example.org",)
check("a link to the repo's own published site or its README is not a LINKS finding",
      milestones.stands_alone("P", page, "me/proj", sites) == [])
check("negative control: the same page without the site listed reports the site links",
      len(milestones.stands_alone("P", page, "me/proj")) == 2)
check("negative control: another host, a lookalike host and another repo's README still fail",
      len(milestones.stands_alone("P", "https://demo.example.org.evil.io/x https://substack.com/p https://github.com/other/r#readme", "me/proj", sites)) == 3)
check("negative control: this repo's issue, pull and source links still fail",
      len(milestones.stands_alone("P", "https://github.com/me/proj/issues/3 https://github.com/me/proj/blob/main/src/a.py", "me/proj", sites)) == 2)
check("no listed site and no repo: nothing changes", milestones.origins(repo) == ())
write(".loop/config.json", json.dumps({"public_origins": ["https://demo.example.org/", 5, "http://plain.example.org"]}))
check("public_origins in .loop/config.json lists the sites (https only, no trailing slash)", milestones.origins(repo) == ("https://demo.example.org",))
write("scripts/public-origins.json", json.dumps(["https://a.example.org"]))
check("scripts/public-origins.json adds its list", milestones.origins(repo) == ("https://demo.example.org", "https://a.example.org"))
write("scripts/public-origins.json", json.dumps({"origins": ["https://b.example.org"]}))
check("and an {\"origins\": [...]} object works too", milestones.origins(repo) == ("https://demo.example.org", "https://b.example.org"))
write("scripts/public-origins.json", "not json")
check("a broken origins file is ignored, not an error", milestones.origins(repo) == ("https://demo.example.org",))
write("docs/wiki/B.md", "<!-- workflow-docs -->\n# B\nSee https://demo.example.org/app and https://other.example.org/z .\n")
found = [f for f in milestones.alone(repo, "docs/wiki", "me/proj") if f[0] == "LINKS"]
check("alone reads the repo's sites: the listed one passes, the other is reported (%s)" % [d[:60] for _, _, d in found],
      len(found) == 1 and "other.example.org" in found[0][2])
BT = chr(96)
here = ("https://demo.example.org", "https://demo.example.org/app")
for text in ("[a link](https://demo.example.org/app)", "See " + BT + "https://demo.example.org" + BT + ".", "Open (" + BT + "https://demo.example.org/app" + BT + "), then.", "Say 'https://demo.example.org'."):
    check("a listed origin followed by ), a backtick, a quote or a full stop passes: %s" % text, milestones.stands_alone("P", text, "me/proj", here) == [])
check("and an unlisted origin in a link or backticks is still reported",
      len(milestones.stands_alone("P", "[x](https://other.example.org/z) " + BT + "https://evil.example.org" + BT + ".", "me/proj", here)) == 2)
print("PASS: merge.py's wiki gate refuses only for pages the goal changed" if not fails else "FAILED %d" % fails)
sys.exit(1 if fails else 0)
