#!/usr/bin/env python3
"""The one docs command: check every required doc, fix what is mechanical, list the wording to rewrite.

usage: docs.py audit [--base REF] [--dry-run]

It checks the pages against the template sheet (references/commands.md), the code (stale pages), the tests (Tests
tables, rows not Given/When/Then, Reviewed requirements with no or a stale test) and a release note per tag. It fixes the
mechanical trouble and prints the rest as REWRITE lines; it never deletes a page or changes a criterion's wording.
--dry-run only says what it would fix. Exit 0 only when nothing is left. UNTESTED lines go to .git/loop/untested.tsv.
"""
import argparse
import contextlib
import io
import json
import os
import re
import subprocess
import sys
from os.path import join

import counting
import criteria as cr
import docs
import entry
import pageformat as pf
import prd
from criteria import put, sha
from entry import req_key, requirements
from prd import out as post
from render import mirror_of

# No terminal: a git or gh prompt must fail, not block.
os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")
if not sys.stdin or not sys.stdin.isatty():
    os.dup2(os.open(os.devnull, os.O_RDONLY), 0)

REWRITE = {"CAP", "SCRIPT", "STALE", "UNWRITTEN", "PROBLEM", "SECTIONS", "CRITERION", "NONGOALS", "METRICS", "REVIEW", "SCENARIO", "FORMAT"}


def release_trouble(root):
    """A tag with no CHANGELOG section or GitHub release."""
    try:
        with open(join(root, "CHANGELOG.md")) as handle:
            notes = handle.read()
    except OSError:
        notes = ""
    out = []
    for tag in cr.git("tag", "-l", "v*", check=False).split():
        if not re.search(r"^##\s+\[?v?%s\b" % re.escape(tag[1:]), notes, re.M):  # with or without the v (#4660)
            have = subprocess.run(["gh", "release", "view", tag], cwd=root, capture_output=True, text=True)
            if have.returncode:
                out.append(("RELEASE", tag, "has no release note. Fix: add its CHANGELOG section or a GitHub release"))
    return out


def scenarios(root):
    """A shown row not written as Given/When/Then."""
    shown = {name for names in list(cr.test_rows(root)[0].values()) + list(cr.defect_rows(root).values()) for name in names}
    return [("SCENARIO", "regression", "row %s: '%s' is not 'Given ..., when ..., then ...'. Fix: rewrite its description "
             "(column 6 of .loop/regression.tsv) as one scenario" % (row[0], row[5][:60])) for row in cr.tsv(root, "regression.tsv")
            if row[0] in shown and not cr.SCENARIO.match(row[5])]


def missing(root, command):
    """Whether a script the row's command names is gone; after `cd DIR &&` its path is read from DIR (#4502)."""
    cd = re.match(r"\s*cd\s+(\S+)\s*(?:&&|;)", command)
    base = cd.group(1) if cd and os.path.isdir(join(root, cd.group(1))) else ""
    return any(not os.path.exists(join(root, base, f)) for f in cr.SCRIPT_FILE.findall(command))


def untested(root):
    """(id, reason) per Reviewed requirement with no test, or none passed since its wording appeared."""
    linked, _ = cr.test_rows(root)
    rows = {row[0]: row for row in cr.tsv(root, "regression.tsv")}
    ran = {row[0]: row[2] for row in cr.tsv(root, "regression-runs.tsv") if row[1] == "PASS"}
    out = []
    for rel in cr.pages(root):
        with open(join(root, rel)) as handle:
            lines = handle.read().splitlines()
        signed = any(line.startswith("Review: **Reviewed ") for line in lines)
        for match in filter(None, (cr.LINE.match(line) for line in lines)):
            key, text = match.group(1), match.group(4)
            if match.group(2) == "Unreviewed" and not signed:
                continue
            if not linked.get(key):
                out.append((key, "no test"))
                continue
            since = own_git(root, "log", "-1", "--format=%cs", "-S" + text, "--", rel) or ""
            gone = [name for name in linked[key] if missing(root, rows[name][2])]
            if gone or not any(ran.get(name, "") >= since for name in linked[key]):
                out.append((key, "test no longer matches"))
    return out


def render(check):
    """Re-render the Tests tables (check: list stale ones), as paths."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        cr.cmd_render(argparse.Namespace(check=check))
    return [line.split(" ", 1)[1] for line in out.getvalue().splitlines() if line.startswith(("STALE ", "WROTE "))]


def audit(root, base, dry):
    would, crit = [], bool(docs.config(root).get("criteria"))
    if not docs.read_map(root):
        print("NO PAGES: run add first")
        return 1
    if crit:
        would += ["%s: re-render the Tests table" % name for name in render(dry)]
    # The entry point and stale agent blocks are generated; a missing block needs agents.py.
    stale = [path for kind, path, why in entry.problems(root) if path == entry.ENTRY and kind in ("STALE", "MISSING") or
             kind == "STALE" and path in entry.agent_files(docs.config(root)) and "ENTRY_MARKER" not in why]
    if stale and not dry:
        entry.write(root)
    would += ["%s: regenerate it (entry.py write)" % path for path in stale]
    for line in would:
        print("%s %s" % ("WOULD FIX" if dry else "FIXED", line))
    found = [x for x in docs.problems(root, base) + docs.contract(root) + docs.counts(root) + release_trouble(root) if x[0] != "CHANGED"]
    found += scenarios(root) if crit else []
    if dry:
        found = [item for item in found if item[0] != "TESTS" and item[:2] != ("STALE", "Tests")]
    for kind, page, detail in found:
        print("%s %s: %s" % ("REWRITE" if kind in REWRITE else kind, page, "%s %s" % (kind, detail) if kind in REWRITE else detail))
    todo = untested(root) if crit else []
    for key, why in todo:
        print("UNTESTED %s: %s" % (key, why))
    if not dry:
        with open(join(os.path.dirname(docs.state_file()), "untested.tsv"), "w") as handle:
            handle.writelines("%s\t%s\n" % item for item in todo)
    left = len(found) + (len(would) if dry else 0)
    print("DOCS OK: %d pages" % len(docs.read_map(root)) if not left else "DOCS: %d to do" % left)
    return 1 if left else 0


# check --own: a stale page the goal's diff doesn't touch is a FINDING.


def own_git(root, *args):
    out = subprocess.run(["git"] + list(args), cwd=root, capture_output=True, text=True)
    return out.stdout.strip() if out.returncode == 0 else None


def own_base(root, name):
    for ref in ("origin/" + name, name):
        if own_git(root, "rev-parse", "--verify", "-q", ref + "^{commit}"):
            return ref
    return None


def own_touched(root, ref, paths, head="HEAD"):
    """True when the goal's diff (merge-base of ref, to head) touches a path."""
    out = own_git(root, "diff", "--name-only", ref + "..." + head, "--", *paths)
    return out is None or bool(out)  # no answer: the goal's own


def own_split(root, found, notes, rows, name="main", head="HEAD"):
    """(found, notes) with STALE lines of untouched pages moved to notes as FINDING. head: the goal's branch."""
    ref = own_base(root, name)
    if not ref or own_git(root, "merge-base", "--is-ancestor", head, ref) is not None:
        return found, notes  # no base, or on the base branch
    keep, moved = [], []
    for item in found:
        if item[0] == "STALE" and item[1] in rows and item[2][:1].isdigit() and not own_touched(root, ref, rows[item[1]], head):
            moved.append(("FINDING", "STALE " + item[1], item[2] + " (not touched by this goal; main's own, left for health)"))
        else:
            keep.append(item)
    return keep, notes + moved


def probe(cmd):
    """The finished command, or None if the program is missing."""
    try:
        return subprocess.run(cmd, capture_output=True, text=True)
    except OSError:
        return None


def live(root):
    for e in counting.entries(root):
        kind, _, target = str(e.get("runs", "")).partition(":")
        if kind == "github":
            done = probe(["gh", "run", "list", "--workflow", target, "--limit", "1", "--json", "conclusion,createdAt",
                          "-q", ".[0] | \"\\(.conclusion) \\(.createdAt)\""])
            said = "unknown: gh is not installed here" if done is None else done.returncode == 0 and done.stdout.strip() or "no run found or gh unavailable"
        elif kind == "mac":
            done = probe(["launchctl", "list", target])
            said = "unknown: launchctl is not available on this host" if done is None else "loaded" if done.returncode == 0 else "not loaded"
        elif kind == "local":
            said = "runs on this Mac's local schedule, not in GitHub Actions"
        else:
            said = "a Claude scheduled task is checked in the Claude app"
        print("%s: %s" % (e["name"], said))
    return 0


def owned(root, rel, body, rule):
    """True when every requirement line is owner-reviewed or explained by a revision row, and none of main's was dropped."""
    name = rule["sections"][1]
    shown = cr.git("show", "origin/main:" + rel, check=False)
    main = [(line, tuple(below), m.group(1)) for line, m, below in cr.blocks(dict(cr.sections(shown)).get(name) or []) if m]
    try:
        with open(join(os.path.abspath(cr.git("rev-parse", "--git-common-dir")), "loop", "reviews.tsv")) as handle:
            logged = {key for row in handle for item in row.split("\t")[2:3] for key in item.split(",") if row.split("\t")[1:2] == ["review"]}
    except OSError:
        logged = set()
    have, (tab, gone, _) = set(), pf.revs(body.get(rule["revs"]) or [])
    for line, m, below in cr.blocks(body.get(name) or []):
        if m and m.group(2) == "Unreviewed" and tab.get(m.group(1)) and " ".join(tab[m.group(1)][0][2].split()) == pf.unit(m.group(4), below):
            have.add(m.group(1))  # DOC-20: a revision row explains the new text
            continue
        if not m or m.group(2) == "Unreviewed" or m.group(5) != cr.seal_of(m.group(4), below):
            return False
        if (line, tuple(below), m.group(1)) not in main and m.group(1) not in logged:
            return False
        have.add(m.group(1))
    return {key for _, _, key in main} <= have | set(gone)


def relock(root, slug="", only=()):
    """Relock (DOC-2): re-stamp a page changed only by another goal's reviewed line; with slug, a page stale by code alone."""
    rule, done = cr.rules(), []
    for rel in cr.pages(root):
        if only and os.path.basename(rel)[:-3] not in only:
            continue
        with open(join(root, rel)) as handle:
            text = handle.read()
        line, why = prd.review_of(text, rule)
        match = prd.REVIEW.match(line or "")
        parts = cr.sections(text)
        if why or not match:
            continue
        if not match.group(2):  # Unreviewed: a kept marker says the text still holds
            if slug and not cr.git("diff", "--name-only", "HEAD", "--", rel, check=False).strip():
                with open(join(root, rel), "w") as handle:
                    handle.write(prd.set_review(text, "Review: **Unreviewed** <!-- kept %s@%s -->" % (slug, cr.git("rev-parse", "--short", "HEAD").strip())))
                done.append(os.path.basename(rel)[:-3])
            continue
        now, was = prd.prints(parts, rule), dict(zip(prd.KEYS, match.group(3, 4, 5, 6, 7)))
        moved = [k for k in prd.KEYS[:4] if was[k] != now[k]]
        if (moved == ["R"] and owned(root, rel.replace(os.sep, "/"), dict(parts), rule)) or (slug and not moved):
            kept = " <!-- kept %s@%s -->" % (slug, cr.git("rev-parse", "--short", "HEAD").strip()) if slug else ""
            with open(join(root, rel), "w") as handle:
                handle.write(prd.set_review(text, "Review: **Reviewed %s** <!-- prd %s -->%s" % (match.group(2), " ".join("%s=%s" % (k, now[k]) for k in prd.KEYS), kept)))
            done.append(os.path.basename(rel)[:-3])
    for page in only if slug else ():  # DOC-18: a How-to-use page has no Review line; a kept marker re-stamps it
        rel, feature = "%s/%s.md" % (docs.wiki_dir(root), page), page[len(docs.deployments.HOWTO):]
        held = page.startswith(docs.deployments.HOWTO) and feature in docs.read_map(root) and os.path.isfile(join(root, rel))
        if held and not cr.git("diff", "--name-only", "HEAD", "--", rel, check=False).strip():
            with open(join(root, rel)) as handle:
                text = re.sub(r"\n*<!-- kept [^>]* -->\s*\Z", "", handle.read()).rstrip("\n")
            with open(join(root, rel), "w") as handle:
                handle.write("%s\n\n<!-- kept %s@%s -->\n" % (text, slug, cr.git("rev-parse", "--short", "HEAD").strip()))
            done.append(page)
    if done:
        log = join(os.path.abspath(cr.git("rev-parse", "--git-common-dir")), "loop")
        os.makedirs(log, exist_ok=True)
        with open(join(log, "reviews.tsv"), "a") as handle:
            handle.write("%s\t%s\t%s\t%s\n" % (cr.datetime.datetime.now(cr.datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "restamp" if slug else "relock", ",".join(done), slug + ": mapped code only" if slug else "auto-relock: all lines owner-reviewed"))
    return done


def restamp_own(root, slug, _=()):
    """DOC-2: relock the pages check --own calls STALE for this goal."""
    seen = subprocess.run([sys.executable, join(os.path.dirname(__file__), "docs.py"), "check", "--own", "HEAD"], cwd=root, capture_output=True, text=True).stdout
    return relock(root, slug, {l.split()[1].rstrip(":") for l in seen.splitlines() if l.startswith("STALE ") and l.split()[1:]})


from prdcopy import sync  # noqa: E402,F401  (docs.py sync: moved to prdcopy.py)


def regions(rel, text):
    """(outside, inside) of a page's generated part: the README or Home blocks, the whole Tests page, a feature page's Tests section."""
    name, text = os.path.basename(rel), text.replace(chr(13) + chr(10), chr(10))
    if name in ("README.md", "Home.md"):
        return counting.BLOCK.sub("", text), "".join(m.group(0) for m in counting.BLOCK.finditer(text))
    if name == "Tests.md":
        return "", text
    head, sep, tail = text.partition("\n## Tests")
    return head, sep + tail


def rerender(root, base):
    """DOC-19 (#4632): re-render the generated blocks and tables of a goal's branch that differ from a fresh render only because
    something else moved (the template, main, a row). A file is kept only when the branch added no line to its generated part
    that the fresh render lacks (a hand edit does) and the render touched nothing outside it; any other file is put back, still
    STALE for the worker. Returns the files rewritten."""
    folder = docs.wiki_dir(root)
    files = [rel for rel in ["README.md"] + sorted("%s/%s" % (folder, n) for n in os.listdir(join(root, folder)) if n.endswith(".md"))
             if os.path.isfile(join(root, rel))]
    held = {}
    for rel in files:
        with open(join(root, rel), newline="") as handle:
            held[rel] = handle.read()
    subprocess.run([sys.executable, join(os.path.dirname(os.path.abspath(__file__)), "criteria.py"), "render"], cwd=root, capture_output=True)
    shown = lambda ref: subprocess.run(["git", "show", ref], cwd=root, capture_output=True, text=True).stdout
    mine = cr.git("merge-base", "HEAD", "origin/" + base, check=False)
    kept = []
    for rel, was in held.items():
        with open(join(root, rel), newline="") as handle:
            now = handle.read()
        if now == was:
            continue
        (out_was, in_was), (out_now, in_now), (_, in_old) = regions(rel, was), regions(rel, now), regions(rel, shown("%s:%s" % (mine, rel)) if mine else "")
        added = set(in_was.splitlines()) - set(in_old.splitlines()) - set(in_now.splitlines())
        if out_was != out_now or any(line.strip() for line in added):
            with open(join(root, rel), "w", newline="") as handle:
                handle.write(was)
        else:
            kept.append(rel)
    return kept


# AUT-9: each routine declares what it may do
PERM_DOC = r"""AUT-9: audit.py permissions write|check [--repo DIR] [--dry-run]: .loop/permissions.tsv rows (routine,
allow|deny, Tool(spec), why) into .claude/settings.json; check prints UNDECLARED, NOT WRITTEN, UNCOVERED or CONFLICT."""


def perm_write(root, dry):
    table, bad = counting.perm_declared(root)
    if bad:
        print("\n".join(bad))
        return 1
    path = join(root, ".claude", "settings.json")
    data = {}
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, ValueError) as error:
            print("REFUSED: .claude/settings.json is not readable JSON (%s). Nothing was written. Fix: repair it." % error)
            return 1
    if not isinstance(data, dict) or not isinstance(data.get("permissions", {}), dict):
        print("REFUSED: .claude/settings.json has no permissions object I can extend. Nothing was written.")
        return 1
    block, added = data.setdefault("permissions", {}), 0
    for kind, rule, _ in (row for mine in table.values() for row in mine):
        held = block.setdefault(kind, [])
        if not isinstance(held, list):
            print("REFUSED: .claude/settings.json permissions.%s is not a list. Nothing was written." % kind)
            return 1
        if rule not in held:
            held.append(rule)
            added += 1
    if dry or not added:
        print("PERMISSIONS %s: %d rule(s) to add" % ("DRY RUN" if dry else "CURRENT", added))
        return 0
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print("PERMISSIONS WRITTEN: %d rule(s) in .claude/settings.json" % added)
    return 0


def perm_main(argv):
    parser = argparse.ArgumentParser(prog="audit.py permissions", description=PERM_DOC, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("write", "check"))
    parser.add_argument("--repo", default="")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    root = counting.perm_root_of(args.repo)
    if args.command == "write":
        return perm_write(root, args.dry_run)
    findings = entry.perm_check(root)
    print("\n".join(findings) if findings else "PERMISSIONS OK")
    return 1 if [line for line in findings if not line.startswith("NOTE")] else 0


if __name__ == "__main__":
    if sys.argv[1:2] == ["rerender"] and len(sys.argv) > 2:
        print("".join("RERENDERED %s\n" % rel for rel in rerender(os.getcwd(), sys.argv[2])), end="")
        sys.exit(0)
    if sys.argv[1:2] in (["restamp"], ["restamp-own"]) and len(sys.argv) > 3 - (sys.argv[1] == "restamp-own"):
        print("".join("RESTAMPED %s\n" % p for p in (restamp_own if sys.argv[1] == "restamp-own" else relock)(os.getcwd(), sys.argv[2], sys.argv[3:])), end="")
        sys.exit(0)
    sys.exit(perm_main(sys.argv[2:]) if sys.argv[1:2] == ["permissions"] else print((__doc__ or "") + PERM_DOC) or 0)
