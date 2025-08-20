import ast
import importlib.util
from pathlib import Path

root = Path("E:/Dropbox/code/ZVIC")
py_files = [str(p) for p in root.rglob("*.py")]
imports = {}
for f in py_files:
    try:
        src = open(f, "rb").read().decode("utf-8")
    except Exception as e:
        print("SKIP", f, e)
        continue
    try:
        tree = ast.parse(src)
    except Exception as e:
        print("PARSE_ERR", f, e)
        continue
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                top = n.name.split(".")[0]
                imports.setdefault(top, set()).add(f)
        elif isinstance(node, ast.ImportFrom):
            if node.module is None:
                continue
            top = node.module.split(".")[0]
            # skip relative imports
            if node.level > 0:
                continue
            imports.setdefault(top, set()).add(f)

# classify stdlib vs third-party by attempting importlib.util.find_spec and checking origin
stdlib = set()
third = set()
missing = set()
for mod in sorted(imports):
    if mod in ("__future__",):
        stdlib.add(mod)
        continue
    try:
        spec = importlib.util.find_spec(mod)
    except Exception:
        spec = None
    if spec is None:
        # not importable in current env
        missing.add(mod)
    else:
        origin = getattr(spec, "origin", None) or ""
        if "site-packages" in origin or "dist-packages" in origin:
            third.add(mod)
        else:
            # heuristics: builtins, stdlib, local package (like zvic)
            if origin and str(root) in str(origin):
                # local package
                stdlib.add(mod)
            else:
                stdlib.add(mod)

# read pyproject optional deps
import re
import tomllib

with open("pyproject.toml", "rb") as f:
    pj = tomllib.load(f)

proj = pj.get("project", {})


def top_name(spec):
    m = re.match(r"^([A-Za-z0-9_.+-]+)", spec)
    return m.group(1) if m else spec


deps = set([top_name(d) for d in proj.get("dependencies", [])])
opt = proj.get("optional-dependencies", {})
opt_deps = set()
for v in opt.values():
    for it in v:
        opt_deps.add(top_name(it))

print("\nSUMMARY")
print("Total modules imported top-level:", len(imports))
print("Third-party detected (heuristic):", sorted(third))
print("Missing (not importable here):", sorted(missing))
print("Declared deps in pyproject.dependencies:", sorted(deps))
print("Declared optional deps:", sorted(opt_deps))

# Now list any third-party modules not declared in deps or optional_deps and not local (zvic)
candidates = []
for mod in sorted(third | missing):
    if mod in deps:
        continue
    if mod in opt_deps:
        continue
    if mod in ("zvic", "tests", "src"):
        continue
    candidates.append(mod)

print("\nSuggested to add to pyproject (if used at runtime):")
print("\n".join(candidates) if candidates else "(none)")

# print small mapping for review
print("\nDetailed import -> files (truncated):")
for mod in sorted(imports):
    files = list(imports[mod])
    if len(files) > 5:
        files = files[:5] + ["..."]
    print(mod, "->", files)
