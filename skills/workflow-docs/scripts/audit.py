#!/usr/bin/env python3
"""The one docs command: check every required doc, fix what is mechanical, list the wording to rewrite.

usage: docs.py audit [--base REF] [--dry-run]

It checks the pages against the template sheet (references/template.md), the code (stale pages), the tests (the Tests
Tests, rows not
written as Given/When/Then, and which Reviewed requirements have no test or tests that no longer match), and the required docs (a release note per tag; a
milestone is optional and never checked). It fixes the mechanical trouble itself (the
Tests tables and the full Tests page) and prints the rest as REWRITE lines for a person or agent. It never
deletes a page and never changes a criterion's wording. --dry-run only says what it would fix. Exit 0 only when
nothing is left. UNTESTED lines are written to untested.tsv (id, reason) in the repo's .git/loop folder for the loop to queue goals from, and
do not fail the audit. It runs git and gh, and nothing else.
"""
import argparse
import contextlib
import io
import os
import re
import subprocess
import sys

import criteria
import docs
import entry

# No terminal, no waiting: a prompt from git or gh must fail, not block.
os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")
if not sys.stdin or not sys.stdin.isatty():
    os.dup2(os.open(os.devnull, os.O_RDONLY), 0)

REWRITE = {"CAP", "SCRIPT", "STALE", "UNWRITTEN", "PROBLEM", "SECTIONS", "CRITERION", "NONGOALS", "METRICS", "REVIEW", "SCENARIO", "FORMAT"}


def release_trouble(root):
    """A tag with neither a CHANGELOG section nor a GitHub release has no release note."""
    try:
        with open(os.path.join(root, "CHANGELOG.md")) as handle:
            notes = handle.read()
    except OSError:
        notes = ""
    out = []
    for tag in criteria.git("tag", "-l", "v*", check=False).split():
        if not re.search(r"^## \[?%s\b" % re.escape(tag), notes, re.M):
            have = subprocess.run(["gh", "release", "view", tag], cwd=root, capture_output=True, text=True)
            if have.returncode:
                out.append(("RELEASE", tag, "has no release note. Fix: add its CHANGELOG section or a GitHub release"))
    return out


def scenarios(root):
    """A row shown on a page whose description is not one Given/When/Then scenario."""
    shown = {name for names in list(criteria.test_rows(root)[0].values()) + list(criteria.defect_rows(root).values()) for name in names}
    return [("SCENARIO", "regression", "row %s: '%s' is not 'Given ..., when ..., then ...'. Fix: rewrite its description "
             "(column 6 of .loop/regression.tsv) as one scenario" % (row[0], row[5][:60])) for row in criteria.tsv(root, "regression.tsv")
            if row[0] in shown and not criteria.SCENARIO.match(row[5])]


def untested(root):
    """(id, reason) for each Reviewed requirement (its own line, or its page's PRD) with no test, or none that passed
    since its wording appeared."""
    linked, _ = criteria.test_rows(root)
    rows = {row[0]: row for row in criteria.tsv(root, "regression.tsv")}
    ran = {row[0]: row[2] for row in criteria.tsv(root, "regression-runs.tsv") if row[1] == "PASS"}
    out = []
    for rel in criteria.pages(root):
        with open(os.path.join(root, rel)) as handle:
            lines = handle.read().splitlines()
        signed = any(line.startswith("Review: **Reviewed ") for line in lines)
        for match in filter(None, (criteria.LINE.match(line) for line in lines)):
            key, text = match.group(1), match.group(4)
            if match.group(2) == "Unreviewed" and not signed:
                continue
            if not linked.get(key):
                out.append((key, "no test"))
                continue
            since = subprocess.run(["git", "log", "-1", "--format=%cs", "-S" + text, "--", rel], cwd=root,
                                   capture_output=True, text=True).stdout.strip()
            gone = [name for name in linked[key] if any(not os.path.exists(os.path.join(root, f))
                    for f in criteria.SCRIPT_FILE.findall(rows[name][2]))]
            if gone or not any(ran.get(name, "") >= since for name in linked[key]):
                out.append((key, "test no longer matches"))
    return out


def render(check):
    """Re-render the Tests tables (or only list the stale ones when check is true), as page paths."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        criteria.cmd_render(argparse.Namespace(check=check))
    return [line.split(" ", 1)[1] for line in out.getvalue().splitlines() if line.startswith(("STALE ", "WROTE "))]


def audit(root, base, dry):
    fix = not dry
    would = []
    if not docs.read_map(root):
        print("NO PAGES: run add first")
        return 1
    if config_criteria(root):
        would += ["%s: re-render the Tests table" % name for name in render(not fix)]
    found = []
    # The entry point and a stale agent block are generated: rewriting them is mechanical (a missing block needs agents.py).
    stale = [path for kind, path, why in entry.problems(root) if path == entry.ENTRY and kind in ("STALE", "MISSING") or
             kind == "STALE" and path in entry.agent_files(docs.config(root)) and "ENTRY_MARKER" not in why]
    if stale and fix:
        entry.write(root)
    would += ["%s: regenerate it (entry.py write)" % path for path in stale]
    for line in would:
        print("%s %s" % ("WOULD FIX" if dry else "FIXED", line))
    found += docs.problems(root, base) + docs.contract(root) + docs.counts(root) + release_trouble(root)
    found = [item for item in found if item[0] != "CHANGED"]  # kept for older pages; Usage is gone
    found += scenarios(root) if config_criteria(root) else []
    if dry:
        found = [item for item in found if item[0] != "TESTS" and item[:2] != ("STALE", "Tests")]  # render fixes these
    for kind, page, detail in found:
        print("%s %s: %s" % ("REWRITE" if kind in REWRITE else kind, page, "%s %s" % (kind, detail) if kind in REWRITE else detail))
    todo = untested(root) if config_criteria(root) else []
    for key, why in todo:
        print("UNTESTED %s: %s" % (key, why))
    if fix:
        with open(os.path.join(os.path.dirname(docs.state_file()), "untested.tsv"), "w") as handle:
            handle.writelines("%s\t%s\n" % item for item in todo)
    left = len(found) + (len(would) if dry else 0)
    print("DOCS OK: %d pages" % len(docs.read_map(root)) if not left else "DOCS: %d to do" % left)
    return 1 if left else 0


def config_criteria(root):
    return bool(docs.config(root).get("criteria"))


# check --own: a stale page the goal's own diff doesn't touch is a FINDING, not a failure.
import subprocess


def own_git(root, *args):
    out = subprocess.run(["git"] + list(args), cwd=root, capture_output=True, text=True)
    return out.stdout.strip() if out.returncode == 0 else None


def own_base(root, name):
    for ref in ("origin/" + name, name):
        if own_git(root, "rev-parse", "--verify", "-q", ref + "^{commit}"):
            return ref
    return None


def own_touched(root, ref, paths):
    """True when the goal's diff (merge-base of ref and HEAD, to HEAD) touches any of the page's mapped paths."""
    out = own_git(root, "diff", "--name-only", ref + "...HEAD", "--", *paths)
    return out is None or bool(out)  # no diff answer: judge the page as the goal's own


def own_split(root, found, notes, rows, name="main"):
    """(found, notes) with each STALE line of an untouched mapped page moved to notes as FINDING."""
    ref = own_base(root, name)
    if not ref or own_git(root, "merge-base", "--is-ancestor", "HEAD", ref) is not None:
        return found, notes  # no base, or on the base branch itself (main's own run keeps every STALE)
    keep, moved = [], []
    for item in found:
        if item[0] == "STALE" and item[1] in rows and item[2][:1].isdigit() and not own_touched(root, ref, rows[item[1]]):
            moved.append(("FINDING", "STALE " + item[1], item[2] + " (not touched by this goal; main's own, left for health)"))
        else:
            keep.append(item)
    return keep, notes + moved


SYNC_MARK = "<!-- prd-sync: owned -->"
REQ = re.compile(r"^(?:[-*]\s+|\d+[.)]\s+|\|\s*)?\**([A-Z]{2,5}-\d+)\**\s*[:|.–—-]*\s*(.*)$")


def req_key(ident):
    prefix, _, number = ident.partition("-")
    return prefix, int(number)


def requirements(body):
    """{id: text} of the requirements an external PRD states: a top-level bullet, numbered item or table row that starts
    with an id (`- XX-1: **Unreviewed** text`, `| XX-1 | text |`), its Reviewed stamp and markup dropped."""
    found = {}
    for line in body.replace("\r\n", "\n").split("\n"):
        match = REQ.match(line)
        if match and match.group(1) not in found:
            text = re.sub(r"\*\*(?:Un)?[Rr]eviewed[^*]*\*\*|<!--.*?-->|\*\*|`|\|", " ", match.group(2))
            found[match.group(1)] = " ".join(text.split())
    return found


def mirror_of(path):
    """({id: text}, owned) of the repo's copy of a PRD: owned is True when sync wrote it (it opens with SYNC_MARK) or
    nothing is there yet, False for any other file, which sync never touches."""
    try:
        with open(path, encoding="utf-8") as handle:
            lines = handle.read().replace("\r\n", "\n").split("\n")
    except OSError:
        return {}, True
    return {m.group(1): m.group(2) for m in (re.match(r"- ([A-Z]{2,5}-\d+): (.*)$", x) for x in lines) if m}, lines[0] == SYNC_MARK


def sync(root, dry=False, texts=None):
    """Compare each feature's external PRD with the repo's copy, .loop/prd/<Page>.md, and rewrite that copy to match
    (unless dry). It reads the source and never writes to it: nothing here can. Exit 1 only for drift under --dry-run; a
    source that can't be read is `not connected` and changes nothing."""
    import counting
    import deployments
    listed = [(p, s) for p, s in sorted(counting.sources(root).items()) if s.startswith(("url:", "mcp:")) and re.fullmatch(r"\w[\w-]*", p)]
    if not listed:
        print("NO EXTERNAL PRDS: no feature's PRD source in .loop/docs.tsv is a url or an mcp source")
    drifted = steady = away = 0
    for page, source in listed:
        if page in (texts or {}):
            try:
                with open(texts[page], encoding="utf-8", errors="replace") as handle:
                    body, why = handle.read(), None
            except OSError as error:
                body, why = None, str(error)
        else:
            body, why = deployments.read_link(source)
        if body is None:
            print("not connected: %s (%s): %s" % (page, source, why))
            away += 1
            continue
        want = requirements(body)
        path = os.path.join(root, ".loop", "prd", page + ".md")
        have, owned = mirror_of(path)
        if not want:
            print("EMPTY %s: the source states no requirement ids; the repo copy is kept" % page)
        elif not owned:
            print("SKIPPED %s: %s is not a file sync wrote; it is left as it is" % (page, os.path.relpath(path, root)))
        else:
            diffs = ["%s %s" % (i, "added" if i not in have else "removed" if i not in want
                                else "changed (repo: %s | source: %s)" % (have[i][:50], want[i][:50]))
                     for i in sorted(set(have) | set(want), key=req_key) if have.get(i) != want.get(i)]
            for line in diffs:
                print("DRIFT %s: %s" % (page, line))
            steady, drifted = steady + (not diffs), drifted + bool(diffs)
            if diffs and not dry:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w", encoding="utf-8", newline="\n") as handle:
                    handle.write(SYNC_MARK + "\n<!-- source: %s -->\n" % source)
                    handle.write("".join("- %s: %s\n" % (i, want[i]) for i in sorted(want, key=req_key)))
                print("SYNCED %s: %d requirement(s) from %s" % (page, len(want), source))
    print("SYNC: %d in step, %d drifted, %d not connected" % (steady, drifted, away))
    return 1 if dry and drifted else 0
