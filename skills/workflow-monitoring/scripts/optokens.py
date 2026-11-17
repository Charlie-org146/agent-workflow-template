#!/usr/bin/env python3
"""The operation session's own turns: what each cost, and which need no model at all (MON-5, token-diet C3 and C4).

usage: optokens.py             the UserPromptSubmit hook (C3): reads the hook's JSON on stdin; prints a block or nothing
       optokens.py append      add one row to <git common dir>/loop/op-tokens.tsv (checkin.py does it every pass)
       optokens.py show        print that file   [--root DIR for append and show]

Triggers, read from the user message that started each turn of the operation session's transcript (classify):
  scheduled   the check-in prompt the schedule sends
  peer        a message from another session, a worker's finished turn or a task notification
  human       anything the owner typed
  hook-retry  `Stop hook feedback`, the reply hook sending a reply back

op-tokens.tsv, one row a check-in: time, session, context (the last call's), the tokens spent since the previous row under
each trigger (input, cache reads, cache writes and output: the unit of the v1 baseline), and the total. Never fails a check-in.

reply_hook.py asks needs_layout (C4): only a scheduled check-in, or the owner asking for one (check-in, status, report, board,
where do things stand), must be answered in the MON-5 layout; a peer message or other talk may be answered in 1-3 lines.

The hook (C3), for the operation session only and only for a scheduled prompt, renders the check-in (checkin.render), drops the
Machine line and every number, and compares it with what the last full check-in showed (checkin.py keeps it with remember()).
The same, and that check-in under QUIET_MINUTES (120) old, blocks the prompt with one line: no model turn runs and nothing enters
the session's context. Anything else, an error included, lets the prompt through. `reply_hook: false` in .loop/config.json or
LOOP_REPLY_HOOK=0 turns it off with the reply hook. Skips are logged in <common>/loop/quiet.log. setup.py --reply-hook installs it.
"""
import argparse
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import time

TRIGGERS = ("scheduled", "peer", "human", "hook-retry")
HEADER = "# time\tsession\tcontext\t" + "\t".join(TRIGGERS) + "\ttotal"
PEER = ("finished a turn", "Another Claude session", "<task-notification", "<cross-session-message", "side-sessions-event",
        "<ci-monitor-event", "<session-message")
ASKED = re.compile(r"check[- ]?in|where do things stand|\bstatus\b|\breport\b|dashboard|\bboard\b", re.I)
QUIET_MINUTES = 120


def classify(text):
    text = str(text or "").lstrip()
    if text.startswith("Stop hook feedback"):
        return "hook-retry"
    if text.startswith("Operation") and "check-in" in text[:120].lower():
        return "scheduled"
    return "peer" if any(mark in text[:400] for mark in PEER) else "human"


def asked(text):
    return classify(text) == "human" and bool(ASKED.search(str(text or "")[:300]))


def text_of(entry):
    """A user entry's own words; None for one that only carries tool results."""
    content = (entry.get("message") or {}).get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [b for b in content if isinstance(b, dict)]
        if parts and all(b.get("type") == "tool_result" for b in parts):
            return None
        return " ".join(str(b.get("text") or "") for b in parts if b.get("type") == "text")
    return None


def needs_layout(entries):
    """True when the last turn that was not a hook retry is a scheduled check-in or an owner's ask for one, or can't be read."""
    for entry in reversed(entries or []):
        if entry.get("type") != "user":
            continue
        text = text_of(entry)
        if text is None or classify(text) == "hook-retry":
            continue
        return classify(text) == "scheduled" or asked(text)
    return True


def tokens_module():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "workflow-delivery", "scripts", "tokens.py")
    spec = importlib.util.spec_from_file_location("loop_tokens", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def hook_module():
    import reply_hook
    return reply_hook


def common(root):
    done = subprocess.run(["git", "-C", root, "rev-parse", "--git-common-dir"], capture_output=True, text=True, timeout=10)
    return os.path.realpath(os.path.join(root, done.stdout.strip())) if done.returncode == 0 and done.stdout.strip() else ""


def turn_label(entry):
    text = text_of(entry)
    return classify(text) if text is not None else None


def row(root, now=None):
    """The line to append: the operation session's tokens since its last row, by trigger; None with no transcript."""
    tok, folder = tokens_module(), common(root)
    ids = sorted((s for s in hook_module().claimed(folder) if tok.transcript(s)), key=lambda s: os.path.getmtime(tok.transcript(s)))
    if not ids:
        return None
    session, table = ids[-1], os.path.join(folder, "loop", "op-tokens.tsv")
    try:
        with open(table, encoding="utf-8") as handle:
            rows = [line.split("\t") for line in handle.read().splitlines() if line and line[0] != "#"]
    except OSError:
        rows = []
    last = max((r[0] for r in rows if len(r) > 1 and r[1] == session), default="")
    found = tok.calls(tok.transcript(session), last, "", turn_label)
    got = {name: sum(tok.total(c) for c in found if c["turn"] == name) for name in TRIGGERS}
    return "\t".join([now or tok.stamp(), session, str(found[-1]["context"] if found else 0)] + [str(got[n]) for n in TRIGGERS] + [str(sum(got.values()))])


def append(root, now=None):
    line = row(root, now)
    if not line:
        return ""
    table = os.path.join(common(root), "loop", "op-tokens.tsv")
    fresh = not os.path.exists(table)
    with open(table, "a", encoding="utf-8", newline="\n") as handle:
        handle.write((HEADER + "\n" if fresh else "") + line + "\n")
    return line


def signature(text):
    """The check-in without its clock: no Machine line, no digits, so only a word that changed counts."""
    kept = [line for line in str(text).splitlines() if not line.startswith("Machine:")]
    return hashlib.sha1(re.sub(r"\d+", "#", "\n".join(kept)).encode("utf-8", "replace")).hexdigest()


def quiet_path(folder):
    return os.path.join(folder, "loop", "quiet.json")


def remember(folder, text, now=None):
    hook_module().write(quiet_path(folder), json.dumps({"sig": signature(text), "at": now or time.time()}))


def held(folder):
    try:
        with open(quiet_path(folder), encoding="utf-8") as handle:
            found = json.load(handle)
        return str(found.get("sig", "")), float(found.get("at", 0))
    except (OSError, ValueError, AttributeError, TypeError):
        return "", 0.0


def decide(payload, text=None, now=None):
    """The block decision for a prompt, or None."""
    rh = hook_module()
    session = str(payload.get("session_id") or "")
    if os.environ.get("LOOP_REPLY_HOOK") == "0" or not rh.SESSION.match(session):
        return None
    where = rh.repo_of(str(payload.get("cwd") or ""))
    if not where or rh.off(where[2]) or session not in rh.claimed(where[1]) or classify(payload.get("prompt")) != "scheduled":
        return None
    top, folder, _ = where
    if text is None:
        import checkin
        text = "\n".join(checkin.render(top))
    sig, at = held(folder)
    now = now or time.time()
    if not sig or sig != signature(text) or now - at >= QUIET_MINUTES * 60:
        return None
    os.makedirs(os.path.join(folder, "loop"), exist_ok=True)
    with open(os.path.join(folder, "loop", "quiet.log"), "a", encoding="utf-8") as handle:
        handle.write("%s skipped %s\n" % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)), session))
    return {"decision": "block", "reason": "No change since the last check-in at %s (checkin.py): model turn skipped. The next full "
            "check-in comes when something changes, or at the latest %d minutes after the last one." % (
                time.strftime("%H:%M", time.localtime(at)), QUIET_MINUTES)}


def hook():
    payload = {}
    try:
        payload = json.load(sys.stdin)
        out = decide(payload) if isinstance(payload, dict) else None
    except Exception as error:  # never stand between the owner and the session
        try:
            where = hook_module().repo_of(str((payload or {}).get("cwd") or ""))
            where and hook_module().log(where[1], "quiet fail-open: %s: %s" % (type(error).__name__, error))
        except Exception:
            pass
        out = None
    out and print(json.dumps(out))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", nargs="?", default="hook", choices=("hook", "append", "show"))
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    if args.command == "hook":
        return hook()
    if args.command == "show":
        try:
            with open(os.path.join(common(args.root), "loop", "op-tokens.tsv"), encoding="utf-8") as handle:
                sys.stdout.write(handle.read())
        except OSError:
            print("no op-tokens.tsv yet")
        return 0
    print(append(args.root) or "no operation transcript found")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    sys.exit(main())
