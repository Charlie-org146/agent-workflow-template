#!/usr/bin/env python3
# reads: dev/toy/hist.py
"""Helpers for the Codex part of test-codex.sh. usage:
  codexrun.py limited SECONDS -- CMD...   run CMD with closed input; past SECONDS its whole process group is killed and the exit is 124
  codexrun.py line CODE NAME [DETAIL...]  print one error line: what happened, "Fix:", "In plain words:", "Side effects:"
  codexrun.py screen TEXT...              print TEXT fit to show: addresses and local paths as their kind, secrets and private names withheld
  codexrun.py keep SOURCE DEST REPO       copy a log to DEST, screened line by line; a DEST inside REPO is refused"""
import os
import signal
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hist  # noqa: E402

RERUN = "read the kept log (set KEEP to a file outside the repository), fix the cause it names, then run this once more; nothing retries by itself."
TEXT = {
    "CODEX-E01": ("codex is not installed on this machine", "install the Codex CLI, or name one in CODEX_BIN.",
                  "the program this check drives isn't on this computer.", "none"),
    "CODEX-E02": ("codex is not signed in on this machine", "run codex login, then run this again.",
                  "someone has to sign in to Codex on this computer first.", "none"),
    "CODEX-E03": ("the live part passed its deadline and the Codex process was stopped", RERUN,
                  "Codex took too long, so it was stopped.", "PARTIAL: the practice run's own temporary files may be half written"),
    "CODEX-E04": ("a command exited with an error", RERUN, "Codex itself reported a failure.",
                  "PARTIAL: the practice run's own temporary files may be half written"),
    "CODEX-E05": ("a command didn't finish the way it should", RERUN,
                  "one of the commands Codex ran ended differently from what a good run gives.",
                  "PARTIAL: the practice run's own temporary files may be half written"),
}


def line(code, name, detail=""):
    said, fix, plain, effects = TEXT[code]
    extra = " (%s)" % hist.screen(detail) if detail else ""
    return "%s: %s: %s%s. Fix: %s In plain words: %s Side effects: %s." % (code, name, said, extra, fix, plain, effects)


def limited(seconds, command):
    child = subprocess.Popen(command, stdin=subprocess.DEVNULL, start_new_session=os.name != "nt")
    try:
        return child.wait(timeout=max(1, seconds))
    except subprocess.TimeoutExpired:
        if os.name == "nt":
            child.kill()
        else:
            os.killpg(child.pid, signal.SIGKILL)
        child.wait()
        return 124


def inside(path, folder):
    path, folder = os.path.realpath(path), os.path.realpath(folder)
    return path == folder or path.startswith(folder + os.sep)


def keep(source, dest, repo):
    if inside(dest, repo):
        print("REFUSED: KEEP names a file inside the repository; Codex's logs stay outside it. Fix: set KEEP to a path outside the "
              "repository. In plain words: a log kept in the project folder could be committed by mistake. Side effects: none.")
        return 2
    if source != "-":
        try:
            with open(source, encoding="utf-8", errors="replace") as handle:
                lines = handle.read().splitlines()
            handle = os.fdopen(os.open(dest, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), "w", encoding="utf-8")
            with handle:
                handle.write("".join(hist.redact(text) + "\n" for text in lines))
        except OSError as error:
            print("REFUSED: the kept log could not be written (%s). Fix: set KEEP to a file you can write, outside the repository. "
                  "In plain words: the copy of Codex's log you asked for was not saved. Side effects: PARTIAL: the file may be half "
                  "written." % hist.screen(error.strerror or type(error).__name__))
            return 2
    return 0


def main(argv):
    if argv[:1] == ["limited"] and len(argv) > 3 and argv[2] == "--":
        return limited(int(argv[1]), argv[3:])
    if argv[:1] == ["line"] and len(argv) > 2 and argv[1] in TEXT:
        print(line(argv[1], argv[2], " ".join(argv[3:])))
        return 0
    if argv[:1] == ["screen"]:
        print(hist.screen(" ".join(argv[1:])))
        return 0
    if argv[:1] == ["keep"] and len(argv) == 4:
        return keep(*argv[1:])
    sys.exit("usage: codexrun.py limited SECONDS -- CMD... | line CODE NAME [DETAIL] | screen TEXT | keep SOURCE DEST REPO")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
