"""Which repo paths a text names (SKP-1.1, o963): the reach finder, moved out of lanes.py unchanged to keep lanes.py under the size cap.

lanes.py keeps `from row_reach import references, HERE_FORMS`. narrow is bound lazily: narrow imports lanes, and lanes imports this file."""
import os
import re


class _Lazy:
    def __getattr__(self, name):
        import narrow as module
        return getattr(module, name)


narrow = _Lazy()
PATH = re.compile(r"(?<![\w.@+/-])(?:\$\{?here\}?/|\./)?((?:\.?[A-Za-z0-9_@+-][A-Za-z0-9._@+-]*/)+[A-Za-z0-9._@+-]*"
                  r"|[A-Za-z0-9_-]+\.[A-Za-z0-9]+)")
BARE = re.compile(r"\$\{?here\}?/skills\b(?!/)")
ROOT = re.compile(r"\$\{?here\}?/?(?=[\s\"')]|$)")
SKILL_NAME = re.compile(r"\bworkflow-[a-z]+\b")
HERE_FORMS = re.compile(r'"\$\{?here\}?"/|\$\{here\}/')
CD_SKILLS = re.compile(r"cd\s+\"?\$\{?here\}?\"?\s*[;&|\n][^\n]*?(?<![\w./$-])skills(?:/\.)?(?=[\s\"')]|$)")


def widen(path):
    parts = path.rstrip("/").split("/")
    return "skills/%s/" % parts[1] if parts[0] == "skills" and len(parts) > 1 else path


def references(root, text, folder, wide=True, memo=None):
    """Repo paths a text names (folders end /) and whether it names the whole repo; wide=False: no widening."""
    memo = {} if memo is None else memo
    text = HERE_FORMS.sub("$here/", text)
    text = text if wide else re.sub(r"""(["'])/(skills|dev)/""", r"\1\2/", text)
    found, whole = set(), bool(ROOT.search(text))
    if BARE.search(text) or (not wide and CD_SKILLS.search(text)):
        found.add("skills/")
    for name in SKILL_NAME.findall(text) if wide else ():
        found.add("skills/%s/" % name)
    for raw in PATH.findall(text):
        raw = raw.rstrip(".")
        for cand in {raw, os.path.normpath(os.path.join(folder, raw)).replace("\\", "/")}:
            if cand.startswith("/") or cand.split("/")[0] == ".git":
                continue
            kind = narrow.kind(memo, os.path.join(root, cand))
            if kind == "d":
                cand = cand.rstrip("/") + "/"
            if kind in ("d", "f"):
                found.add(widen(cand) if wide else cand)
    return found, whole
