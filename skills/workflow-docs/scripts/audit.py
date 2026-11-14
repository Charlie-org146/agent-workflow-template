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


def own_touched(root, ref, paths, head="HEAD"):
    """True when the goal's diff (merge-base of ref and head, to head) touches any of the page's mapped paths."""
    out = own_git(root, "diff", "--name-only", ref + "..." + head, "--", *paths)
    return out is None or bool(out)  # no diff answer: judge the page as the goal's own


def own_split(root, found, notes, rows, name="main", head="HEAD"):
    """(found, notes) with each STALE line of an untouched mapped page moved to notes as FINDING. head: the goal's branch
    when this runs somewhere else, such as the main checkout, where HEAD is the base itself."""
    ref = own_base(root, name)
    if not ref or own_git(root, "merge-base", "--is-ancestor", head, ref) is not None:
        return found, notes  # no base, or on the base branch itself (main's own run keeps every STALE)
    keep, moved = [], []
    for item in found:
        if item[0] == "STALE" and item[1] in rows and item[2][:1].isdigit() and not own_touched(root, ref, rows[item[1]], head):
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


SYNC_MARK = "<!-- prd-sync: owned -->"
def put(path, source, have, base):
    """Write the copy (SYNC_MARK, `- ID: text` lines) and its baseline .base (`ID<TAB>sha8` of the agreed text)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(SYNC_MARK + "\n<!-- source: %s -->\n" % source + "".join("- %s: %s\n" % item for item in have.items()))
    with open(path[:-3] + ".base", "w", encoding="utf-8", newline="\n") as handle:
        handle.write("".join("%s\t%s\n" % item for item in sorted(base.items(), key=lambda x: counting.req_key(x[0]))))


def mirror_of(path):
    """({id: text}, owned, {id: sha8 agreed}) of the repo's copy: owned unless another file is there (never touched)."""
    try:
        with open(path, encoding="utf-8") as handle:
            lines = handle.read().replace("\r\n", "\n").split("\n")
    except OSError:
        return {}, True, {}
    try:
        with open(path[:-3] + ".base", encoding="utf-8") as handle:
            agreed = dict(x.split("\t") for x in handle.read().split("\n") if "\t" in x)
    except OSError:
        agreed = {}
    return {m.group(1): m.group(2) for m in (re.match(r"- ([A-Z]{2,5}-\d+): (.*)$", x) for x in lines) if m}, lines[0] == SYNC_MARK, agreed


def sha(text):
    return None if text is None else criteria.seal(text)


def out(env, *args, **kw):
    """(ok, text) of gh ($LOOP_GH) or the PRD writer ($LOOP_PRD_WRITER, an agent's Notion connector: `WRITER SOURCE comment|replace
    ID|remove ID`, text on stdin). Never raises."""
    cmd = os.environ.get(env) or ("gh" if env == "LOOP_GH" else "")
    if not cmd:
        return False, "set %s to the command that writes to the document" % env
    try:
        done = subprocess.run(cmd.split() + list(args), capture_output=True, text=True, timeout=120, **kw)
    except (OSError, subprocess.SubprocessError) as error:
        return False, str(error)[:100]
    return done.returncode == 0, (done.stdout if done.returncode == 0 else done.stderr).strip()


def sync(root, dry=False, accept=(), opened=False):
    """Compare each external PRD with the repo's copy, .loop/prd/<Page>.md, against what both last agreed on. A difference is a
    DELTA (page, id, side, both texts) and sync overwrites neither side: it posts each new one as a GitHub issue and a comment
    on the external page, and --accept PAGE:ID=repo|source writes that side's text, that id only, to the other side and closes
    the issue. --dry-run posts and writes nothing (exit 1 with a delta). An unreachable source, gh or writer is `not connected`."""
    held = counting.ledger(root)
    if opened:
        print("".join("DELTA %s %s changed (review: %s)\n" % (k.replace(":", ": "), v[0], v[1]) for k, v in held.items()), end="")
        return 0
    listed = [(p, s) for p, s in sorted(counting.sources(root).items()) if s.startswith(("url:", "mcp:")) and re.fullmatch(r"\w[\w-]*", p)]
    if not listed:
        print("NO EXTERNAL PRDS: no feature's PRD source in .loop/docs.tsv is a url or an mcp source")
    same = new = away = 0
    for page, source in listed:
        body, why = prd.read_link(source)
        if body is None:
            print("not connected: %s (%s): %s" % (page, source, why))
            away += 1
            continue
        want, path = counting.requirements(body), os.path.join(root, ".loop", "prd", page + ".md")
        have, owned, agreed = mirror_of(path)
        if not want:
            print("EMPTY %s: the source states no requirement ids; the repo copy is kept" % page)
            continue
        if not owned:
            print("SKIPPED %s: %s is not a file sync wrote; it is left as it is" % (page, os.path.relpath(path, root)))
            continue
        if not os.path.exists(path):  # the first sync adopts the source: nothing to compare yet
            if not dry:
                put(path, source, want, {i: sha(t) for i, t in want.items()})
                print("SYNCED %s: %d requirement(s) from %s" % (page, len(want), source))
            continue
        for item in (a for a in accept if not dry and a.split(":")[0] == page):
            ident, _, side = item.partition(":")[2].partition("=")
            r, s = have.get(ident), want.get(ident)
            keep = r if side == "repo" else s  # the text both sides will hold
            if r == s or side not in ("repo", "source"):
                print("NO DELTA %s: %s (nothing to accept for %s)" % (page, ident, item))
                continue
            ok, why = out("LOOP_PRD_WRITER", source, "replace" if r else "remove", ident, input=r or "") if side == "repo" else (True, "")
            if not ok:
                print("not connected: %s (%s): %s" % (page, source, why))
                continue
            for side_of in (want, have):
                if keep:
                    side_of[ident] = keep
                else:
                    side_of.pop(ident, None)
            agreed[ident] = sha(keep) or ""
            put(path, source, have, {i: h for i, h in agreed.items() if h})
            row = held.pop("%s:%s" % (page, ident), None)
            if row:
                out("LOOP_GH", "issue", "close", row[1], "--comment", "Accepted the %s's text; both sides now say the same." % side)
            print("ACCEPTED %s: %s, the %s's text is on both sides" % (page, ident, side))
        found = []
        for ident in sorted(set(have) | set(want), key=counting.req_key):
            r, s = have.get(ident), want.get(ident)
            if r != s:
                b = agreed.get(ident) or None
                found.append((ident, "both sides" if (sha(r) != b) == (sha(s) != b) else "the repo" if sha(r) != b else "the source", r, s))
        fresh = {i: sha(have[i]) for i in have if have[i] == want.get(i)}
        fresh.update({i: agreed[i] for i, *_ in found if i in agreed})
        if fresh != agreed and not dry:
            put(path, source, have, fresh)
        same, new = same + (not found), new + len(found)
        for ident, side, r, s in found:
            print("DELTA %s: %s %s changed (repo: %s | source: %s)" % (page, ident, side, (r or "<none>")[:160], (s or "<none>")[:160]))
        if dry:
            continue
        for key in [k for k in held if k.startswith(page + ":") and k.split(":")[1] not in [f[0] for f in found]]:
            out("LOOP_GH", "issue", "close", held.pop(key)[1], "--comment", "Both sides now say the same.")
        for ident, side, r, s in found:
            key, text = "%s:%s" % (page, ident), "Delta in %s %s: %s changed.\nRepo copy: %s\nSource: %s\nAccept one side with: docs.py sync --accept %s:%s=repo or =source" % (
                page, ident, side, r or "<none>", s or "<none>", page, ident)
            row = held.get(key) or [side, "", "0", ""]
            if row[1] and row[3] != sha(text):
                out("LOOP_GH", "issue", "comment", row[1], "--body", "The delta changed.\n" + text)
                row[2] = "0"
            elif not row[1]:
                for stone in (["--milestone", page], []):  # the page's milestone is named like it; without one the issue is still made
                    ok, made = out("LOOP_GH", "issue", "create", "--title", "DELTA %s %s: %s changed" % (page, ident, side), "--body", text, *stone)
                    if ok:
                        break
                if not ok:
                    print("not connected: %s %s (gh): %s" % (page, ident, made[:100]))
                    away += 1
                    continue
                row[1] = made.split("\n")[-1]
            if row[2] != "1":
                ok, why = out("LOOP_PRD_WRITER", source, "comment", input=text)
                row[2] = "1" if ok else "0"
                print("POSTED %s %s: %s%s" % (page, ident, row[1], "" if ok else " (not connected to %s: %s)" % (source, why[:80])))
            held[key] = [side, row[1], row[2], sha(text)]
    if not dry:
        counting.ledger(root, held)
    print("SYNC: %d in step, %d with a delta, %d not connected" % (same, new, away))
    return 1 if dry and new else 0
