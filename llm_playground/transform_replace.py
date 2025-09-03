#!/usr/bin/env python3
"""Transform-and-replace utility for ZvIC-instrumented modules.

Usage: python transform_replace.py <module.name>

This script performs the triple-check described in the project:
- check __zvic_transformed__ flag
- verify injected helpers identity (assumption, _)
- if not transformed, locate ZvIC AST transformer at runtime, transform the module
  source, compile and exec into a fresh module object, then atomically replace
  the entry in sys.modules. It reports reference counts before and after and
  runs a garbage collection attempt to ensure old module memory can be freed.

Place this script in `llm_playground` and run it there for multi-command flows.
"""

from __future__ import annotations

import argparse
import ast
import contextlib
import gc
import importlib
import inspect
import os
import pkgutil
import sys
import types

try:
    import zvic
    from zvic import utils as zvic_utils
except Exception:
    zvic = None
    zvic_utils = None


def triple_check(mod) -> dict:
    gl = vars(mod)
    flag = bool(gl.get("__zvic_transformed__", False))
    assumption_ok = False
    underscore_ok = False
    if zvic is not None and zvic_utils is not None:
        assumption_ok = gl.get("assumption") is getattr(
            zvic, "assumption", None
        ) or gl.get("assumption") is getattr(zvic_utils, "assumption", None)
        underscore_ok = gl.get("_") is getattr(zvic_utils, "_", None)
    return {
        "flag": flag,
        "assumption_is_zvic": bool(assumption_ok),
        "underscore_is_zvic": bool(underscore_ok),
    }


def find_transformer() -> type | None:
    """Dynamically search zvic submodules for a NodeTransformer-style class.

    Returns the transformer class or None.
    """
    if zvic is None:
        return None
    # Preferred known locations
    preferred = [
        "zvic.annotation_constraints",
        "zvic.import_hook",
        "zvic.main",
    ]
    for modname in preferred:
        try:
            mod = importlib.import_module(modname)
        except Exception:
            continue
        for attr in ("AnnotateCallsTransformer", "AnnotateTransformer", "Annotator"):
            obj = getattr(mod, attr, None)
            if inspect.isclass(obj):
                return obj

    # Fallback: scan zvic submodules heuristically
    base_path = os.path.dirname(getattr(zvic, "__file__", ""))
    for finder, name, ispkg in pkgutil.iter_modules([base_path]):
        try:
            full = f"{zvic.__name__}.{name}"
            mod = importlib.import_module(full)
        except Exception:
            continue
        for attr in dir(mod):
            if (
                "annotat" in attr.lower()
                or "transform" in attr.lower()
                or "annotate" in attr.lower()
            ):
                obj = getattr(mod, attr)
                if inspect.isclass(obj):
                    try:
                        bases = [b.__name__ for b in inspect.getmro(obj)]
                    except Exception:
                        bases = []
                    if (
                        "NodeTransformer" in ",".join(bases)
                        or "Transformer" in obj.__name__
                    ):
                        return obj
    return None


def transform_source_with(transformer_cls, source: str, filename: str):
    tree = ast.parse(source, filename=filename)
    transformer = transformer_cls()
    new_tree = transformer.visit(tree)
    ast.fix_missing_locations(new_tree)
    code_obj = compile(new_tree, filename, "exec")
    try:
        transformed_src = ast.unparse(new_tree)
    except Exception:
        transformed_src = ""
    return code_obj, transformed_src


class LocalFallbackTransformer(ast.NodeTransformer):
    """A minimal fallback transformer used for experiments.

    It inserts a `_zvic_marker()` call as the first statement of every function
    definition. This is intentionally simple and safe for testing the replace
    flow when ZvIC is not available.
    """

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        self.generic_visit(node)
        call = ast.Expr(
            ast.Call(
                func=ast.Name(id="_zvic_marker", ctx=ast.Load()), args=[], keywords=[]
            )
        )
        node.body.insert(0, call)
        return node

    def visit_AsyncFunctionDef(
        self, node: ast.AsyncFunctionDef
    ) -> ast.AsyncFunctionDef:
        self.generic_visit(node)
        call = ast.Expr(
            ast.Await(
                ast.Call(
                    func=ast.Name(id="_zvic_marker", ctx=ast.Load()),
                    args=[],
                    keywords=[],
                )
            )
        )
        # for async functions insert an await of the marker if any
        node.body.insert(0, call)
        return node


def replace_module(
    module_name: str, force: bool = False, dry_run: bool = False
) -> dict:
    # Ensure project root (parent of workspace) and local 'src' are on sys.path so imports work
    this_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(this_dir, os.pardir))
    src_dir = os.path.join(project_root, "src")
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # Also add local ZVIC source if present (makes finding transformer easier)
    zvic_src = os.path.abspath(os.path.join(project_root, os.pardir, "ZVIC", "src"))
    if os.path.isdir(zvic_src) and zvic_src not in sys.path:
        sys.path.insert(0, zvic_src)

    if module_name not in sys.modules:
        try:
            importlib.import_module(module_name)
        except Exception:
            return {
                "ok": False,
                "reason": "module_not_loaded",
                "project_root": project_root,
            }
    old_mod = sys.modules[module_name]
    checks = triple_check(old_mod)
    # If module is already transformed and helpers match, nothing to do.
    if (
        checks.get("flag")
        and checks.get("assumption_is_zvic")
        and checks.get("underscore_is_zvic")
    ):
        return {"ok": False, "reason": "already_transformed", "checks": checks}

    filename = getattr(old_mod, "__file__", None)
    if not filename or not os.path.exists(filename):
        return {"ok": False, "reason": "no_source_file", "checks": checks}

    with open(filename, "r", encoding="utf-8") as f:
        source = f.read()

    # AST-based detection: check for a top-level call to `constrain_this_module()`
    def has_constrain_call(src: str) -> bool:
        try:
            tree = ast.parse(src)
        except Exception:
            return False
        for node in tree.body:
            # look for expressions like: constrain_this_module()
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                func = node.value.func
                if isinstance(func, ast.Name) and func.id == "constrain_this_module":
                    return True
                if (
                    isinstance(func, ast.Attribute)
                    and func.attr == "constrain_this_module"
                ):
                    return True
        return False

    auto_forced = has_constrain_call(source)

    # If the flag is present but helpers don't match, be conservative unless
    # forced either by the CLI `--force` or by the module's own
    # `constrain_this_module()` call (auto_forced).
    forced_note = None
    if checks.get("flag") and not (
        checks.get("assumption_is_zvic") and checks.get("underscore_is_zvic")
    ):
        if not (force or auto_forced):
            return {"ok": False, "reason": "marked_incompatible", "checks": checks}
        forced_note = "forcing_replace_despite_flag_mismatch"

    # Prefer a ZvIC-provided helper if available: transform_and_compile_source
    code_obj = None
    transformed_src = ""
    if zvic is not None and hasattr(zvic, "transform_and_compile_source"):
        try:
            # helper may accept (path) or (source, path) and may return
            # (transformed_source, code_obj) or (code_obj, transformed_source)
            v = zvic.transform_and_compile_source(filename)
            if isinstance(v, tuple) and len(v) == 2:
                a, b = v
                # detect which is code object
                if isinstance(a, type(compile("", "", "exec"))):
                    code_obj, transformed_src = a, b
                elif isinstance(b, type(compile("", "", "exec"))):
                    transformed_src, code_obj = a, b
                else:
                    # fallback: assume (src, code)
                    transformed_src, code_obj = a, b
            else:
                # unexpected return, treat as failure
                code_obj = None
        except Exception:
            code_obj = None

    transformer_cls = None
    used_fallback = False
    if code_obj is None:
        transformer_cls = find_transformer()
        if transformer_cls is None:
            # If the user passed --force or we auto-forced due to a
            # `constrain_this_module()` in the source, use the local fallback
            # transformer rather than failing.
            if force or auto_forced:
                transformer_cls = LocalFallbackTransformer
                used_fallback = True
            else:
                return {"ok": False, "reason": "no_transformer_found", "checks": checks}

    # report refcount of old module before replacement
    old_refcount_before = sys.getrefcount(old_mod)

    # transform and compile (if not already provided by ZvIC helper)
    if code_obj is None:
        code_obj, transformed_src = transform_source_with(
            transformer_cls, source, filename
        )

    # create new module object and exec (unless dry-run)
    new_mod = types.ModuleType(module_name)
    # copy basic metadata
    for attr in ("__file__", "__package__", "__spec__", "__loader__"):
        if hasattr(old_mod, attr):
            setattr(new_mod, attr, getattr(old_mod, attr))

    # provide zvic helpers if available
    if zvic_utils is not None:
        new_mod.__dict__.setdefault("_", zvic_utils._)
        new_mod.__dict__.setdefault(
            "assumption", getattr(zvic_utils, "assumption", None)
        )

    # if we are using the fallback, also provide a noop marker so the inserted
    # calls resolve
    if used_fallback:

        def _zvic_marker():
            return None

        new_mod.__dict__["_zvic_marker"] = _zvic_marker

    # Exec and replacement are conditional based on dry_run flag provided by
    # the caller. In dry-run mode we do not exec into sys.modules nor alter
    # the running process; we only report what would happen and provide a
    # transformed source preview.

    if not dry_run:
        exec(code_obj, new_mod.__dict__)

        # mark transformed only after exec succeeded
        new_mod.__dict__["__zvic_transformed__"] = True

        # replace in sys.modules atomically
        sys.modules[module_name] = new_mod

        # attempt to clear old references and run gc
        with contextlib.suppress(Exception):
            del old_mod
        gc.collect()

        new_refcount_after = sys.getrefcount(sys.modules[module_name])
        out = {
            "ok": True,
            "module": module_name,
            "checks_before": checks,
            "old_refcount_before": old_refcount_before,
            "new_refcount_after": new_refcount_after,
            "transformed_source_preview": transformed_src[:400],
        }
    else:
        # Dry-run: do not exec or replace the module; only report what would
        # happen and include the transformed source preview if available.
        out = {
            "ok": True,
            "module": module_name,
            "checks_before": checks,
            "old_refcount_before": old_refcount_before,
            "would_replace": True,
            "transformed_source_preview": transformed_src[:400],
            "dry_run": True,
        }
    if forced_note:
        out["note"] = forced_note
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument(
        "module", help="module name to transform/replace (e.g. cidstore.utils)"
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="force replacement even if module is marked transformed but helpers mismatch",
    )
    p.add_argument(
        "--dry-run",
        dest="dry_run",
        action="store_true",
        help="do not exec or replace the module; only show the transformed preview",
    )
    args = p.parse_args()
    res = replace_module(args.module, force=args.force, dry_run=args.dry_run)
    import json

    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
