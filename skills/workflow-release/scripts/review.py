#!/usr/bin/env python3
"""The review hold (DEL-13, issue 3803) and the hard-release gate (REL-1 to REL-8, issue 4914).

usage: review.py record SLUG
       review.py gate vX [--ref REF] [--no-suite]   |   review.py promote vX --owner-record ID [--ref REF]
       review.py revert vX

With "review_hold": true, merge.py merges a goal only after the operation session has recorded that it read the diff.

record stores the pull request's head as the reviewed one; a later push moves the head, so the hold applies again. Only
the operation role records: LOOP_ROLE=worker, or a path inside a goal worktree, is refused and nothing is written.
Until a review of the current head is recorded merge.py refuses with REVIEW_HOLD; the goal stays done and `review_wait`
puts "merge waiting on review" on the board and in the check-in. It runs git and gh and nothing else.
"""
import glob
import importlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import release  # noqa: E402
os.environ.setdefault("GIT_TERMINAL_PROMPT", "0")


def worker():
    """True for a worker or a path inside a goal worktree, where a goal could record its own review."""
    common = release.git("rev-parse", "--path-format=absolute", "--git-common-dir", check=False)
    inside = os.path.join(os.path.normcase(os.path.realpath(common)), "loop", "worktrees") + os.sep
    return os.environ.get("LOOP_ROLE") == "worker" or os.path.normcase(os.path.realpath(os.getcwd())).startswith(inside)


def held(cfg, state, head):
    """"" when merging may go ahead, else the REVIEW_HOLD refusal: the setting is on and HEAD has no recorded review."""
    if cfg.get("review_hold") is not True:
        return ""
    if head and (state.get("review") or {}).get("head") == head:
        state.pop("review_wait", None)
        return ""
    return ("REFUSED (REVIEW_HOLD): review_hold is on and no review of the pull request head %s is recorded; nothing was merged. "
            "Fix: the operation session reads the diff, then review.py record %s, then merge.py %s." % (
                (head or "unknown")[:12], state["slug"], state["slug"]))


def wait(state):
    """Mark the goal as a merge waiting on review (exit 5)."""
    state["review_wait"] = True
    release.save(state, "merge waiting on review (REVIEW_HOLD)")
    return 5


def record(slug):
    if worker():
        sys.exit("REFUSED: only the operation session records a review; a worker or a goal worktree cannot. Nothing was recorded. "
                 "Fix: from the main checkout, as the operation session, run review.py record %s. (REVIEW_ROLE)" % slug)
    state = release.load(slug)
    seen = release.run(["gh", "pr", "view", state.get("pr") or "", "--json", "headRefOid"])
    head = json.loads(seen.stdout or "{}").get("headRefOid") if seen.returncode == 0 else None
    if not state.get("pr") or not head:
        sys.exit("REFUSED: %s has no open pull request to review. Fix: goal.py pr %s first." % (slug, slug))
    state["review"] = {"head": head, "at": release.now()}
    state.pop("review_wait", None)
    release.save(state, "review recorded for pull request head %s by the operation session" % head[:12])
    print("REVIEW RECORDED %s at %s" % (slug, head[:12]))
    return 0


def main():
    args = sys.argv[1:]
    if args[:1] in (["-h"], ["--help"]):
        print(__doc__)
        return 0
    if args[:1] == ["record"] and len(args) == 2:
        return record(args[1])
    if args[:1] in (["gate"], ["promote"], ["revert"]) and len(args) > 1:
        return gate_cli(args)
    sys.exit(__doc__)


def proven(top):
    """Row ids with a PASS on the current commit in any lane record of this repo (loop/tests/*.json in the git common folder).
    regression-runs.tsv holds no commit, so a PASS there is not trusted: a row that passed on an older commit runs again."""
    head = release.git("rev-parse", "HEAD", cwd=top, check=False)
    common = release.git("rev-parse", "--path-format=absolute", "--git-common-dir", cwd=top, check=False)
    found = set()
    for path in glob.glob(os.path.join(common, "loop", "tests", "*.json")):
        try:
            rows = json.load(open(path)).get("rows") or {}
        except (OSError, ValueError, AttributeError):
            continue
        found |= {key for key, item in rows.items() if isinstance(item, dict) and item.get("status") == "PASS" and item.get("commit") == head}
    return found


def left_text(left):
    """The LEFT section of the cut's output and release notes: the count and the ids, or '' when nothing was left."""
    return "\n## LEFT\n\nLEFT %d rows were not run before the cut's stop: %s\n" % (len(left), ", ".join(left)) if left else ""


def criteria(top, cfg, doc_rows, fails):
    """(unmet, left): requirements with no passing row, and the rows the cut did not run before its stop (900 seconds, or
    LOOP_CUT_SECONDS). A row is skipped when it is known failing or has a PASS on the current commit; the rest run until the stop."""
    seconds = float(os.environ.get("LOOP_CUT_SECONDS") or 900)
    try:
        rows = [line.rstrip("\n").split("\t") + [""] * 5 for line in open(os.path.join(top, ".loop", "regression.tsv")) if line[0] != "#"]
    except OSError:
        rows = []
    out, left, stop, skip = [], [], time.time() + seconds, proven(top)
    try:
        skip |= {line.split("\t")[0] for line in open(os.path.join(top, ".loop", "regression-known.tsv")) if line[0] != "#"}
    except OSError:
        pass
    for page in doc_rows(top):
        try:
            part = (re.split(r"\n## (?:Requirements|Criteria)[ \t]*\n", re.sub(r"(?ms)^```.*?^```[^\n]*$", "", open(os.path.join(
                top, cfg.get("wiki_dir") or "docs/wiki", page + ".md")).read()), maxsplit=1) + [""])[1].split("\n## ")[0]
        except OSError:
            continue
        for key in re.findall(r"^- ([A-Z]{2,5}-\d+): \S", part, re.M):
            found = [r for r in rows if key in (r[0], r[3])]
            out += ["%s (no regression row)" % key] * (not found)
            for row in found:
                if row[1] == "covered" or row[0] in skip:
                    continue
                if row[1] != "draft" and time.time() >= stop:
                    left.append(row[0])
                elif row[1] == "draft" or fails(row[2], top):
                    out.append("%s (row %s is a draft or failing)" % (key, row[0]))
                else:
                    skip.add(row[0])
    return out, left


# ---- the hard-release gate (REL-1 to REL-8) ----
RC = re.compile(r"^v(\d+)\.0\.0-rc\.\d+$")
NL = chr(10)
OK = lambda args, cwd: release.run(["git", "rev-parse", "-q", "--verify"] + args, cwd=cwd).returncode == 0  # noqa: E731


def common_of(top):
    return os.path.join(release.git("rev-parse", "--path-format=absolute", "--git-common-dir", cwd=top, check=False), "loop")


def table(top, name):
    try:
        return [l.split("\t") + [""] * 5 for l in open(os.path.join(common_of(top), name)).read().splitlines() if l[:1] != "#"]
    except OSError:
        return []


def waivers(top, kind):
    """{subject: detail} of release-waivers.tsv rows whose owner-words record names the subject."""
    said = {r[0]: (r[3] + r[4]).lower() for r in table(top, "owner-words.tsv")}
    return {r[1]: r[2] for r in table(top, "release-waivers.tsv") if r[0] == kind and r[2] and r[1].lower().lstrip("#") in said.get(r[3], "-")}


def gh_json(*args):
    done = release.run(["gh"] + list(args) + ["--json", "number,title", "--limit", "500"])
    try:
        return json.loads(done.stdout) if done.returncode == 0 else None
    except ValueError:
        return None


def check_reviews(work, cfg):
    out, counts = [], {}
    for page in release.doc_rows(work):
        try:
            text = re.sub(r"(?ms)^```.*?^```[^\n]*$", "", open(os.path.join(work, cfg.get("wiki_dir") or "docs/wiki", page + ".md")).read())
        except OSError:
            continue
        found = re.findall(r"^- ([A-Z]{2,5}-\d+): \*\*(Unreviewed|Reviewed)", text, re.M)
        counts[page] = [sum(m == "Reviewed" for _, m in found), sum(m == "Unreviewed" for _, m in found)]
        out += [("reviews", "%s (%s) is not Reviewed" % (k, page), [k]) for k, m in found if m == "Unreviewed"]
    return out, counts


def run_in(work, script, *args):
    path = os.path.join(work, "skills", script)
    try:
        return subprocess.run([sys.executable, path] + list(args), cwd=work, capture_output=True, text=True,
                              timeout=int(os.environ.get("LOOP_GATE_SECONDS") or 14400)).stdout if os.path.exists(path) else ""
    except subprocess.TimeoutExpired:
        return ""


def check_suite(work, red):
    """REL-3: a FAIL, NOTRUN, ENV, KNOWN or budget-LEFT row refuses unless a red waiver names its issue."""
    text = run_in(work, "workflow-regression/scripts/regression.py", "run", "nightly")
    rows = re.findall(r"^(PASS|FAIL|KNOWN|NOTRUN|ENV) (\S+)", text, re.M)
    rows += [("LEFT", "budget-left")] * bool(re.search(r"^BUDGET .*LEFT [1-9]", text, re.M))
    tally = {k: sum(s == k for s, _ in rows) for k in ("PASS", "FAIL", "KNOWN", "NOTRUN", "ENV", "LEFT")}
    if not rows:
        return [("suite", "the suite did not run", ["suite"])], tally
    return [("suite", "row %s is %s with no owner waiver naming an issue" % (r, s), [r]) for s, r in rows if s != "PASS" and r not in red], tally


def check_health(work):
    text = run_in(work, "workflow-health/scripts/health.py", "check")
    verdict = ([l for l in text.splitlines() if l.startswith("HEALTH:")] or ["HEALTH: not run"])[-1]
    return ([] if verdict == "HEALTH: green" else [("health", verdict, ["health"])]), verdict


def gate_refusals(top, cfg, ver, ref, suite=True):
    """([(check, subject, keys)], facts): the five checks on ref, saved to loop/gate/vX.json."""
    work, moved, base = tempfile.mkdtemp(prefix="gate-"), waivers(top, "moved"), release.base_of(top, cfg)
    got = gh_json("issue", "list", "--milestone", "v%d.0" % ver, "--state", "open")
    out = [("issues", "#%d %s" % (i["number"], i["title"][:60]), ["#%d" % i["number"]]) for i in got or [] if "#%d" % i["number"] not in moved]
    out += [("issues", "gh could not list milestone v%d.0" % ver, ["gh"])] * (got is None)
    facts = {"ref": ref, "suite": {}, "health": "skipped (--no-suite)"}
    if release.run(["git", "worktree", "add", "-q", "--detach", work, ref], cwd=top).returncode:
        out += [("ref", "cannot check out " + ref, ["ref"])]
    else:
        try:
            bad, facts["reqs"] = check_reviews(work, cfg)
            pages = list(release.doc_rows(work))
            out += bad + [("docs", l.strip()[:100], [p for p in pages if p in l] or ["docs"]) for l in release.docs_trouble(work, base, whole=True)]
            if suite:
                for key, bad in (("suite", check_suite(work, waivers(top, "red"))), ("health", check_health(work))):
                    out += bad[0]
                    facts[key] = bad[1]
        finally:
            release.run(["git", "worktree", "remove", "--force", work], cwd=top)
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(os.path.join(common_of(top), "gate"), exist_ok=True)
    json.dump({"ref": ref, "at": release.now(), "refusals": out}, open(os.path.join(common_of(top), "gate", "v%d.json" % ver), "w"))
    return out, facts


def frozen(top, head, slug):
    """REL-5: "" or FROZEN: from a major's rc tag until its release tag a goal merges only if its goal file names a gate subject."""
    live = sorted({int(m.group(1)) for m in map(RC.match, release.git("tag", "--list", "v*.0.0-rc.*", cwd=top, check=False).split())
                   if m and not OK(["refs/tags/v%s.0.0" % m.group(1)], top)})
    if not live:
        return ""
    try:
        keys = [k for r in json.load(open(os.path.join(common_of(top), "gate", "v%d.json" % live[-1])))["refusals"] for k in r[2]]
    except (OSError, ValueError, KeyError, IndexError):
        keys = []
    text = release.run(["git", "show", "%s:.loop/goals/%s.md" % (head, slug)], cwd=top).stdout
    if any(re.search(r"(?<![\w-])%s(?![\w-])" % re.escape(k), text) for k in keys):
        return ""
    return ("REFUSED (FROZEN): frozen for v%d.0.0: only a fix for a gate failure merges, and %s names none of %s. Nothing was merged." % (
        live[-1], slug, ", ".join(keys[:6]) or "(no gate run: review.py gate v%d)" % live[-1]))


def email(top, subject, text):
    """"" when mailed, else why not (the secrets come from mail.env, as notify.py reads it)."""
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "workflow-monitoring", "scripts"))
    try:
        notify = importlib.import_module("notify")  # another skill's script: no static import
        os.environ.update(notify.load_env()[0] or {})
        mail = notify.mailer()
        mode, host, port, wait, api = mail.settings(top)
        done = mail.deliver(mode, mail.secrets(mode, False), subject, text, "<pre>%s</pre>" % text.replace("<", "&lt;"), (host, port, wait, api)) if mode != "off" else ("off",) * 2
        return "" if done[0] == "ok" else "%s: %s" % done[:2]
    except Exception as err:  # noqa: BLE001 - a mail failure never undoes a promotion
        return str(getattr(err, "text", err))[:200]


def state_report(top, ver, tag, sha, facts):
    prior = ([t for t in release.git("tag", "--list", "v*.0.0", "--sort=-v:refname", cwd=top, check=False).split() if t != tag] or [""])[0]
    closed = gh_json("issue", "list", "--milestone", "v%d.0" % ver, "--state", "closed") or []
    reqs = ["- %s: %d Reviewed, %d Unreviewed" % (p, c[0], c[1]) for p, c in sorted(facts.get("reqs", {}).items())]
    log = release.git("log", "--format=- %h %s", prior + ".." + sha if prior else sha, cwd=top, check=False).splitlines()[:60]
    return NL.join(["# State report: " + tag, "Commit %s from %s; every gate check passed." % (sha[:12], facts["ref"]), "## Requirements"] + reqs
                   + ["## Tests", ", ".join("%d %s" % (n, k) for k, n in facts["suite"].items()), "## Health", facts["health"], "## Closed issues"]
                   + ["- #%d %s" % (i["number"], i["title"]) for i in closed] + ["## Changes since " + (prior or "the start")] + log) + NL


def promote(top, cfg, ver, rec, ref):
    tag, rel, base = "v%d.0.0" % ver, "release/v%d" % ver, cfg.get("base", "main")
    if tag not in re.split(r"[,\s]+", " ".join(r[4] for r in table(top, "owner-words.tsv") if r[0] == rec)) or OK(["refs/tags/" + tag], top):
        sys.exit("REFUSED (OWNER_RECORD): owner-words record %r must name %s, and %s must not exist. Nothing changed." % (rec, tag, tag))
    bad, facts = gate_refusals(top, cfg, ver, ref)
    if bad:
        print(NL.join("GATE REFUSED v%d.0 (%s): %s" % (ver, c, s) for c, s, _ in bad) + NL + "NOT PROMOTED %s: no tag, branch or release." % tag)
        return 1
    sha = release.git("rev-parse", ref + "^{commit}", cwd=top)
    text, path = state_report(top, ver, tag, sha, facts), os.path.join(common_of(top), "gate", tag + ".md")
    open(path, "w").write(text)
    release.git("tag", "-a", tag, sha, "-m", "Release " + tag, cwd=top)
    release.git("branch", rel, sha, cwd=top)
    for push in (["origin", "%s:refs/heads/%s" % (sha, base)], ["origin", tag, rel]):
        done = release.run(["git", "push"] + push, cwd=top)
        if done.returncode:
            for undo in ([["tag", "-d", tag], ["branch", "-D", rel]] if push[1] != tag else []):  # nothing remote changed yet
                release.run(["git"] + undo, cwd=top)
            sys.exit("REFUSED (PROMOTE_PUSH): git push failed: " + done.stderr.strip()[-200:])
    made = release.run(["gh", "release", "create", tag, "--title", tag, "--notes-file", path, "--verify-tag"], cwd=top)
    for subject, later in waivers(top, "moved").items():
        release.run(["gh", "issue", "edit", subject.lstrip("#"), "--milestone", later], cwd=top)
    why = email(top, "Release " + tag, text)
    print("PROMOTED %s: tag, branch %s, main moved to %s; report %s%s" % (tag, rel, sha[:12], path, "" if made.returncode == 0 else " (gh release create failed)"))
    print("EMAILED %s" % tag if not why else "EMAIL not sent: %s. Fix: mail %s" % (why, path))
    return 0


def revert(top, cfg, ver):
    """REL-7: a pull request putting main's tree back on release/vX."""
    rel, base = "release/v%d" % ver, cfg.get("base", "main")
    release.run(["git", "fetch", "-q", "origin", rel, base], cwd=top)
    snap = next((n for n in ("origin/" + rel, rel) if OK([n], top)), "")
    if not snap:
        sys.exit("REFUSED: no snapshot branch " + rel)
    name, body = "revert/v%d-%s" % (ver, time.strftime("%Y%m%d%H%M%S", time.gmtime())), os.path.join(common_of(top), "gate", "revert.md")
    release.git("push", "origin", "%s:refs/heads/%s" % (release.git("commit-tree", snap + "^{tree}", "-p", "origin/" + base, "-m",
                                                                     "Revert to v%d" % ver, cwd=top), name), cwd=top)
    os.makedirs(os.path.dirname(body), exist_ok=True)
    open(body, "w").write("Puts `%s` back on the tree of `%s`, the snapshot of v%d.0.0." % (base, rel, ver) + NL)
    done = release.run(["gh", "pr", "create", "--base", base, "--head", name, "--title", "Revert main to v%d" % ver, "--body-file", body], cwd=top)
    if done.returncode:
        sys.exit("REFUSED: gh could not open the pull request (%s is pushed): %s" % (name, done.stderr.strip()[-160:]))
    print("REVERT PR %s: %s holds the tree of %s" % (done.stdout.strip(), name, rel))
    return 0


def gate_cli(args):
    spec, rest = re.match(r"^v?(\d+)(\.0)?(\.0)?$", args[1]), args[2:]
    if not spec:
        sys.exit("REFUSED: give the major as vX, for example v2.")
    ver, top = int(spec.group(1)), release.git("rev-parse", "--show-toplevel")
    cfg, opt = release.read_config(top), lambda flag: rest[rest.index(flag) + 1] if flag in rest[:-1] else ""
    if args[0] != "gate" and worker():
        sys.exit("REFUSED (REVIEW_ROLE): only the operation session does this, on the owner's words.")
    if args[0] == "revert":
        return revert(top, cfg, ver)
    tags = release.git("tag", "--list", "v%d.0.0-rc.*" % ver, "--sort=-v:refname", cwd=top, check=False).split()
    ref = opt("--ref") or (tags + [n for n in ("origin/staging", release.base_of(top, cfg)) if OK([n], top)] + ["HEAD"])[0]
    if args[0] == "promote":
        return promote(top, cfg, ver, opt("--owner-record"), ref)
    bad, _ = gate_refusals(top, cfg, ver, ref, "--no-suite" not in rest)
    print(NL.join("GATE REFUSED v%d.0 (%s): %s" % (ver, c, s) for c, s, _ in bad) or "GATE PASS v%d.0" % ver)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
