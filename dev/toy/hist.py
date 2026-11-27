#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-delivery/scripts/dlf.py skills/workflow-delivery/scripts/private.py
"""History reads for the rows that compare a past goal's own merge on origin/main. A read that can't run is a failure with a code,
never an empty answer. The codes:
HIST-E01 the base ref is missing.
HIST-E02 the history is shallow.
HIST-E03 a git command failed.
HIST-E04 a fixture could not be built.
Each error is one line: what could not be done, "Fix:", "In plain words:" and "Side effects: none." Anything read from git is cut
and screened before it is printed: addresses and local paths become their kind, and text the loop's private-name and secret
screen refuses is withheld. usage: hist.py added REPO GREP | fixture REPO GIT-ARGS..."""
import os
import re
import subprocess
import sys

here = os.path.dirname(os.path.abspath(__file__))
top = os.path.abspath(os.path.join(here, "..", ".."))

REF = "origin/main"


def caller_names(environ):
    """The private-name list of whoever runs the test: LOOP_PRIVATE_NAMES, or their default list when that is unset or empty (the
    row runner's stand-in). A test that moves HOME reads this first and sets NAMES."""
    given = environ.get("LOOP_PRIVATE_NAMES")
    if given and given != os.devnull:
        return given
    default = os.path.join(environ.get("HOME", ""), ".workflow-loop", "private-names")
    return default if os.path.isfile(default) else given or os.devnull


NAMES = caller_names(os.environ)
FETCH = "git fetch origin main:refs/remotes/origin/main"
IDENTITY = ("-c", "user.email=t@example.test", "-c", "user.name=t")
TEXT = {
    "HIST-E01": ("the base ref %s is missing in this repository, so %%s can't be read." % REF,
                 "%s (the scheduled job's full-history checkout supplies it)." % FETCH,
                 "this copy of the project doesn't have its main branch; run that command once, then run the check again."),
    "HIST-E02": ("the history here is shallow, so %s can't be read.",
                 "git fetch --unshallow, then run this once more; a run from a fork or a branch other than main also needs " + FETCH + ".",
                 "this copy only has the latest changes; that command downloads the older ones."),
    "HIST-E03": ("a git command failed while reading %s",
                 "if the cause is missing history, use the fix of HIST-E01 (%s) or HIST-E02 (git fetch --unshallow); otherwise report "
                 "this line to whoever looks after the project." % FETCH,
                 "a step that reads the project's history failed; send this whole line on if the commands above don't help."),
    "HIST-E04": ("a fixture could not be built for %s",
                 "check that git works and the temporary folder is writable, then run this again; if it repeats, report this line.",
                 "the check couldn't make its own practice copy; nothing about the project's history was read."),
}


def screen(text):
    """Text from a child command, fit to print: one line, screened, cut."""
    return redact(" ".join(str(text).split()))[:200]


def redact(text):
    """Addresses and paths as their kind; the whole text withheld if the loop's private-name and secret screen refuses it."""
    text = re.sub(r"[A-Za-z][A-Za-z0-9+.-]*://\S+|\b[\w.-]+@[\w.-]+:\S+", "[address]", text)
    text = re.sub(r"(?<![\w.])(?:~|[A-Za-z]:)?[\\/](?:[^\s'\":\\/]+[\\/])*[^\s'\":]*", "[local path]", text)
    folder = os.path.join(top, "skills", "workflow-delivery", "scripts")
    if folder not in sys.path:
        sys.path.append(folder)  # at the end, so a test's own imports are never shadowed
    import dlf
    held = os.environ.get("LOOP_PRIVATE_NAMES")
    os.environ["LOOP_PRIVATE_NAMES"] = NAMES
    try:
        return dlf.safe(top, text)
    finally:
        os.environ.pop("LOOP_PRIVATE_NAMES") if held is None else os.environ.update(LOOP_PRIVATE_NAMES=held)


def shown(items):
    """A list read from git, each item fit to print. Compare the raw list; print this one."""
    return [screen(item) for item in items]


def line(code, what, detail=""):
    said, fix, plain = TEXT[code]
    said = said % what + (" (%s)." % detail if detail else "." if not said.endswith(".") else "")
    return "FAIL: %s: %s Fix: %s In plain words: %s Side effects: none." % (code, said, fix, plain)


def stop(code, what, detail=""):
    """Print the code's line and end the test as failed: nothing after a history it can't read is worth reporting."""
    print(line(code, what, detail), flush=True)
    sys.exit(1)


def git(repo, *args):
    return subprocess.run(["git", *IDENTITY, *args], cwd=repo, capture_output=True, text=True, errors="replace")


def run(repo, what, *args, code="HIST-E03"):
    """git's output; a command that fails ends the test with the code."""
    try:
        done = git(repo, *args)
    except OSError as error:
        stop(code, what, "git could not start: %s" % screen(type(error).__name__))
    if done.returncode:
        cause = screen(next((l for l in done.stderr.splitlines() if l.strip()), "no message"))
        stop(code, what, "git %s exited %d: %s" % (args[0], done.returncode, cause))
    return done.stdout


def fixture(repo, *args):
    """A git command that builds a test's own practice repository."""
    return run(repo, "this test", *args, code="HIST-E04")


def require(repo, what):
    """Before any history is read: the history is whole and the base ref is there."""
    if run(repo, what, "rev-parse", "--is-shallow-repository").strip() == "true":
        stop("HIST-E02", what)
    if git(repo, "rev-parse", "--verify", "-q", REF).returncode:
        stop("HIST-E01", what)


def added(repo, grep, *paths, what="a past goal's merge"):
    """(merge, files it added under paths): the newest first-parent merge on origin/main whose message matches grep, against its first
    parent; ("", []) when no merge matches."""
    merge = run(repo, what, "log", REF, "--first-parent", "--merges", "--format=%H", "-1", "--grep", grep).strip()
    if not merge:
        return "", []
    out = run(repo, what, "diff", "--diff-filter=A", "--name-only", merge + "^1", merge, "--", *paths)
    return merge, [l for l in out.splitlines() if l.strip()]


def main(argv):
    if argv[:1] == ["added"] and len(argv) == 3:
        merge, files = added(argv[1], argv[2], "skills")
        print("\n".join(files) if merge else "NOMERGE")
        return 0
    if argv[:1] == ["require"] and len(argv) == 2:
        require(argv[1], "the merge this row reads")
        return 0
    if argv[:1] == ["fixture"] and len(argv) > 2:
        fixture(argv[1], *argv[2:])
        return 0
    sys.exit("usage: hist.py added REPO GREP | require REPO | fixture REPO GIT-ARGS...")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
