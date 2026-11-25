#!/usr/bin/env python3
"""Release helpers moved whole from release.py to keep it under its size line: the verify steps, the documentation lines and the
deliver-first debt gate. release.py and autorelease.py import this; it imports release for the helpers it shares."""
import os
import re
import sys

from release import doc_rows, git, wiki_link  # noqa: E402,F401

DELIVERY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "workflow-delivery", "scripts")


def verify_steps(top, slug):
    try:
        text = open(os.path.join(top, ".loop", "goals", slug + ".md")).read()
    except OSError:
        return ""
    part = text.partition("## Verify by hand")[2].split("\n## ", 1)[0]
    part = re.sub(r"<!--.*?-->", "", part, flags=re.S).strip()
    steps = re.split(r"^\s*\d+\.\s+(?=\S)", part, flags=re.M)[1:]
    return part if steps and all(re.search(r"Expect:\s*\S", step) for step in steps) else ""


def docs_lines(top, cfg, base):
    if not doc_rows(top):
        return ["Documentation: not set up (run workflow-docs init)."]
    out = git("diff", "--name-only", base + "...HEAD", "--", cfg.get("wiki_dir") or "docs/wiki", cwd=top, check=False)
    changed = [os.path.basename(name)[:-3] for name in out.splitlines() if name.endswith(".md")]
    link = wiki_link(top)
    return ["Documentation changed: %s." % (", ".join(changed) or "none")] + (["Wiki: " + link] if link else [])


def debt(cwd, slug, runs):
    """DLF-1.4: '' when no deliver-first line stands between this release and its cut; else why not. Fails closed: no ledger reader, no cut."""
    paths = [os.path.join(DELIVERY, name + ".py") for name in ("dlf", "dlf_cut")]
    if not all(os.path.isfile(path) for path in paths):
        return "the deliver-first ledger can't be read: workflow-delivery is not beside workflow-release. Fix: install workflow-delivery"
    import importlib.util
    sys.path.insert(0, DELIVERY)
    mods = []
    for name, path in zip(("dlf", "dlf_cut"), paths):
        spec = importlib.util.spec_from_file_location(name, path)
        mods.append(importlib.util.module_from_spec(spec))
        spec.loader.exec_module(mods[-1])
    return mods[1].cut(cwd, runs, mods[0].brief(cwd, slug)[1])
