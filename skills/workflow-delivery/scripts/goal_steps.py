"""the record and pr commands"""
import json
import os
import re
import sys

import cover


def cmd_record(args):
    slug, step = args.slug, args.step
    state = _s.held(slug)
    _s.guards.waiting_gate(_s.ME, state)
    _s.add_tokens(state, step, args.tokens, True)
    ran = os.path.join(_s.state_dir(), "%s.%s.ran" % (slug, step))
    if args.in_session:
        args.file = _s.role.session_reply(state, slug, step, args.file, _s.state_dir(), _s.FLOW)
    lane = cover.need(_s.role.need_lane, _s.role.over_caps, _s.state_dir(), slug, args.file, step) if step in ("qa", "ship") else None
    if lane:
        _s.guards.refuse_no_try(state, *lane, _s.save)
    reply = os.path.realpath(args.file)
    if reply != os.path.realpath(os.path.join(_s.state_dir(), "%s.%s.txt" % (slug, step))) or not os.path.exists(ran):
        _s.guards.refuse_no_try(state, "%s wasn't run by flow.py" % step, "run flow.py %s %s until it prints NEXT" % (
            slug, step), _s.guards.NOT_RUN_BY_FLOW, _s.save)
    text = _s.read(reply)
    found = re.findall(r"^\W*STEP:\s*(done|skipped|pending|failed)\b[ :.-]*(.*)$", text, re.M | re.I)
    result, why = (found[-1][0].lower(), found[-1][1].strip()) if found else ("", "")
    why = why if why or step not in ("qa", "ship") else _s.role.lane_note(_s.state_dir(), slug, step)
    pending = _s.guards.pending_items(text)
    session = args.in_session or state.get("worker") == "session"
    if not result and not pending and session:
        _s.guards.refuse_no_try(state, "the %s reply has no STEP line" % step, "end the reply with the DEPTH line and a "
                             "STEP: done|skipped|pending|failed line, then record again", _s.guards.NO_STEP_LINE, _s.save)
    stamp, cfg = "", _s.config()
    wait = pending or result == "pending"
    auto, ok = wait and (_s.dlf.autoapprove(_s.ME, state, pending, step, cfg, result, why)), result in ("done", "skipped")
    if ok or auto:
        stamp, refusal, ask, skipped = _s.guards.check_record(state, step, text, cfg, result)
        for line in skipped:
            state.setdefault("log", []).append("%s rule %s" % (_s.now(), line))
        if ask:
            _s.guards.hold(state, ask[:600])
            _s.save(state, "%s waits for the owner (no try used): %s" % (step, ask[:200]))
            print("WAITING %s (no try used): %s" % (slug, ask))
            return 0
        if refusal:
            _s.guards.refuse_no_try(state, refusal[0], refusal[1], refusal[2], _s.save)
    os.remove(ran)
    if ok or wait:
        _s.guards.clear_refusals(state)
    if ok or auto:
        _s.fit.keep(_s.ME, state, step, text)
    if auto:
        took = _s.dlf.safe(_s.root(), "; ".join(pending) or why or "the step's pending gate")
        state["flow"][step] = "done: auto-approved: " + took[:200] + stamp
        state["step"] = _s.role.after(step)
        state["note"] = {"text": "auto-approved at %s: %s" % (step, took[:240]), "at": _s.now()}
        _s.guards.advance(_s.ME, state)
        _s.save(state, "%s auto-approved: %s" % (step, took[:300]))
        print("AUTO-APPROVED %s %s: %s" % (slug, step, took))
        print(_s.nxt(args, state))
        return 0
    if wait:
        state["flow"][step] = "pending"
        ask = _s.dlf.held_ask(_s.root(), step, pending, why)
        _s.guards.hold(state, ask[:600])
        _s.save(state, "%s pending: %s" % (step, ask[:200]))
        print("WAITING %s: %s" % (slug, ask))
        return 0
    if ok:
        state["flow"][step] = result + (" in session" if args.in_session else "") + (": " + why[:120] if why else "") + stamp
        state["step"] = _s.role.after(step)
        _s.guards.advance(_s.ME, state)
        _s.save(state, "%s %s" % (step, state["flow"][step]))
        print("RECORDED %s %s" % (step, state["flow"][step]))
        tool = os.path.join(_s.SKILLS, "workflow-health", "scripts", "milestone.py")
        if step == "ship" and re.search(r"^\W*FILE\s", text, re.M | re.I) and os.path.exists(tool):
            print(_s.run([sys.executable, tool, "leftovers", reply, "--goal", slug, "--live"]).stdout.strip())
        print(_s.nxt(args, state))
        return 0
    _s.failed_try(state, "%s %s" % (step, "failed: " + why[:200] if result else "gave no STEP line"), step,
               "fix the cause, then run flow.py %s %s again" % (slug, step))
    return 1


def cmd_pr(args):
    slug, cfg = args.slug, _s.config()
    state, base = _s.held(slug), cfg["base"]
    _s.fit.budget_stop(slug, state, _s.state_dir(), cfg, save=_s.save)
    _s.guards.waiting_gate(_s.ME, state)
    left = [step for step in _s.FLOW if not str(state.get("flow", {}).get(step, "")).startswith(("done", "skipped"))]
    if left:
        _s.no("the flow hasn't finished: %s. Fix: run flow.py %s %s." % (", ".join(left), slug, left[0]))
    waited = "waiting: pr queue" in (state.get("log") or [""])[-1]
    _s.queue("preflight", _s.ME, state)
    _s.pods and _s.pods.pr_queue("join", _s.ME, state)
    if ahead := _s.queue("turn", slug):
        waited or _s.save(state, "waiting: pr queue, behind " + ahead)
        print("WAITING pr queue: %s first; run pr again" % ahead)
        return 0
    waited and _s.save(state, "pr queue: its turn")
    _s.queue("hold", slug)
    what, detail = _s.role.sync(base)
    if what == "merged":
        state = _s.held(slug)
    round_stop(_s.ME, state, what)
    if what == "conflict":
        why, fix = "merging %s conflicts in: %s" % (base, detail), "merge %s, resolve the conflicts, commit, then pr" % base
        return _s.queue("moved", _s.ME, state, why, fix) or _s.failed_try(state, why, "build", fix) or 1
    if what == "dirty":
        _s.no("the merge was refused: %s. Fix: commit or remove them, then run pr." % detail)
    if what == "merged":
        print("MERGED %s into the branch" % detail)
    _s.guards.sync_touches(_s.goal_file(slug), _s.guards.touches_of(_s.state_dir(), state))
    if _s.git("status", "--porcelain", "--", _s.goal_file(slug)):
        _s.git("commit", "-m", "Goal: %s touches" % slug, "--", _s.goal_file(slug))
    head = _s.git("rev-parse", "HEAD")
    owed = _s.fit.owed(_s.root(), _s.read(_s.goal_file(slug)))
    if owed:
        _s.no("no passing defect test, seen failing, for %s. Fix: regression.py add --category defect --link ..., then red." % ", ".join(owed))
    _s.role.requirement_gate(_s.ME, slug)
    if _s.git("status", "--porcelain", "--", "."):
        print("NOTE: uncommitted files stay out")
    head = _s.role.bump_version(_s.ME, state, head)
    head = _s.fit.regen(_s.ME, slug)
    gate, line, ids = cover.lane(_s.role.lane, _s.state_dir(), slug, "pr", _s.role.flow_spec(), cfg)
    print(line)
    if gate == "running":
        return 0
    if gate == "fail":
        if _s.queue("ahead", base):
            return _s.queue("moved", _s.ME, state, "lane failed while %s moved" % base, "run pr")
        return _s.fit.pr_fail(_s.ME, state, head, line, ids)
    _s.role.record(state, base)
    if cover.late(_s.state_dir(), slug, cfg):
        gate, line, ids = cover.lane(_s.role.lane, _s.state_dir(), slug, "pr", _s.role.flow_spec(), cfg)
        print(line)
        if gate == "running":
            return 0
        if gate == "fail":
            return _s.fit.pr_fail(_s.ME, state, head, line, ids)
        _s.role.record(state, base)
    state["pr_lane"] = cover.pr_part(_s.state_dir(), slug) or state["pr_lane"]
    known = _s.run(["gh", "pr", "view", state["branch"], "--json", "url,state"])
    info = json.loads(known.stdout) if not known.returncode else {}
    body = _s.fit.pr_text(_s.ME, state)
    if left := _s.fit.monitor("pool").pr_closing(_s.root(), body):
        _s.no("the PR leaves %s open. Fix: add Fixes %s to the goal file, not its done lines." % (", ".join(left), left[0]))
    state["step"] = "pr"
    _s.save(state, "pr")
    url = _s.fit.pr_open(_s.ME, state, base, info, body)
    cover.refresh(_s, state, info, body)
    state.update(pr=url, statuses="ok" if _s.private.pr_result(_s.root(), base, _s.git("rev-parse", "HEAD"), state["branch"], True) else "failed")
    state.update(step="release", status="done")
    _s.save(state, "pull request " + url)
    print("PR " + url)
    print("NEXT: " + ("workflow-release merges it: merge.py %s" % slug if cfg.get("auto_merge") is True and state.get("release") != "ask"
                      else "workflow-release asks cut or leave. The loop never merges."))
    if state["statuses"] == "failed":
        print("NEXT: no merge until the status posts: private.py statuses --head %s --ok" % head)
    return 5 * (state["statuses"] == "failed")


def round_stop(g, state, what):
    return _s.dlf.round_stop(g, state, what)


import goal as _s  # noqa: E402
