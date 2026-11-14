#!/usr/bin/env python3
"""AUT-9: each routine declares what it may do, in its repo.

usage: permissions.py write [--repo DIR] [--dry-run]
       permissions.py check [--repo DIR]

`.loop/permissions.tsv` has one row per rule: `routine<TAB>allow|deny<TAB>rule<TAB>why` (# lines are comments). A rule is
a Claude Code permission rule: Bash(python3 skills/x/scripts/*), Read(~/.workflow-loop/**), WebFetch(domain:api.github.com).

  write   merge the rows into the repo's committed .claude/settings.json (permissions.allow and permissions.deny),
          keeping every other key and rule; a row holding a home path, a user name or a token-like string is refused
  check   UNDECLARED a routine with no rows; NOT WRITTEN a row the settings file lacks; UNCOVERED a command or site the
          routine's Runbook (Steps, Full run) names that no allow row covers; CONFLICT an allow a deny covers
          (a deny wins); PERMISSIONS OK or one line per finding and exit 1. No routines means OK; no
          permissions.tsv is a NOTE line (said, never a failure) until the repo adds one.
"""
import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys

PROGRAMS = ("python3", "python", "gh", "git", "claude", "curl", "node")
PRIVATE = re.compile(r"(/Users/|/home/[A-Za-z]|[A-Za-z]:[\\/]+Users|\bsk-[A-Za-z0-9]{8}|\bghp_|\bxox[bp]-)")
FIELD = re.compile(r"^- \*\*([A-Za-z ]+):\*\*\s*(.*)$")


def root_of(repo):
    top = subprocess.run(["git", "-C", repo or ".", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    return top.stdout.strip() or os.path.abspath(repo or ".")


def rows(path):
    """The (line number, fields) of a tab file, comments and blanks skipped; [] when the file is absent."""
    try:
        with open(path, encoding="utf-8-sig") as handle:
            return [(n, line.rstrip("\r\n").split("\t")) for n, line in enumerate(handle, 1)
                    if line.strip() and not line.lstrip().startswith("#")]
    except OSError:
        return []


def declared(root):
    """{routine: [(kind, rule, why)]} and the problems in the file itself."""
    out, bad = {}, []
    for number, row in rows(os.path.join(root, ".loop", "permissions.tsv")):
        routine, kind, rule = (row + ["", "", ""])[:3]
        if kind not in ("allow", "deny") or not re.match(r"^[A-Za-z]+\(.+\)$", rule) or not routine:
            bad.append("BAD ROW permissions.tsv:%d (routine<TAB>allow|deny<TAB>Tool(spec)<TAB>why)" % number)
        elif PRIVATE.search(rule) or os.path.expanduser("~") in rule:
            bad.append("PRIVATE ROW permissions.tsv:%d holds a home path, a user name or a token: write it with ~ or a glob" % number)
        else:
            out.setdefault(routine, []).append((kind, rule, row[3] if len(row) > 3 else ""))
    return out, bad


def matches(rule, tool, text):
    """Does a permission rule `Tool(spec)` cover `text` for that tool: a prefix rule `x:*`, else a glob."""
    found = re.match(r"^([A-Za-z]+)\((.*)\)$", rule)
    if not found or found.group(1) != tool:
        return False
    spec = found.group(2)
    if spec.endswith(":*"):
        return text == spec[:-2] or text.startswith(spec[:-2] + " ")
    return fnmatch.fnmatchcase(text, spec)


def wiki_page(root, page):
    try:
        with open(os.path.join(root, ".loop", "config.json"), encoding="utf-8") as handle:
            folder = json.load(handle).get("wiki_dir") or "docs/wiki"
    except (OSError, ValueError):
        folder = "docs/wiki"
    try:
        with open(os.path.join(root, folder, page + ".md"), encoding="utf-8-sig") as handle:
            return handle.read().splitlines()
    except OSError:
        return []


def needs(root, routine, page):
    """The (tool, text) pairs the Runbook's Steps and Full run name: a backticked command that starts with a program, and
    each https host as a WebFetch domain."""
    lines, inside, field, found = wiki_page(root, page), False, "", []
    for line in lines:
        if line.startswith("### "):
            inside = line[4:].strip() == routine
        elif line.startswith("## "):
            inside = False
        elif inside:
            match = FIELD.match(line)
            field = match.group(1) if match else field
            if field in ("Steps", "Full run"):
                for span in re.findall(r"`([^`]+)`", line):
                    if " " in span and span.split(" ", 1)[0] in PROGRAMS:
                        found.append(("Bash", " ".join(span.split())))
                found += [("WebFetch", "domain:" + host) for host in re.findall(r"https?://([A-Za-z0-9.-]+)", line)]
    return found


def covered(allow, tool, text):
    return any(matches(rule, tool, text) for kind, rule, _ in allow if kind == "allow")


def check(root):
    """The findings, one line each, for every routine in .loop/routines.tsv."""
    table, findings = declared(root)
    if not os.path.exists(os.path.join(root, ".loop", "permissions.tsv")):
        return ["NOTE no .loop/permissions.tsv: routines declare no permissions yet. Fix: add its rows, then permissions.py write"]             if rows(os.path.join(root, ".loop", "routines.tsv")) else []
    try:
        with open(os.path.join(root, ".claude", "settings.json"), encoding="utf-8") as handle:
            written = (json.load(handle).get("permissions") or {})
    except (OSError, ValueError):
        written = {}
    for _, row in rows(os.path.join(root, ".loop", "routines.tsv")):
        routine, page = (row + ["", ""])[:2]
        mine = table.get(routine, [])
        if not mine:
            findings.append("UNDECLARED %s: no rows in .loop/permissions.tsv. Fix: list the commands, paths and sites its Runbook needs" % routine)
        for kind, rule, _ in mine:
            if rule not in [r for r in (written.get(kind) if isinstance(written, dict) else None) or [] if isinstance(r, str)]:
                findings.append("NOT WRITTEN %s %s %s. Fix: permissions.py write" % (routine, kind, rule))
        for tool, text in needs(root, routine, page):
            if mine and not covered(mine, tool, text):
                findings.append("UNCOVERED %s: the Runbook names %s(%s) and no allow row covers it" % (routine, tool, text))
        for kind, rule, _ in mine:
            inner = re.match(r"^([A-Za-z]+)\((.*)\)$", rule)
            if kind == "allow" and inner and any(k == "deny" and matches(r, inner.group(1), inner.group(2)) for k, r, _ in mine):
                findings.append("CONFLICT %s: the allow %s is covered by a deny, which wins" % (routine, rule))
    return findings


def write(root, dry):
    table, bad = declared(root)
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


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("write", "check"))
    parser.add_argument("--repo", default="")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    root = root_of(args.repo)
    if args.command == "write":
        return write(root, args.dry_run)
    findings = check(root)
    print("\n".join(findings) if findings else "PERMISSIONS OK")
    return 1 if [line for line in findings if not line.startswith("NOTE")] else 0


if __name__ == "__main__":
    sys.exit(main())
