#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-release/scripts/autorelease.py .github/workflows/release.yml .github/workflows/regression.yml
"""REL-15: with merge_queue on, the release is made in CI on push to main, so finish() pushes no commit and opens no pull request.

A toy origin and a fake gh that logs every call. finish() with merge_queue must leave the base commit where it was, call
gh for no pull request or release, and label_part must put release:minor or release:major (not patch) on the merged
pull request. release.yml must trigger on push to main, run no lane, and regression.yml must not run on a tag.
AUTORELEASE=PATH tests another copy of autorelease.py (a red run uses the one before this goal)."""
import contextlib
import io
import os
import subprocess
import sys
import tempfile

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.normpath(os.path.join(here, "..", ".."))
scripts = os.path.join(root, "skills", "workflow-release", "scripts")
sys.path.insert(0, scripts)
sys.path.insert(1, os.path.join(root, "skills", "workflow-delivery", "scripts"))
if os.environ.get("AUTORELEASE"):  # a copy of autorelease.py: the other scripts still come from this tree
    import importlib.util
    spec = importlib.util.spec_from_file_location("autorelease", os.environ["AUTORELEASE"])
    ar = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ar)
else:
    import autorelease as ar  # noqa: E402

failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


def main():
    temp = tempfile.mkdtemp(prefix="rel15-")
    origin, clone, bindir, log = (os.path.join(temp, n) for n in ("origin.git", "clone", "bin", "gh.log"))
    os.makedirs(bindir)
    git("init", "-q", "--bare", "-b", "main", origin, cwd=temp)
    git("clone", "-q", origin, clone, cwd=temp)
    git("config", "user.email", "t@example.com", cwd=clone)
    git("config", "user.name", "t", cwd=clone)
    open(os.path.join(clone, "VERSION"), "w").write("1.0.0\n")
    git("add", "VERSION", cwd=clone)
    git("commit", "-q", "-m", "first", cwd=clone)
    git("push", "-q", "origin", "main", cwd=clone)
    with open(os.path.join(bindir, "gh"), "w") as fake:
        fake.write('#!/bin/sh\necho "$@" >> "%s"\nexit 0\n' % log)
    os.chmod(os.path.join(bindir, "gh"), 0o755)
    os.environ["PATH"] = bindir + os.pathsep + os.environ["PATH"]
    base_before = git("rev-parse", "origin/main", cwd=clone)

    def gh_calls():
        return open(log).read() if os.path.exists(log) else ""

    state = {"slug": "toy", "pr": "https://example.com/pull/7", "release_part": "minor", "release_reason": "a goal"}
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        ar.label_part(clone, {"merge_queue": True}, state)
        got = ar.finish(clone, {"merge_queue": True, "base": "main"}, state)
    calls = gh_calls()
    git("fetch", "-q", "origin", cwd=clone)
    check(got is True and "RELEASE from CI" in out.getvalue(), "finish() with merge_queue on says the release comes from CI")
    check(git("rev-parse", "origin/main", cwd=clone) == base_before and not git("branch", "-r", cwd=clone).count("release/"),
          "finish() pushes no commit to the base and no release branch")
    check("pr create" not in calls and "release create" not in calls, "finish() opens no pull request and creates no release")
    check("label create release:minor" in calls and "pr edit https://example.com/pull/7 --add-label release:minor" in calls,
          "a minor part is labelled release:minor on the merged pull request")
    open(log, "w").close()
    state["release_part"] = "patch"
    with contextlib.redirect_stdout(io.StringIO()):
        ar.label_part(clone, {"merge_queue": True}, state)
        state["release_part"] = "major"
        ar.label_part(clone, {}, state)  # the setting off labels nothing
    check(gh_calls() == "", "a patch part and a repo without merge_queue add no label")

    release = open(os.path.join(root, ".github", "workflows", "release.yml")).read()
    check("branches: [main]" in release and "regression.py" not in release and "pull_request" not in release.split("jobs:")[0],
          "release.yml runs on push to main and runs no lane")
    check("gh release create" in release and "--generate-notes" in release and "git push" not in release,
          "release.yml makes the release with gh release create --generate-notes and pushes nothing")
    flow = open(os.path.join(root, ".github", "workflows", "regression.yml")).read()
    check("tags:" not in flow, "regression.yml does not run on a release tag")

    # a negative control: a push to the base is seen by the same detector
    open(os.path.join(clone, "VERSION"), "w").write("1.0.1\n")
    git("commit", "-q", "-am", "Release v1.0.1", cwd=clone)
    git("push", "-q", "origin", "main", cwd=clone)
    git("fetch", "-q", "origin", cwd=clone)
    check(git("rev-parse", "origin/main", cwd=clone) != base_before, "the control: a release commit on the base is detected")
    if failed:
        sys.exit(1)
    print("PASS: REL-15: with merge_queue on, the release is made in CI and finish() pushes nothing and opens no pull request")


main()
