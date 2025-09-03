"""Transform-and-replace developer tool for ZvIC.

This module provides a small developer helper that can apply the ZvIC AST
transformer to a module source, optionally replace the running module in
`sys.modules`, and provide a dry-run preview. It is intentionally conservative
and will prefer ZvIC's own `transform_and_compile_source` helper when
available.
"""

from __future__ import annotations

import ast
import gc
import importlib
import importlib.machinery
import importlib.util
import inspect
import os
import pkgutil
import sys
import types
from contextlib import contextmanager

# Use PEP 604 union types (e.g. `list[str] | None`) on Python 3.12; no typing.Optional import needed


def triple_check(mod) -> dict:
    gl = vars(mod)
    flag = bool(gl.get("__zvic_transformed__", False))
    assumption_ok = False
    underscore_ok = False
    try:
        zvic_utils = importlib.import_module("zvic.utils")
    except Exception:
        zvic_utils = None
    try:
        zvic = importlib.import_module("zvic")
    except Exception:
        zvic = None
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
    try:
        zvic = importlib.import_module("zvic")
    except Exception:
        zvic = None
    if zvic is None:
        return None

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
        node.body.insert(0, call)
        return node


def has_constrain_call(src: str) -> bool:
    try:
        tree = ast.parse(src)
    except Exception:
        return False
    for node in tree.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            func = node.value.func
            if isinstance(func, ast.Name) and func.id == "constrain_this_module":
                return True
            if isinstance(func, ast.Attribute) and func.attr == "constrain_this_module":
                return True
    return False


def replace_module(
    module_name: str,
    force: bool = False,
    dry_run: bool = False,
    patch_refs: bool = False,
) -> dict:
    @contextmanager
    def _ensure_transient_constrain():
        injected = False
        try:
            zvic_pkg = importlib.import_module("zvic")
        except Exception:
            zvic_pkg = None
        if zvic_pkg is not None and not hasattr(zvic_pkg, "constrain_this_module"):
            setattr(zvic_pkg, "constrain_this_module", lambda: None)
            injected = True
        try:
            yield
        finally:
            if injected and zvic_pkg is not None:
                try:
                    delattr(zvic_pkg, "constrain_this_module")
                except Exception:
                    pass

    module_loaded = True
    filename = None
    source = None
    if module_name not in sys.modules:
        try:
            with _ensure_transient_constrain():
                importlib.import_module(module_name)
        except Exception:
            # Attempt to locate the source file using importlib utilities first,
            # then fall back to manual sys.path scanning.
            module_loaded = False
            module_spec = None
            try:
                module_spec = importlib.util.find_spec(module_name)
            except Exception:
                module_spec = None
            if module_spec is not None and getattr(module_spec, "origin", None):
                filename = module_spec.origin
            else:
                # Try a PathFinder lookup which accepts an explicit path list
                try:
                    import importlib.machinery

                    spec2 = importlib.machinery.PathFinder.find_spec(
                        module_name, sys.path
                    )
                except Exception:
                    spec2 = None
                if spec2 is not None and getattr(spec2, "origin", None):
                    filename = spec2.origin
                else:
                    module_parts = module_name.split(".")
                    for p in sys.path:
                        if not p:
                            p = os.curdir
                        candidate = os.path.join(p, *module_parts) + ".py"
                        if os.path.exists(candidate):
                            filename = candidate
                            break
                        candidate_pkg = os.path.join(p, *module_parts, "__init__.py")
                        if os.path.exists(candidate_pkg):
                            filename = candidate_pkg
                            break
            if filename is None:
                return {"ok": False, "reason": "module_not_loaded"}
            with open(filename, "r", encoding="utf-8") as f:
                source = f.read()
    if module_loaded:
        old_mod = sys.modules[module_name]
        checks = triple_check(old_mod)
        filename = getattr(old_mod, "__file__", None)
    else:
        old_mod = None
        checks = {
            "flag": False,
            "assumption_is_zvic": False,
            "underscore_is_zvic": False,
        }
    if (
        checks.get("flag")
        and checks.get("assumption_is_zvic")
        and checks.get("underscore_is_zvic")
    ):
        return {"ok": False, "reason": "already_transformed", "checks": checks}
    # `filename` may have been determined above (either from the loaded module
    # or by locating the source on sys.path). Ensure it exists before proceeding.
    if not filename or not os.path.exists(filename):
        return {"ok": False, "reason": "no_source_file", "checks": checks}

    if source is None:
        with open(filename, "r", encoding="utf-8") as f:
            source = f.read()

    auto_forced = has_constrain_call(source)

    forced_note = None
    if checks.get("flag") and not (
        checks.get("assumption_is_zvic") and checks.get("underscore_is_zvic")
    ):
        if not (force or auto_forced):
            return {"ok": False, "reason": "marked_incompatible", "checks": checks}
        forced_note = "forcing_replace_despite_flag_mismatch"

    code_obj = None
    transformed_src = ""
    try:
        zvic_mod = importlib.import_module("zvic")
    except Exception:
        zvic_mod = None

    if zvic_mod is not None and hasattr(zvic_mod, "transform_and_compile_source"):
        try:
            v = zvic_mod.transform_and_compile_source(filename)
            if isinstance(v, tuple) and len(v) == 2:
                a, b = v
                if isinstance(a, type(compile("", "", "exec"))):
                    code_obj, transformed_src = a, b
                elif isinstance(b, type(compile("", "", "exec"))):
                    transformed_src, code_obj = a, b
                else:
                    transformed_src, code_obj = a, b
            else:
                code_obj = None
        except Exception:
            code_obj = None

    transformer_cls = None
    used_fallback = False
    if code_obj is None:
        transformer_cls = find_transformer()
        if transformer_cls is None:
            if force or auto_forced:
                transformer_cls = LocalFallbackTransformer
                used_fallback = True
            else:
                return {"ok": False, "reason": "no_transformer_found", "checks": checks}

    old_refcount_before = sys.getrefcount(old_mod) if old_mod is not None else 0

    if code_obj is None:
        code_obj, transformed_src = transform_source_with(
            transformer_cls, source, filename
        )

    new_mod = types.ModuleType(module_name)
    # Ensure the new module has a sensible __file__ when we located the
    # source via importlib/path scanning even if the module wasn't previously
    # loaded into sys.modules (old_mod may be None in that case).
    if filename:
        try:
            setattr(new_mod, "__file__", filename)
        except Exception:
            # best-effort: ignore attribute errors
            pass
    for attr in ("__package__", "__spec__", "__loader__"):
        if hasattr(old_mod, attr):
            setattr(new_mod, attr, getattr(old_mod, attr))

    try:
        zvic_utils = importlib.import_module("zvic.utils")
    except Exception:
        zvic_utils = None
    if zvic_utils is not None:
        new_mod.__dict__.setdefault("_", getattr(zvic_utils, "_", None))
        new_mod.__dict__.setdefault(
            "assumption", getattr(zvic_utils, "assumption", None)
        )

    if used_fallback:

        def _zvic_marker():
            return None

        new_mod.__dict__["_zvic_marker"] = _zvic_marker

    patched_report: dict[str, list[str]] | None = None
    if not dry_run:
        exec(code_obj, new_mod.__dict__)
        new_mod.__dict__["__zvic_transformed__"] = True
        sys.modules[module_name] = new_mod

        # Optional aggressive patching: scan other modules for attributes
        # that still point to objects from the old module and rebind them
        # to the equivalent objects from the new module. This is invasive
        # and therefore opt-in via `patch_refs`.
        patched_report = None
        if patch_refs and old_mod is not None:
            patched_report = {}
            try:
                project_root = os.getcwd()
            except Exception:
                project_root = None

            def module_is_in_project(m: types.ModuleType) -> bool:
                try:
                    mf = getattr(m, "__file__", None)
                    if not mf:
                        return False
                    # Normalize and check if module file is inside project_root
                    if (
                        project_root
                        and os.path.commonpath([project_root, os.path.abspath(mf)])
                        == project_root
                    ):
                        return True
                except Exception:
                    pass
                return False

            # Build a map of old object's id -> attribute path in old module
            old_members = {
                name: getattr(old_mod, name)
                for name in dir(old_mod)
                if not name.startswith("__")
            }
            old_id_map = {id(v): name for name, v in old_members.items()}

            for modname, mod in list(sys.modules.items()):
                if not isinstance(mod, types.ModuleType):
                    continue
                if modname == module_name:
                    continue
                if not module_is_in_project(mod):
                    # Don't patch third-party modules by default
                    continue
                patched_names: list[str] = []
                for attr in dir(mod):
                    if attr.startswith("__"):
                        continue
                    try:
                        val = getattr(mod, attr)
                    except Exception:
                        continue
                    if id(val) in old_id_map:
                        # Found a reference to an object from the old module.
                        old_name = old_id_map[id(val)]
                        if hasattr(new_mod, old_name):
                            try:
                                setattr(mod, attr, getattr(new_mod, old_name))
                                patched_names.append(attr)
                            except Exception:
                                # best-effort: ignore failures
                                pass
                if patched_names:
                    patched_report[modname] = patched_names

        # Drop the local reference to the old module and run GC to update refcounts.
        # Avoid using `del old_mod` since that creates a local binding in all
        # branches and can lead to UnboundLocalError; rely on GC instead.
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

        if patched_report:
            out["patched"] = patched_report

        # Optional aggressive patching: scan other modules for attributes
        # that still point to objects from the old module and rebind them
        # to the equivalent objects from the new module. This is invasive
        # and therefore opt-in via `patch_refs`.
        if patch_refs and old_mod is not None:
            patched_report = {}
            try:
                project_root = os.getcwd()
            except Exception:
                project_root = None

            def module_is_in_project(m: types.ModuleType) -> bool:
                try:
                    mf = getattr(m, "__file__", None)
                    if not mf:
                        return False
                    # Normalize and check if module file is inside project_root
                    if (
                        project_root
                        and os.path.commonpath([project_root, os.path.abspath(mf)])
                        == project_root
                    ):
                        return True
                except Exception:
                    pass
                return False

            # Build a map of old object's id -> attribute path in old module
            old_members = {
                name: getattr(old_mod, name)
                for name in dir(old_mod)
                if not name.startswith("__")
            }
            old_id_map = {id(v): name for name, v in old_members.items()}

            for modname, mod in list(sys.modules.items()):
                if not isinstance(mod, types.ModuleType):
                    continue
                if modname == module_name:
                    continue
                if not module_is_in_project(mod):
                    # Don't patch third-party modules by default
                    continue
                patched_names: list[str] = []
                for attr in dir(mod):
                    if attr.startswith("__"):
                        continue
                    try:
                        val = getattr(mod, attr)
                    except Exception:
                        continue
                    if id(val) in old_id_map:
                        # Found a reference to an object from the old module.
                        old_name = old_id_map[id(val)]
                        if hasattr(new_mod, old_name):
                            try:
                                setattr(mod, attr, getattr(new_mod, old_name))
                                patched_names.append(attr)
                            except Exception:
                                # best-effort: ignore failures
                                pass
                if patched_names:
                    patched_report[modname] = patched_names
            if patched_report:
                out["patched"] = patched_report
    else:
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


def main(argv: list[str] | None = None):
    import argparse
    import json

    p = argparse.ArgumentParser()
    p.add_argument("module")
    p.add_argument("--force", action="store_true")
    p.add_argument("--dry-run", dest="dry_run", action="store_true")
    p.add_argument(
        "--patch-refs",
        dest="patch_refs",
        action="store_true",
        help="Aggressively patch other project modules to point to new objects",
    )
    args = p.parse_args(argv)
    res = replace_module(
        args.module,
        force=args.force,
        dry_run=args.dry_run,
        patch_refs=bool(getattr(args, "patch_refs", False)),
    )
    print(json.dumps(res, indent=2))
