#!/usr/bin/env python3
# windows: ok
# reads: dev/toy/move-manifest.json skills/workflow-delivery/scripts/ skills/workflow-release/scripts/merge.py
"""The move check of the make-room goal (pure moves of whole functions into sibling modules), plan section 3.
usage: move-check.py check [--root DIR] [--pin SHA]    prove every move (--pin reads the script and module texts from that commit) against the comparison base; print PASS or FAIL lines, exit 1 on any FAIL
       move-check.py --derive              write the free-name prefixes of each moved function into the manifest
       move-check.py --apply NAME          perform the move of one manifest entry (script stem) on the working tree
       move-check.py --inventory           list every toy, row and package rule that names a moved function or reads a moved script
The manifest (move-manifest.json) holds the comparison base sha, then per move: script, module, doc, functions, and the derived
prefixes. Names a moved function uses are `_s.NAME` when they stay in the old script, plain when they move with it, and a
standard-library module is imported again in the new module. The only lines that are not a byte-identical move are the header:
docstring, imports, the DEL-10 guard line, the registration line, the `_s` import and the re-export line."""
import ast
import builtins
import json
import os
import re
import subprocess
import sys
import symtable

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
MAN = os.path.join(HERE, "move-manifest.json")
GIT = os.environ.get("MR_GIT") or REPO  # where git commands run (a row runs this from an archive of a pinned commit)
GUARD = 'os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")'
BAN = ("__file__", "__name__", "traceback", "inspect", "_getframe")
OUT = []


def say(ok, text):
    OUT.append(ok)
    print(("PASS: " if ok else "FAIL: ") + text)


def base_text(man, path):
    got = subprocess.run(["git", "show", "%s:%s" % (man["base"], path)], capture_output=True, text=True, cwd=GIT)
    return got.stdout if got.returncode == 0 else ""


PIN = [""]


def read(root, path):
    if PIN[0]:
        got = subprocess.run(["git", "show", "%s:%s" % (PIN[0], path)], capture_output=True, text=True, cwd=GIT)
        return got.stdout.replace("\r\n", "\n")
    with open(os.path.join(root, path), encoding="utf-8", newline="") as handle:
        return handle.read().replace("\r\n", "\n")


def tops(tree):
    return {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}


def seg(lines, node):
    start = node.decorator_list[0].lineno if node.decorator_list else node.lineno
    return "\n".join(lines[start - 1:node.end_lineno])


def tables(top, name):
    for child in top.get_children():
        if child.get_name() == name and child.get_type() == "function":
            return child
    raise KeyError(name)


def used_globals(table, bound):
    """{name: 'g' | 'l'} over a function table and its nested ones: a name seen as a global anywhere in it."""
    found = {}
    for sym in table.get_symbols():
        n = sym.get_name()
        if sym.is_global() and sym.is_referenced() or sym.is_global() and sym.is_assigned():
            found[n] = "g"
        elif sym.is_local() and n not in found:
            found.setdefault(n, "l")
    for child in table.get_children():
        for n, kind in used_globals(child, bound).items():
            found[n] = "g" if kind == "g" else found.get(n, "l")
    return found


def classify(text, path, funcs):
    """Per function: (prefix names, standard-library names), from the free names of the base text."""
    tree, top = ast.parse(text), symtable.symtable(text, path, "exec")
    names = {s.get_name() for s in top.get_symbols() if s.is_assigned() or s.is_imported() or s.is_namespace()}
    std = {}
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in sys.stdlib_module_names and not alias.asname:
                    std[alias.name.split(".")[0]] = "import " + alias.name
    out = {}
    for fn in funcs:
        pre, sd = set(), set()
        for n, kind in used_globals(tables(top, fn), names).items():
            if kind != "g" or n in funcs:
                continue
            if n in std:
                sd.add(n)
            elif n in names:
                pre.add(n)
            elif not hasattr(builtins, n):
                pre.add(n)
        out[fn] = (sorted(pre), sorted(sd))
    return out, std


def header_names(node):
    """Names a def evaluates when it is defined (defaults, decorators, annotations)."""
    parts = list(node.args.defaults) + [d for d in node.args.kw_defaults if d] + list(node.decorator_list)
    parts += [a.annotation for a in node.args.args + node.args.kwonlyargs if a.annotation] + ([node.returns] if node.returns else [])
    return {m.id for p in parts for m in ast.walk(p) if isinstance(m, ast.Name)}


def derive():
    man = json.load(open(MAN))
    for move in man["moves"]:
        text = base_text(man, move["script"])
        info, std = classify(text, move["script"], move["functions"])
        tree = tops(ast.parse(text))
        bad = [f for f in move["functions"] if f not in tree]
        if bad:
            sys.exit("REFUSED: %s has no function %s at the base" % (move["script"], ", ".join(bad)))
        move["prefix"] = {f: info[f][0] for f in move["functions"]}
        move["std"] = {n: std[n] for f in move["functions"] for n in info[f][1]}
        late = {f: sorted(header_names(tree[f]) & (set(info[f][0]) | set(move["functions"]))) for f in move["functions"]}
        if any(late.values()):
            sys.exit("REFUSED: a moved def evaluates a script name at definition time: %s" % late)
    json.dump(man, open(MAN, "w"), indent=1)
    print("DERIVED %d moves" % len(man["moves"]))


def rewrite(lines, node, prefix):
    """The function's source with each prefixed global name written `_s.NAME`."""
    first = node.decorator_list[0].lineno if node.decorator_list else node.lineno
    body = ["" + l for l in lines[first - 1:node.end_lineno]]
    hits = [(m.lineno - first, m.col_offset, len(m.id)) for m in ast.walk(node) if isinstance(m, ast.Name) and m.id in prefix]
    for row, col, size in sorted(hits, reverse=True):
        raw = body[row].encode("utf-8")
        body[row] = (raw[:col] + b"_s." + raw[col:]).decode("utf-8")
    return "\n".join(body)


def apply(name):
    man = json.load(open(MAN))
    move = next(m for m in man["moves"] if os.path.basename(m["script"])[:-3] == name)
    path = os.path.join(REPO, move["script"])
    text = open(path, encoding="utf-8", newline="").read()
    lines, tree = text.split("\n"), ast.parse(text)
    fns, drop, chunks = tops(tree), [], []
    for f in move["functions"]:
        node = fns[f]
        chunks.append(rewrite(lines, node, set(move["prefix"][f])))
        first = node.decorator_list[0].lineno if node.decorator_list else node.lineno
        drop.append((first, node.end_lineno))
    code = "\n\n\n".join(chunks)
    std = sorted({v for v in move["std"].values()} | ({"import os"} if "subprocess" in code else set()))
    head = ['"""%s"""' % move["doc"]] + std + ([GUARD] if "subprocess" in code else [])
    mod = "\n".join(head) + "\n\n\n" + code + "\n\n\nimport %s as _s  # noqa: E402\n" % name
    open(os.path.join(os.path.dirname(path), move["module"] + ".py"), "w", encoding="utf-8", newline="").write(mod)
    keep = [l for i, l in enumerate(lines, 1) if not any(a <= i <= b for a, b in drop)]
    new = re.sub(r"\n{4,}", "\n\n\n", "\n".join(keep))
    sibs = {f[:-3] for f in os.listdir(os.path.dirname(path)) if f.endswith(".py")}
    reg = 'sys.modules.setdefault("%s", sys.modules[__name__])' % name
    if reg not in new and 'sys.modules.setdefault("%s"' % name not in new:
        t2 = ast.parse(new)
        first = next(n for n in t2.body if isinstance(n, (ast.Import, ast.ImportFrom)) and (n.names[0].name if isinstance(n, ast.Import) else n.module or "").split(".")[0] in sibs - {name})
        new = "\n".join(new.split("\n")[:first.lineno - 1] + [reg] + new.split("\n")[first.lineno - 1:])
    out = "from %s import %s  # noqa: E402,F401" % (move["module"], ", ".join(move["functions"]))
    t3 = ast.parse(new)
    tail = next((n for n in t3.body if isinstance(n, ast.If) and "__name__" in ast.dump(n.test)), None)
    rows = new.split("\n")
    at = tail.lineno - 1 if tail else len(rows)
    new = "\n".join(rows[:at] + [out, "", ""] + rows[at:])
    open(path, "w", encoding="utf-8", newline="").write(new)
    print("MOVED %s: %d functions, %d bytes into %s.py" % (name, len(chunks), len(mod.encode()), move["module"]))


def strings(tree):
    return sorted(repr(n.value) for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str))


def check(root):
    man = json.load(open(MAN))
    for move in man["moves"]:
        stem = os.path.basename(move["script"])[:-3]
        folder = os.path.dirname(move["script"])
        mpath = os.path.join(folder, move["module"] + ".py")
        if not PIN[0] and not os.path.exists(os.path.join(root, mpath)):
            print("SKIP %s: not moved yet" % stem)
            continue
        btext, ntext, mtext = base_text(man, move["script"]), read(root, move["script"]), read(root, mpath)
        btree, ntree, mtree = ast.parse(btext), ast.parse(ntext), ast.parse(mtext)
        blines, mlines = btext.split("\n"), mtext.split("\n")
        bf, nf, mf = tops(btree), tops(ntree), tops(mtree)
        for f in move["functions"]:
            pre = set(move["prefix"][f])
            node = mf.get(f)
            if f not in bf or node is None or f in nf:
                say(False, "%s: %s is not moved exactly once (base %s, old script %s, module %s)" % (stem, f, f in bf, f in nf, node is not None))
                continue
            plain = re.sub(r"\b_s\.(?=(%s)\b)" % "|".join(sorted(pre)) if pre else r"\b_s\.\b\b", "", seg(mlines, node))
            norm = ast.parse(plain).body[0]
            same = ast.dump(norm) == ast.dump(bf[f]) and plain == seg(blines, bf[f])
            say(same, "%s.%s moved byte-identical but for the _s. prefixes" % (stem, f))
            for m in ast.walk(node):
                if isinstance(m, ast.Attribute) and isinstance(m.value, ast.Name) and m.value.id == "_s":
                    print("PREFIX %s %s line %d: _s.%s" % (move["module"], f, m.lineno, m.attr))
            used = {m.id for m in ast.walk(bf[f]) if isinstance(m, ast.Name)} | {m.attr for m in ast.walk(bf[f]) if isinstance(m, ast.Attribute)}
            say(not (set(BAN) & used), "%s.%s uses none of %s" % (stem, f, ", ".join(BAN)))
        info, stds = classify(btext, move["script"], move["functions"])
        say(all(sorted(move["prefix"][f]) == info[f][0] for f in move["functions"]), "%s: the manifest's prefixes equal the free names derived from the base" % stem)
        mtop = symtable.symtable(mtext, mpath, "exec")
        mnames = {x.get_name() for x in mtop.get_symbols() if x.is_assigned() or x.is_imported() or x.is_namespace()}
        for f in move["functions"]:
            if f in mf:
                lost = sorted(n for n, k in used_globals(tables(mtop, f), mnames).items() if k == "g" and n not in mnames and not hasattr(builtins, n))
                say(not lost, "%s.%s has no unresolved global name%s" % (move["module"], f, (": " + ", ".join(lost)) if lost else ""))
        names = {n for n in mf} & set(move["functions"])
        say(f"from {move['module']} import " in ntext and all(f in ntext.split("from %s import" % move["module"])[-1].split("\n")[0] for f in move["functions"]),
            "%s re-exports its moved names from %s" % (stem, move["module"]))
        rest = [ast.dump(n) for n in btree.body if not (isinstance(n, ast.FunctionDef) and n.name in move["functions"])]
        have = [ast.dump(n) for n in ntree.body]
        extra = [n for n in ntree.body if ast.dump(n) not in rest]
        extra_ok = all(isinstance(n, (ast.ImportFrom, ast.Expr)) and ("sys.modules" in ast.unparse(n) or isinstance(n, ast.ImportFrom)) for n in extra)
        say(extra_ok and [d for d in have if d in rest] == rest, "%s: the rest of the script is the base's, plus only the registration and the re-export" % stem)
        body = [n for n in mtree.body if not (isinstance(n, ast.FunctionDef) and n.name in move["functions"])]
        okh = all(isinstance(n, (ast.Import, ast.Expr)) and (not isinstance(n, ast.Expr) or isinstance(n.value, ast.Constant) or ast.dump(n.value) == ast.dump(ast.parse(GUARD).body[0].value)) for n in body[:-1]) and ast.unparse(body[-1]) == "import %s as _s" % stem
        say(okh, "%s: the header of %s holds only the docstring, imports, the guard line and the _s import" % (move["module"], move["module"]))
        header = [n for n in mtree.body if not isinstance(n, ast.FunctionDef)]
        want = sorted(strings(btree))
        got = sorted(strings(ast.Module([n for n in ntree.body if ast.dump(n) in rest] + [n for n in mtree.body if isinstance(n, ast.FunctionDef)], [])))
        say(want == got, "%s and %s hold the base's string constants exactly" % (stem, move["module"]))
        for label, text in ((stem, ntext), (move["module"], mtext)):
            size = len(text.encode())
            say(size <= 13000, "%s is %d bytes (at most 13,000, room to 19,000)" % (label, size))
        say(("subprocess" not in mtext) or "GIT_TERMINAL_PROMPT" in mtext, "%s carries the DEL-10 guard where it starts processes" % move["module"])
    return all(OUT)


def inventory():
    man = json.load(open(MAN))
    names = {f for m in man["moves"] for f in m["functions"]} | {os.path.basename(m["script"]) for m in man["moves"]}
    pat = re.compile("|".join(r"\b%s\b" % re.escape(n) for n in sorted(names)))
    for rel in ("dev/toy", "dev/package.py", ".loop/regression.tsv"):
        full = os.path.join(REPO, rel)
        files = [os.path.join(full, f) for f in sorted(os.listdir(full))] if os.path.isdir(full) else [full]
        for f in files:
            if f.endswith((".json", ".bak")) or "move-" in f or not os.path.isfile(f):
                continue
            for n, line in enumerate(open(f, encoding="utf-8", errors="replace"), 1):
                if pat.search(line) and re.search(r"grep|split|open\(|read|cat |\.find\(|count", line):
                    print("%s:%d: %s" % (os.path.relpath(f, REPO), n, line.strip()[:150]))


def main(argv):
    if argv[:1] == ["--derive"]:
        return derive() or 0
    if argv[:1] == ["--apply"] and len(argv) == 2:
        return apply(argv[1]) or 0
    if argv[:1] == ["--inventory"]:
        return inventory() or 0
    if argv[:1] == ["check"]:
        root = argv[argv.index("--root") + 1] if "--root" in argv else REPO
        PIN[0] = argv[argv.index("--pin") + 1] if "--pin" in argv else ""
        return 0 if check(root) else 1
    print("usage: move-check.py check [--root DIR] [--pin SHA] | --derive | --apply NAME | --inventory")
    return 0 if argv[:1] in (["-h"], ["--help"]) else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
