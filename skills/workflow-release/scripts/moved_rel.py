"""The one way to reach the shared steps.py (skills/ in the repo, shared/ in a pack)."""
import importlib
import os
import re
import sys


def steps():
    """The shared steps.py by name, found in skills/ (repo) or shared/ (pack); a named refusal when it is missing."""
    if "steps" not in sys.modules:
        here = os.path.dirname(os.path.abspath(__file__))
        for path in (os.path.join(here, "..", ".."), os.path.join(here, "..", "..", "..", "shared")):
            if os.path.exists(os.path.join(path, "steps.py")):
                sys.path.insert(0, os.path.normpath(path))
                break
    try:
        return importlib.import_module("steps")
    except ImportError:
        sys.exit("REFUSED: steps.py is missing. Fix: reinstall the workflow package (SC_MISSING).")


def fail(state, text):
  state["release_error"] = text if len(text) <= 400 else text[:330] + " ... " + text[-65:]
  report, note = state.get("report"), ""
  if not isinstance(report, dict):
    note = "" if report is None else "(the stored report was a %s and was reset) " % type(report).__name__
    report = state["report"] = {}
  report["text"] = ("%s %sRelease failed: %s" % (str(report.get("text") or ""), note, text)).strip()[:600]
  if state.get("release") != "merged":
    state["status"] = "failed"
  import release
  release.save(state, "release failed: " + text[:200])
  sys.exit("REFUSED: " + text)


def stage_steps(top, state):
  """The release text's steps: the verify steps, then the Steps block."""
  import release
  block = steps().summary(state)
  state["release_steps"] = (release.verify_steps(top, state["slug"]) or "No manual steps were recorded.") + "\n\n" + block
  state["release_steps_final"] = block



def changelog_text(old, version, day, bullets, steps):
    title = "## [%s] - %s" % (version, day) if re.search(r"^## \[", old, re.M) else "## v%s - %s" % (version, day)
    entry = "%s\n\n%s\n\n### How to verify\n\n%s\n" % (title, "\n".join("- " + item for item in bullets) or "- No code changes", steps)
    if not old.strip():
        return "# Changelog\n\n" + entry
    first = re.search(r"^## ", old, re.M)
    return old[:first.start()] + entry + "\n" + old[first.start():] if first else old.rstrip("\n") + "\n\n" + entry
