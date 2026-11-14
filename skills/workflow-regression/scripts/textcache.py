"""Bounded per-run memory for lanes.py (#4151): file text, and yes/no answers that every row would otherwise recompute.

Texts      file name -> text, at most LIMIT characters held; the oldest text is dropped, the name stays (tiers.unsafe lists
           the files read from the cache's "text"). A dropped text is read again from disk: slower, never different.
names      whether a text names a path: the path, its basename, or `import <stem>` for a .py file.
kind       "d", "f" or "" for a path, asked of the disk once per run.
"""
import collections
import os
import re

LIMIT = 32000000


class Texts(dict):
    def __init__(self):
        super().__init__()
        self.live, self.size = collections.OrderedDict(), 0

    def load(self, root, rel):
        if rel in self.live:
            self.live.move_to_end(rel)
            return self[rel]
        try:
            with open(os.path.join(root, rel), errors="replace") as handle:
                text = handle.read(400000)
        except OSError:
            text = None
        self[rel] = text
        self.live[rel] = len(text or "")
        self.size += self.live[rel]
        while self.size > LIMIT and len(self.live) > 1:
            old, count = self.live.popitem(last=False)
            self[old], self.size = "", self.size - count
        return text


def names(text, path):
    name = os.path.basename(path)
    stem = re.escape(name[:-3]) if name.endswith(".py") else None
    return path in text or name in text or bool(stem and re.search(r"(?m)^\s*(?:from|import)\s+(?:[\w, ]*\b)?%s\b" % stem, text))


def kind(memo, full):
    if full not in memo:
        memo[full] = "d" if os.path.isdir(full) else "f" if os.path.isfile(full) else ""
    return memo[full]
