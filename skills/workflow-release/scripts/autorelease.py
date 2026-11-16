#!/usr/bin/env python3
"""The automatic release, called by merge.py: run the owner's routines, then after the merge bump the version once,
write the CHANGELOG entry, push that commit to the base branch and create a published GitHub release.

No draft, no question. Every failure is recorded on the goal as `release_error` (shown under Issues).
The bump is patch unless the owner recorded one (`goal.py set SLUG --bump minor|major`, read through workflow-delivery's
fit.py). The release commit and notes pass the private-name scan (workflow-delivery's private.py; missing or broken
refuses, PRIVATE_MODULE) before any push. A protected base (a `pull_request` rule, or a push refused for protection)
takes the release pull request instead (merge.py).
"""
import datetime
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

import release
import wiki  # noqa: E402

# a prompt from git or gh must fail, not block
os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")
if not sys.stdin or not sys.stdin.isatty():
    os.dup2(os.open(os.devnull, os.O_RDONLY), 0)

PUSH_TRIES = 3
SIBLING = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "workflow-delivery", "scripts"))
PROTECTED = re.compile(r"GH006|GH013|protected branch|through a pull request|rule violations", re.I)
LOADED = {}


def sibling(name):
    """(module, None), or (None, refusal) when the workflow-delivery module is missing or broken."""
    if name not in LOADED:
        path = os.path.join(SIBLING, name + ".py")
        try:
            spec = importlib.util.spec_from_file_location("delivery_" + name, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception as error:  # noqa: BLE001
            return None, ("workflow-delivery's %s.py could not be loaded from %s (%s: %s); nothing was pushed or merged"
                          % (name, path, type(error).__name__, "no such file" if isinstance(error, OSError) else str(error)[:120]),
                          "reinstall the skills, or put workflow-delivery beside workflow-release, then run it again", "PRIVATE_MODULE")
        LOADED[name] = module
    return LOADED[name], None


def private_check(top, base, texts, pushed=False, head="HEAD"):
    """None when the push may go on, else (why, fix, code). base None scans only texts."""
    private, stop = sibling("private")
    if stop:
        return stop
    try:
        result = private.scan(top, base, texts, head)
        stop = private.refusal(result, base or "the base branch", pushed)
    except Exception as error:  # noqa: BLE001
        return "the private-name scan failed (%s); nothing was pushed" % error, "run private.py check, then again", "PRIVATE_LIST"
    if not stop and result["state"] == "none":
        print("NOTE: " + result["note"])
    return stop


def check(state, top, base, texts, pushed=False, head="HEAD"):
    stop = private_check(top, base, texts, pushed, head)
    if stop:
        fail(state, "%s. Fix: %s (%s)" % stop)


def notes_text(state):
    bullets = "\n".join("- " + item for item in state["release_bullets"]) or "- No code changes"
    return bullets + "\n\n## How to verify\n\n%s\n\nPull request: %s\n" % (state["release_steps"], state.get("pr", ""))


def protected(top, base):
    """True when the base has a pull_request rule; a 403/404 or no rule says nothing."""
    got = sh(["gh", "api", "repos/{owner}/{repo}/rules/branches/" + base], cwd=top)
    try:
        rules = json.loads(got.stdout) if got.returncode == 0 else []
    except ValueError:
        return False
    return isinstance(rules, list) and any(isinstance(r, dict) and r.get("type") == "pull_request" for r in rules)


def sh(args, cwd=None):
    try:
        return subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    except OSError as error:
        return subprocess.CompletedProcess(args, 127, "", str(error))


def sh_text(args, text, flag="--body-file", cwd=None):
    """Run gh with a long text in a temp file passed as flag, never on the command line."""
    with tempfile.NamedTemporaryFile("w", suffix=".md", prefix="gh-text-", delete=False, encoding="utf-8", newline="\n") as f:
        f.write(text)
    try:
        return sh(args + [flag, f.name], cwd=cwd)
    finally:
        os.remove(f.name)


def fail(state, text):
    state["release_error"] = text if len(text) <= 400 else text[:330] + " ... " + text[-65:]  # keeps the (CODE)
    report, note = state.get("report"), ""
    if not isinstance(report, dict):  # a goal reset leaves report null
        note = "" if report is None else "(the stored report was a %s and was reset) " % type(report).__name__
        report = state["report"] = {}
    report["text"] = ("%s %sRelease failed: %s" % (str(report.get("text") or ""), note, text)).strip()[:600]
    if state.get("release") != "merged":  # the pull request is still open: resume can revive it
        state["status"] = "failed"
    release.save(state, "release failed: " + text[:200])
    sys.exit("REFUSED: " + text)


def reopen(state, code):
    """A merge refused because the head or base moved sends the goal back to its pr step."""
    state.update(status="running", step="pr")
    release.save(state, "merge refused (exit %d): run goal.py pr, then merge.py again" % code)
    return code


def mergeable(state):
    """merge.py's gate: a finished goal with its pull request, or one left failed with a release_error."""
    return bool(state.get("pr")) and (state.get("status") == "done" or (state.get("status") == "failed" and bool(state.get("release_error"))))


def mark_merged(state):
    state["release"] = "cut" if state.get("release") == "cut" else "merged"
    state["status"] = "done"


def run_routines(top, cfg, state):
    """Routines come from the base branch: a pull request cannot add a command the merge runs."""
    shown = sh(["git", "show", "origin/%s:.loop/config.json" % cfg.get("base", "main")], cwd=top)
    try:
        routines = (json.loads(shown.stdout) if shown.returncode == 0 else cfg).get("routines") or []
    except ValueError:
        routines = cfg.get("routines") or []
    for item in routines:
        argv = ["sh", "-c", item] if isinstance(item, str) else list(item)
        name = item if isinstance(item, str) else " ".join(item)
        done = sh(argv, cwd=top)
        if done.returncode:
            tail = (done.stderr or done.stdout).strip()[-200:]
            fail(state, "routine %s exited %d before the merge, so nothing was merged: %s" % (name, done.returncode, tail))
        print("ROUTINE ok: %s" % name)


def stage_notes(top, state, cfg):
    if "release_bullets" not in state:
        state["release_bullets"] = release.subjects(release.base_of(top, cfg), top) + wiki.fixes_lines(top)
        state["release_steps"] = release.verify_steps(top, state["slug"]) or "No manual steps were recorded."
        release.save(state)


def stage_part(top, state):
    """The bump, read on every run until the release commit exists (goal.py set --bump binds)."""
    if not state.get("release_part") or not (state.get("release_pushed") or state.get("release_pr")):
        part, reason = release.auto_need(top, state)
        state["release_part"], state["release_reason"] = ("patch", "a docs or test change") if part == "leave" else (part, reason)
        release.save(state)


def drop(top, tree, temp):
    sh(["git", "worktree", "remove", "--force", tree], cwd=top)
    shutil.rmtree(temp, ignore_errors=True)


def push_release_commit(top, cfg, state, part, to_branch=False):
    """(version, release commit sha); (None, stderr) when the base refused the push for protection. to_branch pushes
    to release/vX-<slug> instead (force-updating only it)."""
    base, slug = cfg.get("base", "main"), state["slug"]
    temp = tempfile.mkdtemp(prefix="release-")
    tree = os.path.join(temp, "tree")
    try:
        for _ in range(PUSH_TRIES):
            if sh(["git", "fetch", "-q", "origin", base], cwd=top).returncode:
                fail(state, "could not fetch origin/%s" % base)
            sh(["git", "worktree", "remove", "--force", tree], cwd=top)
            if sh(["git", "worktree", "add", "-q", "--detach", tree, "origin/" + base], cwd=top).returncode:
                fail(state, "could not check out origin/%s" % base)
            version_file = cfg.get("version_file") or "VERSION"
            if os.path.isabs(version_file) or ".." in version_file.split("/"):
                fail(state, "version_file must be a path inside the repo")
            vpath = os.path.join(tree, version_file)
            cur = open(vpath).read().strip() if os.path.exists(vpath) else None
            version = "0.1.0" if cur is None else release.bump(cur, "minor" if part == "major" and cur.startswith("0.") else part)
            tag = "v" + version
            if sh(["git", "ls-remote", "--exit-code", "--tags", "origin", tag], cwd=top).returncode == 0:
                fail(state, "tag %s already exists" % tag)
            cpath = os.path.join(tree, "CHANGELOG.md")
            old = open(cpath).read() if os.path.exists(cpath) else ""
            day = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
            open(vpath, "w").write(version + "\n")
            open(cpath, "w").write(release.changelog_text(old, version, day, state["release_bullets"], state["release_steps"]))
            files = [version_file, "CHANGELOG.md"]
            if sh(["git", "add", "--"] + files, cwd=tree).returncode or sh(
                    ["git", "commit", "-q", "-m", "Release %s (%s)" % (tag, slug), "--"] + files, cwd=tree).returncode:
                fail(state, "could not commit the release files")
            dest = "release/%s-%s" % (tag, slug) if to_branch else base
            texts = {"release notes": notes_text(state)}
            if to_branch:
                texts["release PR title"] = "Release %s (%s)" % (tag, slug)
            check(state, tree, "origin/" + base, texts)
            pushed = sh(["git", "push"] + ["--force"] * to_branch + ["origin", "HEAD:refs/heads/" + dest], cwd=tree)
            if pushed.returncode == 0:
                return version, sh(["git", "rev-parse", "HEAD"], cwd=tree).stdout.strip()
            if to_branch:
                fail(state, "push of %s was rejected: %s" % (dest, pushed.stderr.strip()[-200:]))
            if PROTECTED.search(pushed.stderr):
                print("NOTE: origin/%s refused the push for protection; the release goes through a pull request" % base)
                return None, pushed.stderr
            # another goal moved the base first: redo the bump on top of it
        fail(state, "push to %s was rejected %d times: %s" % (base, PUSH_TRIES, pushed.stderr.strip()[-200:]))
    finally:
        drop(top, tree, temp)


def restatus(top, cfg, state, head):
    """Post the pr lane's result for a head that moved only by wiki pages."""
    module, stop = sibling("private")
    if not stop:
        module.pr_result(top, cfg.get("base", "main"), head, state["branch"], True)


def carried(top, cfg, state, sha):
    """True when the goal's pr lane passed (statuses ok) and the release head only moves the version file and the
    CHANGELOG over its parent: the tested tree plus the bump, so the pass carries over (#3870)."""
    if state.get("statuses") != "ok":
        return False
    done = sh(["git", "diff", "--name-only", sha + "^", sha], cwd=top)
    names = set(done.stdout.split())
    return done.returncode == 0 and bool(names) and names <= {cfg.get("version_file") or "VERSION", "CHANGELOG.md"}


def lane_at(top, cfg, sha):
    """(exit code or None, output) of the affected rows at sha in a detached copy."""
    temp = tempfile.mkdtemp(prefix="release-status-")
    tree, code, text = os.path.join(temp, "tree"), None, "could not check out the release head"
    try:
        if sh(["git", "worktree", "add", "-q", "--detach", tree, sha], cwd=top).returncode == 0:
            try:
                script = os.path.join(SIBLING, "..", "..", "workflow-regression", "scripts", "regression.py")
                done = subprocess.run([sys.executable, script, "run", cfg.get("ci_levels") or "nightly", "--reuse", "--tier", "goal",
                                       "--timeout", "900"], cwd=tree, capture_output=True, text=True, errors="replace", timeout=1200)
                code, text = done.returncode, done.stdout + done.stderr
            except (OSError, subprocess.TimeoutExpired) as error:
                text = "the lane could not finish: %s" % error
    finally:
        drop(top, tree, temp)
    return code, text


def release_statuses(top, cfg, state, branch, sha):
    """Post the lane's result for the release PR's head under every required check's name, never a failure the head did
    not earn: a bump-only head carries the goal's pass; otherwise the affected rows run and only rows that ran and failed
    post failure. A lane that could not run posts nothing (release_status untested). Success is final;
    release_status_why names the cause."""
    module, stop = sibling("private")
    if stop or not sha or state.get("release_status") == "success":
        return
    state.pop("release_status_why", None)
    if sh(["git", "cat-file", "-e", sha + "^{commit}"], cwd=top).returncode:
        sh(["git", "fetch", "-q", "origin", branch], cwd=top)
    if carried(top, cfg, state, sha):
        print("CARRIED the goal's passing lane to the release head %s (it only moves the version and changelog)" % sha[:12])
        ok = True
    else:
        code, text = lane_at(top, cfg, sha)
        rows = re.findall(r"^FAIL (\S+)", text, re.M)
        ok = code == 0
        if not ok and not rows:  # nothing ran and failed: don't blame an untested head
            state["release_status"], state["release_status_why"] = "untested", "the lane at the release head %s produced no result: %s" % (
                sha[:12], " ".join((text or "(no output)").split())[-160:])
            return print("RELEASE_STATUS untested: " + state["release_status_why"])
        if rows:
            state["release_status_why"] = "rows %s failed at the release head %s" % (", ".join(rows[:8]) + (" +%d more" % (len(rows) - 8) * (len(rows) > 8)), sha[:12])
    posted = module.pr_result(top, cfg.get("base", "main"), sha, branch, ok)
    state["release_status"] = "success" if ok and posted else "failure"


RED = ("FAILURE", "ERROR", "TIMED_OUT", "CANCELLED", "STARTUP_FAILURE", "ACTION_REQUIRED")


def status_held(state, url, number, seen=None):
    """Refuse, naming the cause, when the release PR's head has no passing status (RELEASE_STATUS_FAILED, _UNTESTED) or a
    required check is red (RELEASE_CHECKS_FAILED): a merge past a red check is never advised (issue 3870)."""
    red = [str(c.get("name") or c.get("context")) for c in (seen or {}).get("statusCheckRollup") or []
           if isinstance(c, dict) and (c.get("conclusion") in RED or c.get("state") in RED)]
    why = state.get("release_status") in ("failure", "untested") and state.get("release_status_why")
    if red and not why:
        fail(state, "the release PR %s (#%s) can't merge: required checks failed: %s. Nothing needs the owner's merge, and none "
             "may be merged past a red check; fix the cause and run merge.py %s again (RELEASE_CHECKS_FAILED)"
             % (url, number, ", ".join(sorted(set(red))[:8]), state["slug"]))
    if not why:
        return
    fail(state, "the release PR %s (#%s) can't merge: %s. Nothing needs the owner's merge; fix the cause and run merge.py %s again "
         "(%s)" % (url, number, why, state["slug"], "RELEASE_STATUS_" + state["release_status"].upper().replace("FAILURE", "FAILED")))


def create_release(top, cfg, state, version, target):
    tag, text = "v" + version, notes_text(state)
    check(state, top, None, {"release notes": text})
    seen = sh(["gh", "release", "view", tag, "--json", "targetCommitish,url"], cwd=top)
    if seen.returncode == 0:  # a crash after create is adopted, one elsewhere is not ours
        try:
            info = json.loads(seen.stdout)
        except ValueError:
            info = {}
        if info.get("targetCommitish") == target:
            print("ADOPTED the existing release %s at %s" % (tag, target[:12]))
            return info.get("url") or ""
        fail(state, "a GitHub release %s already exists at %s, not at this goal's release commit %s; nothing new was "
             "created. Fix: look at it (gh release view %s) and keep or delete it, then run merge.py %s (RELEASE_EXISTS)"
             % (tag, info.get("targetCommitish") or "another target", target[:12], tag, state["slug"]))
    made = sh_text(["gh", "release", "create", tag, "--title", tag, "--target", target], text, "--notes-file", top)
    if made.returncode:
        fail(state, "gh release create %s failed after the version was pushed; run merge.py again: %s" % (
            tag, (made.stderr or made.stdout).strip()[-200:]))
    return (made.stdout.strip().splitlines() or [""])[-1]


def finish(top, cfg, state):
    """After the merge. Each step records itself, so a retry repeats only what did not finish."""
    if state.get("release") == "cut" and state.get("release_url"):
        print("ALREADY released %s as v%s" % (state["slug"], state.get("release_version")))
        return
    base = cfg.get("base", "main")
    if not state.get("release_pushed"):
        stage_notes(top, state, cfg)
        stage_part(top, state)
        part, reason = state["release_part"], state["release_reason"]
        version = sha = None
        if not state.get("release_pr") and not protected(top, base):
            version, sha = push_release_commit(top, cfg, state, part)
        if version is None:  # a protected base: the release pull request lands VERSION and CHANGELOG
            import merge as release_pr
            got = release_pr.advance(top, cfg, state)
            if not got:
                return False
            version, sha = got
        state.update(release_pushed=version, release_part=part, release_target=sha)
        release.save(state, "version pushed: v%s (%s)" % (version, reason))
    version = state["release_pushed"]
    url = create_release(top, cfg, state, version, state.get("release_target") or base)
    state.update(release="cut", release_version=version, release_url=url, status="done", waiting=None)
    for key in ("release_error", "release_pr_waiting"):
        state.pop(key, None)
    release.save(state, "release v%s published %s" % (version, url))
    print("RELEASED v%s %s (%s bump)" % (version, url, state["release_part"]))
    return True
