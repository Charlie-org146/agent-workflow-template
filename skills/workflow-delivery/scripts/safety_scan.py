#!/usr/bin/env python3
"""DLF-1.3's safety classes (E7, CEO B1, E10): one scan for a stop's words and one for a diff. Both report every class that
matches. No match is never proof of safety for an action: it is held under operation. A changed Reviewed requirement is
found from the requirement units themselves, not from the page's path. The diff is read with external tools off, and one
that can't be read refuses. Standard library only."""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dlf  # noqa: E402
os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")

DELETE, MONEY, SECURITY, PRIVATE, STEWARD, PROMISE, TESTS = dlf.SAFETY
GONE = r"(delet|remov|purg|wip|truncat|eras|destroy|discard|overwrit)\w*"
WHAT = r"(repo|repositor\w+|branch\w*|backups?|releases?|history|databases?|tables?|tags?|issues?|files?|folders?|director\w+|data|logs?|records?|worktrees?|accounts?|buckets?)"
# beside dlf's words: the same classes in the other ways people write them
MORE = {DELETE: (r"\b%s\b[^.;]{0,60}\b%s\b" % (GONE, WHAT), r"\b%s\b[^.;]{0,60}\b(is|are|gets?|being|be)\s+%s\b" % (WHAT, GONE),
                 r"\b(rm\s+-[a-z]*r|reset\s+--hard|push\s+(-f|--force)|force[- ]push)"),
        MONEY: (r"\b(pay|pays|paying|paid|buy|buys|buying|bought|billed|subscri\w+|checkout|refunds?)\b", r"\bcharg\w+\b[^.;]{0,30}\b(card|account)\b",
                r"\bcredit card\b|\$\s?\d|\b(costs?|spends?) money\b"),
        SECURITY: (r"\b(permissions?|ssh key|private key|firewall|network access)\b",),
        STEWARD: (r"\badmin[- ]merg\w*|\bmerg\w+\b[^.;]{0,50}\bas steward\b|\bbypass\w*\b[^.;]{0,50}\b(required check|branch protection)s?\b",
                  r"--admin\b"),
        TESTS: (r"\b(remov|delet|disabl|drop|skip|comment\w* out)\w*\b[^.;]{0,40}\b(tests?|assert\w*|checks?|regression rows?)\b",)}
# added lines of a diff: only wording that names an act, since a script's ordinary words are no act
ACTS = {DELETE: r"\brm\s+-[a-z]*r|\breset\s+--hard\b|\bpush\b[^\n]*(\s-f\b|--force)|\bDROP\s+(TABLE|DATABASE)\b|\brmtree\(|--delete-branch\b",
        STEWARD: r"--admin\b|\bpr\b[^\n]{0,20}\bmerge\b[^\n]*--(admin|auto)\b|enqueuePullRequest",
        MONEY: r"\b(stripe|paypal|braintree)\b",
        SECURITY: r"bypass[-_ ]?permissions|dangerously[-_]skip|--no-sandbox\b|danger-full-access"}
SETTINGS = (dlf.PATHS[SECURITY], r"^\.loop/config\.json$|^\.loop/permissions\.tsv$")
# a page's requirement line: mark (with its date), heading, and the seal comment a review leaves
UNIT = re.compile(r"^- ([A-Z]{2,5}-\d+): \*\*(Unreviewed|Reviewed(?: \d{4}-\d\d-\d\d)?)\*\* (.*?)(?: <!-- reviewed \w+ -->)?$")
PAGES = "docs/wiki/"
OUTSIDE = "text-outside-a-unit"
# a requirement sentence ends in its tag; one indented where no unit holds it is no ordinary note
TAGGED = re.compile(r"\[[A-Z]{2,5}-\d+\]\s*$")


def text_classes(text, paths=(), label=""):
    """Every class the words, the named files or a label point to; a label only adds."""
    words = " ".join(str(text).split())
    hit = {name for name in dlf.SAFETY
           if re.search(dlf.WORDS[name], words, re.I) or any(re.search(p, words, re.I) for p in MORE.get(name, ()))}
    re.search(dlf.SECRET, words) and hit.add(PRIVATE)
    any(re.search(pattern, path) for pattern in SETTINGS for path in paths) and hit.add(SECURITY)
    label in dlf.SAFETY and hit.add(label)
    return [name for name in dlf.SAFETY if name in hit]


def action(text, paths=(), label=""):
    """CEO B1: an action is safety when a class matches and unknown otherwise; nothing here clears one. Only operation may
    rule an unknown action not safety, with a reason that is listed."""
    classes = text_classes(text, paths, label)
    return {"state": "safety" if classes else "unknown", "classes": classes}


def units(text, reviewed=False):
    """{ID: unit text} of a page's requirements, or of its Reviewed ones: the heading and the indented lines under it,
    without the mark, its date or the seal, so the text alone is compared."""
    found, current = {}, None
    for line in text.split("\n"):
        start = UNIT.match(line.rstrip())
        if start:
            current = None if reviewed and start.group(2) == "Unreviewed" else start.group(1)
            if current:
                found[current] = start.group(3)
        elif current and line.startswith("  ") and line.strip():
            found[current] += "\n" + line.rstrip()
        else:
            current = None
    return found


def reviewed_units(text):
    return units(text, True)


def outside(text):
    """Tagged indented lines that no requirement's unit holds."""
    found, current = set(), False
    for line in text.split("\n"):
        if UNIT.match(line.rstrip()):
            current = True
        elif not (current and line.startswith("  ") and line.strip()):
            current = False
            line.startswith("  ") and TAGGED.search(line) and found.add(line.strip())
    return found


def changed_units(before, after):
    """IDs whose Reviewed text changed: reviewed before and now different or gone, or reviewed now with new text."""
    gone = {key for key, text in reviewed_units(before).items() if units(after).get(key) != text}
    new = {key for key, text in reviewed_units(after).items() if units(before).get(key) != text}
    return sorted(gone | new) + ([OUTSIDE] if outside(after) - outside(before) else [])


def sections(diff):
    """(path, deleted, removed lines, added lines) for each file of a diff."""
    for part in re.split(r"^(?=diff --git )", diff, flags=re.M):
        head = re.match(r"diff --git \"?a/(.*?)\"? \"?b/(.*?)\"?\n", part)
        if head:
            body = part.split("\n@@", 1)
            lines = body[1].split("\n") if len(body) > 1 else []
            yield (head.group(2), bool(re.search(r"^deleted file mode", body[0], re.M)),
                   [x[1:] for x in lines if x.startswith("-")], [x[1:] for x in lines if x.startswith("+")])


def diff_classes(diff, units=()):
    """{class: files} for every class a diff can show; `units` are the (page, ID) pairs whose Reviewed text changed."""
    found = {}

    def hit(name, path):
        path in found.setdefault(name, []) or found[name].append(path)

    for path, deleted, removed, added in sections(diff):
        test, page = re.search(dlf.TESTS, path), path.endswith(".md")
        if test and (deleted or any(x.strip() for x in removed) or any(re.search(dlf.SKIP, x) for x in added)):
            hit(TESTS, path)
        any(re.search(pattern, path) for pattern in SETTINGS) and hit(SECURITY, path)
        any(re.search(dlf.SECRET, x) for x in added) and hit(PRIVATE, path)
        if not (test or page):  # tests and pages describe these acts; scripts and workflows do them
            for name, pattern in ACTS.items():
                any(re.search(pattern, x, re.I) for x in added) and hit(name, path)
    for page, _ in units:
        hit(PROMISE, page)
    return found


def git(top, *args):
    try:
        got = subprocess.run(["git", "-c", "core.quotepath=off"] + list(args), cwd=top, capture_output=True, timeout=120)
    except (OSError, subprocess.SubprocessError) as error:
        sys.exit("REFUSED: the diff can't be read: %s. Fix: repair the repository, then run it again (ONE_REVIEW_DIFF)" % error)
    return got.returncode, got.stdout.decode("utf-8", "replace")


def read_diff(top, base, head):
    """(diff text, changed Reviewed units) of base...head, external diff and text filters off, every file read as text."""
    def must(*args):
        code, out = git(top, *args)
        code and sys.exit("REFUSED: git %s of %s...%s failed, so the diff is unread. Fix: fetch both commits, then run it "
                          "again (ONE_REVIEW_DIFF)" % (args[0], base[:12], head[:12]))
        return out
    start = must("merge-base", base, head).strip()
    quiet = ("--no-ext-diff", "--no-textconv", "--no-renames", "--no-color")
    text = must("diff", "--text", *quiet, start, head)
    changed = []
    for path in [p for p in must("diff", "-z", "--name-only", *quiet, start, head).split("\0") if p]:
        if not (path.startswith(PAGES) and path.endswith(".md")):
            continue
        before, after = (out if not code else "" for code, out in
                         (git(top, "cat-file", "blob", "%s:%s" % (ref, path)) for ref in (start, head)))
        changed += [(path, ident) for ident in changed_units(before, after)]
    return text, changed
