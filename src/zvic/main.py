import ast
import contextlib
import inspect
import sys
from collections.abc import Mapping
from pathlib import Path
from types import ModuleType
from typing import Any, get_args, get_origin, get_type_hints

from .ast_utils import transform_module
from .import_hook import ZvicFinder
from .utils import _, assumption, normalize_constraint

# More permissive canonical type to match function/class representations
CANONICAL = Mapping[str, Any]

__all__ = [
    "constrain_this_module",
    "transform_module",
    "install_import_hook",
    "uninstall_import_hook",
    "load_module",
    "canonicalize",
    "pprint_recursive",
    "transform_replace",
]


def constrain_this_module(*, return_lingering: bool = False):
    """Transform and replace the caller module in-place using the pure transformer.

    This function delegates the heavy lifting to the pure `transform_module`
    implementation (which returns a newly executed module and the transformed
    AST). It then updates the caller module's globals to point to
    the new objects (removing names which no longer exist) and performs a
    best-effort scan of other loaded modules to detect external references
    to old objects — if any are found a warning is emitted.
    """
    frame = inspect.currentframe()
    if frame is None or frame.f_back is None:
        raise RuntimeError("Could not find caller frame")
    caller_globals = frame.f_back.f_globals

    if "_" not in caller_globals:
        caller_globals["_"] = _
        with contextlib.suppress(Exception):
            import builtins

            if not hasattr(builtins, "_"):
                setattr(builtins, "_", _)
    if "assumption" not in caller_globals:
        caller_globals["assumption"] = assumption

    # Prevent recursion: only transform if not already transformed
    if caller_globals.get("__zvic_transformed__", False):
        return
    caller_globals["__zvic_transformed__"] = True

    filename = caller_globals.get("__file__")
    if not filename:
        raise RuntimeError("Caller module has no __file__; cannot transform")

    # Parse source AST to validate future import on older Pythons
    source = Path(filename).read_text(encoding="utf-8")
    parsed = ast.parse(source, filename=filename)
    if sys.version_info < (3, 13):
        body = parsed.body
        has_future_annotations = False

        idx = 0
        if (
            body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            idx = 1
        if (
            idx < len(body)
            and isinstance(body[idx], ast.ImportFrom)
            and body[idx].module == "__future__"
        ):
            for alias in body[idx].names:
                if alias.name == "annotations":
                    has_future_annotations = True
                    break
        if not has_future_annotations:
            # Insert the future import into the source so downstream parsing
            # and transformations see postponed annotations. We do this
            # automatically to avoid requiring the user to modify their code.
            import warnings

            warnings.warn(
                "`from __future__ import annotations` was inserted. This may or may not change runtime behaviour!",
                UserWarning,
            )

            class _Placeholder:
                def __getattr__(self, _):
                    return self

                def __call__(self, *a, **k):
                    return self

                def __bool__(self):
                    return False

                def __int__(self):
                    return 0

                def __index__(self):
                    return 0

                def __len__(self):
                    return 0

                def __mod__(self, other):
                    return 0

                def __rmod__(self, other):
                    return 0

                def __lt__(self, other):
                    return False

                def __le__(self, other):
                    return False

                def __gt__(self, other):
                    return False

                def __ge__(self, other):
                    return False

                def __eq__(self, other):
                    return False

                def __ne__(self, other):
                    return True

                def __add__(self, other):
                    return self

                def __radd__(self, other):
                    return self

                def __sub__(self, other):
                    return self

                def __rsub__(self, other):
                    return self

                def __repr__(self):
                    return "<_>"

            # Only set '_' if not already present to avoid clobbering user symbols
            if caller_globals.get("_") is None:
                caller_globals["_"] = _Placeholder()
                with contextlib.suppress(Exception):
                    import builtins

                    if not hasattr(builtins, "_"):
                        setattr(builtins, "_", _)
            # Prepend the future import after an optional module docstring
            insert_idx = 0
            if (
                body
                and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)
            ):
                # keep docstring as first element
                insert_idx = 1
            future_line = "from __future__ import annotations\n"
            # Modify the source string directly and reparse
            lines = source.splitlines(keepends=True)
            # Determine where to insert: after any initial shebang and docstring
            # If insert_idx == 1, we need to find the end of the docstring statement
            if insert_idx == 1:
                # Find the line index of the first statement after the docstring
                # We'll approximate by inserting after the first triple-quoted string
                # or after the first line if detection fails.
                try:
                    # Locate end of module docstring in the original source by using ast.get_docstring
                    mod_doc = ast.get_docstring(parsed)
                    if mod_doc is not None:
                        # Find the first occurrence of the docstring literal in the source
                        doc_node = parsed.body[0]
                        # Use lineno and end_lineno (available in Python 3.8+)
                        end_line = getattr(doc_node, "end_lineno", None)
                        if end_line is not None:
                            # Insert after that line
                            insert_at_char = sum(len(l) for l in lines[:end_line])
                            source = (
                                source[:insert_at_char]
                                + future_line
                                + source[insert_at_char:]
                            )
                        else:
                            # Fallback: insert after first line
                            source = future_line + source
                    else:
                        source = future_line + source
                except Exception:
                    source = future_line + source
            else:
                source = future_line + source
            # Reparse with the modified source
            parsed = ast.parse(source, filename=filename)

    # Obtain the original module object (should already be in sys.modules)
    module_name = caller_globals.get("__name__")
    original_module = sys.modules.get(module_name)

    # Use the pure transformer to produce a new executed module
    fake_module = ModuleType(module_name or "<module>")
    fake_module.__dict__["__file__"] = filename
    new_mod, new_tree = transform_module(fake_module)

    # Install transformed module into sys.modules so future imports see it
    import gc
    import weakref

    old_mod_ref = weakref.ref(original_module) if original_module is not None else None
    sys.modules[module_name] = new_mod

    # Replace caller globals: remove names that no longer exist and update others
    new_keys = set(new_mod.__dict__.keys())
    for k in list(caller_globals.keys()):
        if k.startswith("__"):
            continue
        if k not in new_keys:
            del caller_globals[k]
    for k, v in new_mod.__dict__.items():
        if k == "__file__":
            continue
        caller_globals[k] = v

    # Try to allow the old module to be garbage-collected; if it remains,
    # perform a scan to report which names are still referenced elsewhere.
    # Remove our strong local reference to the old module to avoid keeping it alive.
    del original_module
    gc.collect()

    lingering: dict[str, list[str]] = {}
    if old_mod_ref is not None and old_mod_ref() is not None:
        old_mod = old_mod_ref()
        for name, old_obj in getattr(old_mod, "__dict__", {}).items():
            if name.startswith("__"):
                continue
            new_obj = new_mod.__dict__.get(name, object())
            if old_obj is new_obj:
                continue
            refs: list[str] = []
            for m in sys.modules.values():
                try:
                    if m is None or getattr(m, "__name__", None) == module_name:
                        continue
                    if getattr(m, name, None) is old_obj:
                        refs.append(getattr(m, "__name__", str(m)))
                except Exception:
                    continue
            if refs:
                lingering[name] = refs

        if lingering:
            import warnings

            details = ", ".join(
                f"{n} (referenced in: {sorted(set(refs))})"
                for n, refs in lingering.items()
            )
            warnings.warn(
                f"ZVIC: could not fully replace some objects from module '{module_name}': {details}.\n"
                "Other modules still hold references to the original objects (e.g. via 'from module import name').\n"
                "Consider reloading those modules or restarting the interpreter for a complete replacement.",
                RuntimeWarning,
            )

    transformed_source = ast.unparse(new_tree)
    if return_lingering:
        return transformed_source, lingering
    return transformed_source


# Import hook helpers
_installed_finder = None


def install_import_hook(
    exclude_prefix: str | None = None, allow_roots: list[str] | None = None
):
    """Install ZvIC import hook into sys.meta_path. Call from tests or
    session startup to ensure all subsequent imports are transformed.
    """
    global _installed_finder
    if _installed_finder is not None:
        return
    finder = ZvicFinder(exclude_prefix=exclude_prefix, allow_roots=allow_roots)
    sys.meta_path.insert(0, finder)
    _installed_finder = finder


def uninstall_import_hook():
    global _installed_finder
    if _installed_finder is None:
        return
    with contextlib.suppress(ValueError):
        sys.meta_path.remove(_installed_finder)
    _installed_finder = None


def load_module(path: Path, module_name: str) -> ModuleType:
    original_source = path.read_text(encoding="utf-8")
    # transform and execute into a fresh module
    orig_mod = ModuleType(module_name)
    orig_mod.__dict__["__file__"] = str(path)
    mod, transformed_tree = transform_module(orig_mod)

    setattr(mod, "__original_source__", original_source)

    canonical = canonicalize(mod)
    setattr(mod, "_zvic_canonical", canonical)
    assert assumption(mod, ModuleType)
    return mod


def canonicalize(obj: Any) -> CANONICAL:
    """
    Canonicalize any object using the type normalization layer.
    For a module, returns a dict mapping names to canonicalized signatures/types.
    For a function or class, returns its canonical signature/type.
    For other objects, returns their normalized type.
    """
    if isinstance(obj, ModuleType):
        # Only include user-defined functions and classes (exclude built-ins, imports, and typing helpers)
        result: CANONICAL = {}
        for attr_name, attr in vars(obj).items():
            if attr_name == "Annotated":
                continue
            # If it's a function, represent as a dict with a single '__call__' field
            if (
                inspect.isfunction(attr)
                and getattr(attr, "__module__", None) == obj.__name__
            ):
                result[attr_name] = {"__call__": canonical_signature(attr)}
            # If it's a class, represent as its methods and __call__
            elif (
                inspect.isclass(attr)
                and getattr(attr, "__module__", None) == obj.__name__
            ):
                result[attr_name] = canonicalize(attr)
        return result
    elif inspect.isclass(obj):
        result: CANONICAL = {}
        # If the class is callable (has a custom __call__), represent it by its __call__
        call_method = obj.__dict__.get("__call__")
        if call_method and inspect.isfunction(call_method):
            result["__call__"] = canonical_signature(call_method)
        # Also include other user-defined methods (excluding __call__ and dunder methods)
        for name, member in vars(obj).items():
            if name.startswith("__") and name != "__call__":
                continue
            if name == "__call__":
                continue
            if inspect.isfunction(member):
                result[name] = canonical_signature(member)
            elif isinstance(member, staticmethod):
                result[name] = canonical_signature(member.__func__)
            elif isinstance(member, classmethod):
                result[name] = canonical_signature(member.__func__)
        return result
    elif callable(obj):
        # For any other callable (including functions), represent as a dict with a single '__call__' field
        call_method = getattr(obj, "__call__", None)
        result: CANONICAL = {}
        if call_method and inspect.ismethod(call_method):
            result["__call__"] = canonical_signature(call_method)
        elif call_method and inspect.isfunction(call_method):
            result["__call__"] = canonical_signature(call_method)
        else:
            result["__call__"] = canonical_signature(obj)
        return result
    else:
        return canonical_signature(obj)


def canonical_signature(func: Any, name: str | None = None) -> CANONICAL:
    sig = inspect.signature(func)

    def strip_typing_prefix(s: str) -> str:
        return s.replace("typing.", "") if s.startswith("typing.") else s

    positional_only: list[dict[str, Any]] = []
    positional_or_keyword: list[dict[str, Any]] = []
    keyword_only: list[dict[str, Any]] = []
    # Use runtime type hints for robust Annotated extraction
    try:
        type_hints = get_type_hints(func, include_extras=True)
    except Exception:
        type_hints = {}
    for param in sig.parameters.values():
        param_info = {}
        ann = type_hints.get(param.name, param.annotation)
        origin = get_origin(ann)
        args = get_args(ann)
        if origin is not None and origin.__name__ == "Annotated" and len(args) >= 2:
            base_type = args[0]
            if hasattr(base_type, "__name__"):
                param_info["type"] = base_type.__name__
            else:
                param_info["type"] = strip_typing_prefix(str(base_type))
            param_info["constraint"] = normalize_constraint(str(args[1]))
        elif ann != inspect.Signature.empty:
            if hasattr(ann, "__module__") and ann.__module__ == "typing":
                param_info["type"] = strip_typing_prefix(str(ann))
            elif hasattr(ann, "__name__"):
                param_info["type"] = ann.__name__
            else:
                param_info["type"] = str(ann)
        else:
            param_info["type"] = None
        if param.kind in (
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        ):
            param_info["name"] = param.name
        if param.default != inspect.Signature.empty:
            param_info["default"] = param.default
        if param.kind == inspect.Parameter.POSITIONAL_ONLY:
            positional_only.append(param_info)
        elif param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
            positional_or_keyword.append(param_info)
        elif param.kind == inspect.Parameter.KEYWORD_ONLY:
            keyword_only.append(param_info)
    # Remove 'type' field if it is None
    for plist in (positional_only, positional_or_keyword, keyword_only):
        for p in plist:
            if "type" in p and p["type"] is None:
                del p["type"]
    keyword_only = sorted(keyword_only, key=lambda p: p["name"])
    params: dict[str, list[dict[str, Any]]] = {
        "positional_only": positional_only,
        "positional_or_keyword": positional_or_keyword,
        "keyword_only": keyword_only,
    }
    # Handle return type using runtime type hints
    try:
        return_ann = type_hints.get("return", sig.return_annotation)
    except Exception:
        return_ann = sig.return_annotation
    return_info = {}
    origin = get_origin(return_ann)
    args = get_args(return_ann)
    if origin is not None and origin.__name__ == "Annotated" and len(args) >= 2:
        base_type = args[0]
        if hasattr(base_type, "__name__"):
            return_info["type"] = base_type.__name__
        else:
            return_info["type"] = strip_typing_prefix(str(base_type))
        return_info["constraint"] = normalize_constraint(str(args[1]))
    elif return_ann != inspect.Signature.empty:
        if hasattr(return_ann, "__module__") and return_ann.__module__ == "typing":
            return_info["type"] = strip_typing_prefix(str(return_ann))
        elif hasattr(return_ann, "__name__"):
            return_info["type"] = return_ann.__name__
        else:
            return_info["type"] = str(return_ann)
    else:
        return_info["type"] = None
    if return_info.get("type") == "None":
        return_info["type"] = None
    # Remove 'type' field from return if it is None
    if "type" in return_info and return_info["type"] is None:
        del return_info["type"]
    return {
        "params": params,
        "return": return_info,
    }


def pprint_recursive(obj, indent=0):
    prefix = " " * indent
    if isinstance(obj, dict):
        for k, v in obj.items():
            print(f"{prefix}{k}:")
            pprint_recursive(v, indent + 2)
    elif isinstance(obj, (list, tuple, set)):
        for v in obj:
            if isinstance(v, dict):
                print(f"{prefix}-")
                pprint_recursive(v, indent + 2)
            else:
                print(f"{prefix}- {v}")
    else:
        print(f"{prefix}{obj}")


def transform_replace(module_name: str, *, force: bool = False, dry_run: bool = False):
    # Developer tooling shim (lazy import to avoid import-time side-effects)
    from .transform_replace import replace_module

    return replace_module(module_name, force=force, dry_run=dry_run)
