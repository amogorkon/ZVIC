#!/usr/bin/env python3
"""Discover candidate AST transformer classes in local ZVIC installation."""

from __future__ import annotations

import ast
import importlib
import inspect
import os
import pkgutil
import sys

# Prepare local ZVIC src path (assume workspace layout)
repo_root = os.path.abspath(os.path.join(".."))
zvic_src = os.path.abspath(os.path.join(repo_root, "..", "ZVIC", "src"))
if os.path.isdir(zvic_src) and zvic_src not in sys.path:
    sys.path.insert(0, zvic_src)

try:
    import zvic
except Exception as e:
    print("Failed to import zvic:", e)
    sys.exit(1)

base = os.path.dirname(getattr(zvic, "__file__", ""))
print("zvic base:", base)

candidates = []
for finder, name, ispkg in pkgutil.iter_modules([base]):
    full = f"zvic.{name}"
    try:
        m = importlib.import_module(full)
    except Exception as e:
        print("Could not import", full, "->", e)
        continue
    for attr in dir(m):
        obj = getattr(m, attr)
        if inspect.isclass(obj):
            try:
                mro = inspect.getmro(obj)
            except Exception:
                mro = ()
            reason = []
            if any(c is ast.NodeTransformer for c in mro):
                reason.append("mro_contains_NodeTransformer")
            if "Annotat" in attr or "Annotate" in attr or "Transformer" in attr:
                reason.append("name_matches")
            if hasattr(obj, "visit_Call") or hasattr(obj, "visit_FunctionDef"):
                reason.append("has_visit_methods")
            if reason:
                candidates.append({
                    "module": full,
                    "class": attr,
                    "mro": [c.__name__ for c in mro],
                    "reason": reason,
                })

print("\nCandidates:")
for c in candidates:
    print(c)

print("\nDone")
