"""A lane row this machine cannot run (GRD-11, #4492): told apart from a real failure, and one other-machine to-do per goal.

unrunnable(code, text): exit 127, or output saying a tool or a POSIX-only module is missing (`pnpm: command not found`,
`No module named 'fcntl'`). todo(root, slug, ids, live): the to-do issue on the rows' feature milestone, once per goal.
"""
import glob
import json
import os
import re

MISSING = re.compile(r"command not found|: not found|is not recognized as an internal|No module named '(fcntl|termios|pwd|grp|resource)'"
                     r"|spawn (node|pnpm|npm) ENOENT")
LABEL = "other-machine"


def unrunnable(code, text):
    return code == 127 or bool(code and MISSING.search(text or ""))


def milestone(root, ids):
    """The number of the feature milestone of the first page that lists one of ids, or ''."""
    for page in sorted(glob.glob(os.path.join(root, "docs", "wiki", "*.md"))):
        text = open(page, encoding="utf-8").read()
        found = re.search(r"^Milestone:\s*\S*/milestone/(\d+)", text, re.M)
        if found and any("(Tests#t-%s)" % key in text for key in ids):
            return found.group(1)
    return ""


def todo(root, slug, ids, live, gh):
    """File one to-do for goal slug listing ids; the same goal never files a second. Returns its url, or '' (dry run)."""
    stone = milestone(root, ids)
    if not live:
        print("WOULD open one to-do issue (milestone %s) for %s: %s" % (stone or "none", slug, ", ".join(ids)))
        return ""
    mark = "<!-- loop-notrun %s -->" % slug
    listed = gh("issue", "list", "--label", LABEL, "--state", "open", "--limit", "1000", "--json", "url,body")
    for item in [] if listed.returncode else json.loads(listed.stdout or "[]"):
        if mark in item.get("body", ""):
            return item["url"]
    title = gh("api", "repos/{owner}/{repo}/milestones/" + stone, "--jq", ".title").stdout.strip() if stone else ""
    gh("label", "create", LABEL, "--force", "--description", "A step only another machine can do")
    body = "%s\nGoal `%s` has rows its machine cannot run (a missing tool or a POSIX-only module). On a machine that can, run " \
           "`regression.py run ID` for each, then close this. It never blocks the goal.\n\n%s\n" % (
               mark, slug, "\n".join("- `%s`" % key for key in ids))
    made = gh("issue", "create", "--title", "To do on another machine: run %d rows of %s" % (len(ids), slug), "--label", LABEL,
              *(("--milestone", title) if title else ()), body=body)
    return made.stdout.strip().splitlines()[-1] if made.returncode == 0 and made.stdout.strip() else ""
