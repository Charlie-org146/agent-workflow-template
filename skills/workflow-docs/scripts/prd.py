#!/usr/bin/env python3
"""The PRD layer of feature pages: the owner's review line and its lock, converting old pages, drafting new ones.

usage: prd.py <command> [options]

  new NAME "<idea>" --paths A,B [--prefix XX]
                               draft a new feature's PRD from a one-line idea, Unreviewed, and map it
  convert [--write]            turn old pages (Summary, Criteria, Tests) into PRD pages; without --write only says so
  skeleton PATH --title T --problem P --requirement LINE
                               write one PRD page (the one page writer; workflow-setup uses it)

The review line sits under the title (or the Milestone line): 'Review: **Unreviewed**', or
'Review: **Reviewed DATE** <!-- prd P=.. R=.. N=.. M=.. U=.. -->', one 8-hex fingerprint each for Problem,
Requirements, Non-goals, Success metrics and Usage, written by criteria.py review PAGE --user. Each covers the
section's name and paragraphs, whitespace collapsed, requirement stamps removed. While Reviewed, a change to any of the
first four is LOCKED (the check fails); Usage was dropped on 2026-11-13: U is still written, never reported.

convert completes partial pages: Summary+Criteria (old), Problem+Criteria, Summary+Requirements, a missing Review
line, a missing Non-goals and/or Success metrics section. A page in PRD form is skipped; any other is refused with
what is missing. New sections get one placeholder line, so the docs check says UNWRITTEN until real drafts replace it.
It runs git and nothing else.
"""
import argparse
import importlib
import itertools
import os
import re
import subprocess
import sys
import urllib.request

import criteria

MARKER = "<!-- workflow-docs -->"
PLACEHOLDER = "Write this page from what is really in the repo."
REVIEW = re.compile(r"^Review: \*\*(Unreviewed|Reviewed (\d{4}-\d\d-\d\d))\*\*"
                    r"(?: <!-- prd P=(\w{8}) R=(\w{8}) N=(\w{8}) M=(\w{8}) U=(\w{8}) -->)?(?: <!-- kept [\w.@-]+ -->)?$")
KEYS = "PRNMU"
def names(rule):
    """Section names in fingerprint order."""
    return rule["sections"][:4] + [rule["usage"]]


def core(parts, rule):
    """The section names other than Usage, Deployments, Runbook."""
    return [name for name, _ in parts if name not in (rule["usage"], rule["deploy"], rule["runbook"])]


def paras(lines):
    """A section's paragraphs: a blank line or list item starts one; a wrapped line joins the last."""
    out = []
    for block in re.split(r"\n[ \t]*\n", "\n".join(lines or []).replace("\r\n", "\n").replace("\r", "\n")):
        new = True
        for line in block.split("\n"):
            if new or re.match(r"\s*([-*+]|\d+\.)\s", line):
                out.append(line)
            else:
                out[-1] += "\n" + line
            new = False
    return [para for para in out if para.strip()]


def norm(name, lines):
    """A section as hashed: name, then lines, whitespace collapsed, stamps removed."""
    found = [" ".join(" ".join("- %s: %s" % (m.group(1), m.group(4)) if m else x for x, m in
                               ((x, criteria.LINE.match(x.rstrip())) for x in para.split("\n"))).split()) for para in paras(lines)]
    return name + "\n" + "\n".join(found)


def prints(parts, rule):
    body = dict(parts)
    return {key: criteria.seal(norm(name, body.get(name))) for key, name in zip(KEYS, names(rule))}


def head(text):
    """The lines before the first section."""
    return list(itertools.takewhile(lambda line: not line.startswith("## "), text.replace("\r\n", "\n").split("\n")))


def review_of(text, rule):
    """(review line or None, trouble or None) from the page head."""
    seq = [line.strip() for line in head(text) if line.strip()]
    starts = lambda n, pre: n < len(seq) and seq[n].startswith(pre)  # noqa: E731
    at = 1 if seq[:1] == [MARKER] else 0
    at += starts(at, "# ")
    at += starts(at, rule["milestone"] + ":")
    line = seq[at] if starts(at, rule["review"] + ":") else None
    rest = seq[at + bool(line):]
    if line is None:
        if any(item.startswith(rule["review"] + ":") for item in seq):
            return None, ("REVIEW", "the Review line must come right after the title or the Milestone line. Fix: move it there")
        return None, ("REVIEW", "has no Review line. Fix: add 'Review: **Unreviewed**' under the title (or its Milestone "
                                "line), or run prd.py convert --write (workflow-docs)")
    if rest:
        return line, ("SECTIONS", "has text between the Review line and the first section: %s. Fix: move it into Problem, "
                                  "or remove it" % rest[0][:60])
    found = REVIEW.match(line)
    if not found or (found.group(2) and not found.group(3)):
        return line, ("REVIEW", "a malformed Review line: %s. Fix: write 'Review: **Unreviewed**'; only the owner's "
                                "/workflow-docs review PAGE --user writes a Reviewed one" % line[:60])
    return line, None


def trouble(root, page, text, parts, rule):
    """The PRD contract lines for one page, as (kind, page, detail)."""
    found, body, top = [], dict(parts), rule["metrics_lines"]
    nongoals, metrics = rule["sections"][2:4]
    line, why = review_of(text, rule)
    if why:
        found.append((why[0], page, why[1]))
    if not paras(body.get(nongoals)):
        found.append(("NONGOALS", page, "%s is empty. Fix: write at least one line on what the feature deliberately "
                                        "won't do" % nongoals))
    count = len(paras(body.get(metrics)))
    if not 1 <= count <= top:
        found.append(("METRICS", page, "%s has %d lines, want 1 to %d. Fix: write one to %d measurable lines on how we "
                      "know it works" % (metrics, count, top, top)))
    match = REVIEW.match(line or "")
    if why or not match or not match.group(2):
        return found
    was, now = dict(zip(KEYS, match.group(3, 4, 5, 6, 7))), prints(parts, rule)
    moved = [key for key in KEYS[:4] if was[key] != now[key]]
    rel = "%s/%s.md" % (criteria.folder_of(root), page)
    if moved == ["R"] and importlib.import_module("audit").owned(root, rel, dict(parts), rule):
        moved = []  # another goal's reviewed line moved the lock: relock re-stamps it
    if moved:
        found.append(("LOCKED", page, "the reviewed PRD changed in %s (reviewed lock %s, now %s). Fix: git log -p -- %s to "
                      "find the reviewed text and restore it, or the owner runs /workflow-docs unreview %s --user (and "
                      "/workflow-docs unreview ID --user for a reviewed requirement) and reviews it again" % (
                          ", ".join(dict(zip(KEYS, names(rule)))[key] for key in moved),
                          " ".join("%s=%s" % (key, was[key]) for key in moved),
                          " ".join("%s=%s" % (key, now[key]) for key in moved), rel, page)))
    return found


def set_review(text, line):
    """The text with its Review line replaced."""
    lines = text.split("\n")
    for number in range(len(head(text))):
        if lines[number].startswith("Review:"):
            lines[number] = line
            return "\n".join(lines)
    return text


def review_text(text, day, page):
    """(new text, None) Reviewed on day, or (text, why)."""
    rule = criteria.rules()
    parts = criteria.sections(text)
    have = core(parts, rule)
    if have != rule["sections"]:
        return text, "its sections are %s, not a PRD. Fix: run prd.py convert --write (workflow-docs) first" % (", ".join(have) or "none")
    line, why = review_of(text, rule)
    if line is None or (why and why[0] == "SECTIONS"):
        return text, why[1]
    sums = prints(parts, rule)
    return set_review(text, "Review: **Reviewed %s** <!-- prd %s -->" % (day, " ".join("%s=%s" % (k, sums[k]) for k in KEYS))), None


def unreview_text(text, page):
    line, why = review_of(text, criteria.rules())
    return (text, why[1]) if line is None else (set_review(text, "Review: **Unreviewed**"), None)


def skeleton(title, problem, requirement, milestone=""):
    """The one PRD page writer: an Unreviewed page with placeholder sections."""
    return "%s\n%s\n\n%sReview: **Unreviewed**\n\n## Problem\n\n%s\n\n## Requirements\n\n%s\n\n## Non-goals\n\n- %s\n\n" \
           "## Success metrics\n\n- %s\n\n## Tests\n\n" % (MARKER, title, milestone + "\n\n" if milestone else "",
                                                           problem.strip(), group(requirement), PLACEHOLDER, PLACEHOLDER)


def group(requirements):
    """Requirement lines under the two DOC-7 groups (all Functional); kept if grouped."""
    if re.search(r"^### ", requirements, re.M):
        return requirements
    return "### Functional\n\n%s\n\n### Non-functional\n\nNone" % requirements.strip("\n")


def convert_text(text, rule):
    """(outcome, new text): skipped, converted, completed, 'refused: why'."""
    parts = criteria.sections(text)
    have = core(parts, rule)
    first, second, third, fourth = rule["sections"][:4]
    shapes = ([first, "Summary"], [second, "Criteria"], [third, None], [fourth, None], ["Tests"])
    at, plan = 0, []
    for allowed in shapes:
        if at < len(have) and have[at] in allowed:
            plan.append(have[at])
            at += 1
        elif None in allowed:
            plan.append(None)
        else:
            return "refused: sections are %s; want %s (Summary and Criteria are read as Problem and Requirements)" % (
                ", ".join(have) or "none", ", ".join(rule["sections"])), text
    if at != len(have):
        return "refused: unknown section %s; want %s" % (have[at], ", ".join(rule["sections"])), text
    line, _ = review_of(text, rule)
    if plan == rule["sections"] and line:
        return "skipped", text
    fenced, out = False, []
    for raw in text.split("\n"):
        if raw.startswith("```"):
            fenced = not fenced
        if not fenced and raw.strip() == "## Summary":
            raw = "## " + first
        elif not fenced and raw.strip() == "## Criteria":
            raw = "## " + second
        elif not fenced and raw.strip() in ("## " + fourth, "## " + rule["deploy"], "## Tests"):
            for name, there in ((third, plan[2]), (fourth, plan[3])):
                if not there and "## " + name not in out:
                    out += ["## " + name, "", "- " + PLACEHOLDER, ""]
                if raw.strip() == "## " + fourth:
                    break
        out.append(raw)
    fresh = "\n".join(out)
    head_, _, rest = fresh.partition("\n## %s\n" % second)
    if rest:
        body, _, tail = rest.partition("\n## ")
        fresh = head_ + "\n## %s\n\n%s\n\n" % (second, group(body.strip("\n"))) + ("## " + tail if tail else "")
    if not line:
        pre = head(fresh)
        spot = max([n for n, item in enumerate(pre) if item.startswith(("# ", rule["milestone"] + ":"))] or [0])
        rest = fresh.split("\n")[spot + 1 if pre else 0:]
        fresh = "\n".join(pre[:spot + 1] + ["", "Review: **Unreviewed**"] + ([""] if not pre else []) + rest)
    return ("converted" if "Summary" in have and "Criteria" in have else "completed"), fresh


def feature_pages(root):
    import docs
    folder = criteria.folder_of(root)
    return [page for page in sorted(docs.read_map(root)) if page != "Home" and os.path.isfile(os.path.join(root, folder, page + ".md"))
            and not docs.guide(root, page)]


def cmd_convert(args):
    root = criteria.git("rev-parse", "--show-toplevel")
    rule, bad = criteria.rules(), 0
    for page in feature_pages(root):
        path = os.path.join(root, criteria.folder_of(root), page + ".md")
        text = open(path).read()
        outcome, fresh = convert_text(text, rule)
        bad += outcome.startswith("refused")
        if args.write and fresh != text:
            open(path, "w").write(fresh)
        print("%s %s%s" % (page, outcome, "" if args.write or outcome == "skipped" or outcome.startswith("refused") else " (dry run)"))
    if not args.write:
        print("DRY RUN: nothing written. Fix: run prd.py convert --write")
    elif bad:
        print("REFUSED %d page(s). Fix: give each the sections Problem (or Summary), Requirements (or Criteria) and Tests, "
              "then run prd.py convert --write again" % bad)
    return 1 if bad else 0


def used_prefixes(root):
    """Every ID prefix in use."""
    used = set()
    for rel in criteria.pages(root):
        used |= set(re.findall(r"^- ([A-Z]{2,5})-\d+: ", open(os.path.join(root, rel)).read(), re.M))
    for row in criteria.tsv(root, "regression.tsv"):
        used |= {item.split("-")[0] for item in (row[0], row[3]) if criteria.ID.match(item)}
    return used


def cmd_new(args):
    import docs
    example = 'prd.py new Billing "charge cards once a month" --paths src/billing'
    if criteria.ID.match(args.name):
        sys.exit("REFUSED: %s looks like a requirement ID (^[A-Z]{2,5}-\\d+$), so review could not name the page. "
                 "Fix: pick another name, e.g. %s" % (args.name, example))
    if not docs.PAGE.match(args.name) or args.name == "Home":
        sys.exit("REFUSED: bad page name %s. Fix: letters, digits and dashes, not Home, e.g. %s" % (args.name, example))
    if not [p for p in (args.paths or "").split(",") if p.strip()]:
        sys.exit("REFUSED: no --paths, and an unmapped page fails the docs check. Fix: name what the page describes, e.g. %s" % example)
    idea = " ".join(args.idea.split())
    if not idea:
        sys.exit("REFUSED: no idea. Fix: give one line, e.g. %s" % example)
    root = criteria.git("rev-parse", "--show-toplevel")
    rel = "%s/%s.md" % (criteria.folder_of(root), args.name)
    path = os.path.join(root, rel)
    if os.path.exists(path):
        sys.exit("REFUSED: %s already exists. Fix: edit it, or pick a new name, e.g. %s" % (rel, example))
    used = used_prefixes(root)
    if args.prefix:
        if not re.match(r"^[A-Z]{2,5}$", args.prefix) or args.prefix in used:
            sys.exit("REFUSED: --prefix %s must be 2 to 5 capital letters not already in use. Fix: --prefix %s" % (
                args.prefix, next(("ZZ" + c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if "ZZ" + c not in used), "QQQ")))
        tag = args.prefix
    else:
        letters = re.sub(r"[^A-Za-z]", "", args.name).upper()
        tag = next((x for x in dict.fromkeys(letters[:n] for n in (3, 4, 5)) if len(x) >= 2 and x not in used), None)
        if not tag:
            sys.exit("REFUSED: no free ID prefix from the name %s. Fix: add --prefix XX (2 to 5 capital letters, unused)" % args.name)
    key = "%s-1" % tag
    text = skeleton("# " + args.name.replace("-", " "), "- " + idea, "- %s: **Unreviewed** %s\n  - %s" % (key, idea, PLACEHOLDER))
    linked, _ = criteria.test_rows(root)
    text += "\n".join(criteria.table(root, [(key, idea)], linked)) + "\n"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(text)
    docs.cmd_add(argparse.Namespace(page=args.name, paths=args.paths))
    print("DRAFTED %s: Review **Unreviewed**, requirement %s" % (rel, key))
    print("NEXT replace the placeholder lines (the requirement's sub-bullet, Non-goals, Success metrics) with real drafts, "
          "and say the Problem from the user's side; the docs check says UNWRITTEN until then")
    print("NEXT add %s's regression row in this same pull request (it needs one before the next release): "
          "regression.py add <row-id> --level land --command \"<test>\" --goal %s --describe \"Given ..., when ..., then ...\"" % (key, key))
    print("NEXT then run: docs.py check")
    return 0


def cmd_skeleton(args):
    open(args.path, "w").write(skeleton(args.title, args.problem, args.requirement))
    print("WROTE " + args.path)
    return 0


READER = "LOOP_PRD_READER"  # run as `COMMAND URL`; stdout is the PRD


def read_link(url):
    """(text, None) of the PRD at a source (`url:<link>` or `mcp:<server>:<resource>`), or (None, why): never a guess or
    cache. A reader command in $LOOP_PRD_READER (given the whole source) wins, and is how an MCP connector is reached;
    else a file path, file: link or http(s) page. An mcp source or a Notion link needs the reader (no sign-in)."""
    try:
        source, url = url, url[4:] if url.startswith("url:") else url
        reader = os.environ.get(READER)
        if reader:
            done = subprocess.run(reader.split() + [source], capture_output=True, text=True, timeout=120)
            return (done.stdout, None) if done.returncode == 0 and done.stdout.strip() else (None, "the reader %s printed nothing (exit %d)" % (reader.split()[0], done.returncode))
        if url.startswith("file:"):
            url = urllib.request.url2pathname(url[5:].lstrip("/") if re.match(r"file:/+\w:", url) else url[5:])
        if os.path.exists(url):
            return open(url, encoding="utf-8").read(), None
        if source.startswith("mcp:") or re.search(r"(^|[/.])notion\.(so|site|com)/", url):
            return None, "this source needs its MCP connector: set %s to a command that prints the document" % READER
        if url.startswith(("http://", "https://")):
            with urllib.request.urlopen(url, timeout=20) as page:
                return page.read().decode("utf-8", "replace"), None
        return None, "not a path or an http(s) link"
    except Exception as error:
        return None, "%s: %s" % (type(error).__name__, str(error)[:80])


def out(env, *args, **kw):
    """(ok, text) of gh ($LOOP_GH) or the PRD writer ($LOOP_PRD_WRITER: `WRITER SOURCE comment|replace ID|remove ID`,
    text on stdin). Never raises."""
    cmd = os.environ.get(env) or ("gh" if env == "LOOP_GH" else "")
    if not cmd:
        return False, "set %s to the command that writes to the document" % env
    try:
        done = subprocess.run(cmd.split() + list(args), capture_output=True, text=True, timeout=120, **kw)
    except (OSError, subprocess.SubprocessError) as error:
        return False, str(error)[:100]
    return done.returncode == 0, (done.stdout if done.returncode == 0 else done.stderr).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    item = sub.add_parser("new")
    item.set_defaults(func=cmd_new)
    for name in ("name", "idea"):
        item.add_argument(name)
    for name in ("--paths", "--prefix"):
        item.add_argument(name, default="")
    item = sub.add_parser("convert")
    item.add_argument("--write", action="store_true")
    item.set_defaults(func=cmd_convert)
    item = sub.add_parser("skeleton")
    item.add_argument("path")
    item.set_defaults(func=cmd_skeleton)
    for name in ("--title", "--problem", "--requirement"):
        item.add_argument(name, required=True)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
