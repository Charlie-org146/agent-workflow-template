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
import fnmatch
import io
import json
import os
import re
import subprocess
import sys

import counting
import criteria
import docs
import entry
import prd

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


def probe(cmd):
    """The finished command, or None when the program is missing (no gh, or no launchctl off the Mac): the state is then unknown."""
    try:
        return subprocess.run(cmd, capture_output=True, text=True)
    except OSError:
        return None


def live(root):
    """Print each routine's live state: a workflow's newest run, a launch agent loaded or not."""
    for e in counting.entries(root):
        kind, _, target = str(e.get("runs", "")).partition(":")
        if kind == "github":
            done = probe(["gh", "run", "list", "--workflow", target, "--limit", "1", "--json", "conclusion,createdAt",
                          "-q", ".[0] | \"\\(.conclusion) \\(.createdAt)\""])
            said = "unknown: gh is not installed here" if done is None else done.stdout.strip() if done.returncode == 0 and done.stdout.strip() else "no run found or gh unavailable"
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
    """True when every requirement line is owner-reviewed text: its seal holds, and it is main's own line or its id is in
    the reviews log; no line main has was dropped. A line nobody reviewed is not owned, so the page stays LOCKED."""
    name = rule["sections"][1]
    shown = criteria.git("show", "origin/main:" + rel, check=False)
    main = [(line, tuple(below), m.group(1)) for line, m, below in criteria.blocks(dict(criteria.sections(shown)).get(name) or []) if m]
    try:
        with open(os.path.join(os.path.abspath(criteria.git("rev-parse", "--git-common-dir")), "loop", "reviews.tsv")) as handle:
            logged = {key for row in handle for item in row.split("\t")[2:3] for key in item.split(",") if row.split("\t")[1:2] == ["review"]}
    except OSError:
        logged = set()
    have = set()
    for line, m, below in criteria.blocks(body.get(name) or []):
        if not m or m.group(2) == "Unreviewed" or m.group(5) != criteria.seal_of(m.group(4), below):
            return False
        if (line, tuple(below), m.group(1)) not in main and m.group(1) not in logged:
            return False
        have.add(m.group(1))
    return {key for _, _, key in main} <= have


def relock(root):
    """Relock (DOC-2): re-stamp each reviewed page whose only change is another goal's owner-reviewed line (R moved, all lines owned)."""
    rule, done = criteria.rules(), []
    for rel in criteria.pages(root):
        with open(os.path.join(root, rel)) as handle:
            text = handle.read()
        line, why = prd.review_of(text, rule)
        match = prd.REVIEW.match(line or "")
        parts = criteria.sections(text)
        if why or not match or not match.group(2):
            continue
        now = prd.prints(parts, rule)
        if [k for k in prd.KEYS[:4] if match.group(3 + prd.KEYS.index(k)) != now[k]] == ["R"] and owned(root, rel, dict(parts), rule):
            fresh = prd.set_review(text, "Review: **Reviewed %s** <!-- prd %s -->" % (match.group(2), " ".join("%s=%s" % (k, now[k]) for k in prd.KEYS)))
            with open(os.path.join(root, rel), "w") as handle:
                handle.write(fresh)
            done.append(os.path.basename(rel)[:-3])
    if done:
        log = os.path.join(os.path.abspath(criteria.git("rev-parse", "--git-common-dir")), "loop")
        os.makedirs(log, exist_ok=True)
        with open(os.path.join(log, "reviews.tsv"), "a") as handle:
            handle.write("%s\trelock\t%s\tauto-relock: all lines owner-reviewed\n" % (criteria.datetime.datetime.now(
                criteria.datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), ",".join(done)))
    return done


# --- AUT-9: each routine declares what it may do (python3 audit.py permissions write|check) ---
PERM_DOC = r"""AUT-9: audit.py permissions write|check [--repo DIR] [--dry-run]: .loop/permissions.tsv rows (routine,
allow|deny, Tool(spec), why) into .claude/settings.json; check prints UNDECLARED, NOT WRITTEN, UNCOVERED or CONFLICT."""
PERM_PROGRAMS = ("python3", "python", "gh", "git", "claude", "curl", "node")
PERM_PRIVATE = re.compile(r"(/Users/|/home/[A-Za-z]|[A-Za-z]:[\\/]+Users|\bsk-[A-Za-z0-9]{8}|\bghp_|\bxox[bp]-)")
PERM_FIELD = re.compile(r"^- \*\*([A-Za-z ]+):\*\*\s*(.*)$")


def perm_root_of(repo):
    top = subprocess.run(["git", "-C", repo or ".", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    return top.stdout.strip() or os.path.abspath(repo or ".")


def perm_rows(path):
    """The (line number, fields) of a tab file, comments and blanks skipped; [] when the file is absent."""
    try:
        with open(path, encoding="utf-8-sig") as handle:
            return [(n, line.rstrip("\r\n").split("\t")) for n, line in enumerate(handle, 1)
                    if line.strip() and not line.lstrip().startswith("#")]
    except OSError:
        return []


def perm_declared(root):
    """{routine: [(kind, rule, why)]} and the problems in the file itself."""
    out, bad = {}, []
    for number, row in perm_rows(os.path.join(root, ".loop", "permissions.tsv")):
        routine, kind, rule = (row + ["", "", ""])[:3]
        if kind not in ("allow", "deny") or not re.match(r"^[A-Za-z]+\(.+\)$", rule) or not routine:
            bad.append("BAD ROW permissions.tsv:%d (routine<TAB>allow|deny<TAB>Tool(spec)<TAB>why)" % number)
        elif PERM_PRIVATE.search(rule) or os.path.expanduser("~") in rule:
            bad.append("PERM_PRIVATE ROW permissions.tsv:%d holds a home path, a user name or a token: write it with ~ or a glob" % number)
        else:
            out.setdefault(routine, []).append((kind, rule, row[3] if len(row) > 3 else ""))
    return out, bad


def perm_matches(rule, tool, text):
    """Does a permission rule `Tool(spec)` cover `text` for that tool: a prefix rule `x:*`, else a glob."""
    found = re.match(r"^([A-Za-z]+)\((.*)\)$", rule)
    if not found or found.group(1) != tool:
        return False
    spec = found.group(2)
    if spec.endswith(":*"):
        return text == spec[:-2] or text.startswith(spec[:-2] + " ")
    return fnmatch.fnmatchcase(text, spec)


def perm_wiki_page(root, page):
    try:
        folder = docs.wiki_dir(root)
    except SystemExit:
        folder = "docs/wiki"
    try:
        with open(os.path.join(root, folder, page + ".md"), encoding="utf-8-sig") as handle:
            return handle.read().splitlines()
    except OSError:
        return []


def perm_needs(root, routine, page):
    """The (tool, text) pairs the Runbook's Steps and Full run name: a backticked command that starts with a program, and
    each https host as a WebFetch domain."""
    lines, inside, field, found = perm_wiki_page(root, page), False, "", []
    for line in lines:
        if line.startswith("### "):
            inside = line[4:].strip() == routine
        elif line.startswith("## "):
            inside = False
        elif inside:
            match = PERM_FIELD.match(line)
            field = match.group(1) if match else field
            if field in ("Steps", "Full run"):
                for span in re.findall(r"`([^`]+)`", line):
                    if " " in span and span.split(" ", 1)[0] in PERM_PROGRAMS:
                        found.append(("Bash", " ".join(span.split())))
                found += [("WebFetch", "domain:" + host) for host in re.findall(r"https?://([A-Za-z0-9.-]+)", line)]
    return found


def perm_covered(allow, tool, text):
    return any(perm_matches(rule, tool, text) for kind, rule, _ in allow if kind == "allow")


def perm_check(root):
    """The findings, one line each, for every routine in .loop/routines.tsv."""
    table, findings = perm_declared(root)
    if not os.path.exists(os.path.join(root, ".loop", "permissions.tsv")):
        return ["NOTE no .loop/permissions.tsv: routines declare no permissions yet. Fix: add its rows, then permissions.py write"]             if perm_rows(os.path.join(root, ".loop", "routines.tsv")) else []
    try:
        with open(os.path.join(root, ".claude", "settings.json"), encoding="utf-8") as handle:
            written = (json.load(handle).get("permissions") or {})
    except (OSError, ValueError):
        written = {}
    for _, row in perm_rows(os.path.join(root, ".loop", "routines.tsv")):
        routine, page = (row + ["", ""])[:2]
        mine = table.get(routine, [])
        if not mine:
            findings.append("UNDECLARED %s: no rows in .loop/permissions.tsv. Fix: list what its Runbook needs" % routine)
        for kind, rule, _ in mine:
            if rule not in [r for r in (written.get(kind) if isinstance(written, dict) else None) or [] if isinstance(r, str)]:
                findings.append("NOT WRITTEN %s %s %s. Fix: audit.py permissions write" % (routine, kind, rule))
        for tool, text in perm_needs(root, routine, page):
            if mine and not perm_covered(mine, tool, text):
                findings.append("UNCOVERED %s: the Runbook names %s(%s) and no allow row covers it" % (routine, tool, text))
        for kind, rule, _ in mine:
            inner = re.match(r"^([A-Za-z]+)\((.*)\)$", rule)
            if kind == "allow" and inner and any(k == "deny" and perm_matches(r, inner.group(1), inner.group(2)) for k, r, _ in mine):
                findings.append("CONFLICT %s: the allow %s is covered by a deny, which wins" % (routine, rule))
    return findings


def perm_write(root, dry):
    table, bad = perm_declared(root)
    if bad:
        print("\n".join(bad))
        return 1
    path = os.path.join(root, ".claude", "settings.json")
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
    for mine in table.values():
        for kind, rule, _ in mine:
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
    root = perm_root_of(args.repo)
    if args.command == "write":
        return perm_write(root, args.dry_run)
    findings = perm_check(root)
    print("\n".join(findings) if findings else "PERMISSIONS OK")
    return 1 if [line for line in findings if not line.startswith("NOTE")] else 0


if __name__ == "__main__":
    sys.exit(perm_main(sys.argv[2:]) if sys.argv[1:2] == ["permissions"] else print((__doc__ or "") + PERM_DOC) or 0)
