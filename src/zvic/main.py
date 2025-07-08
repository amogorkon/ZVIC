import contextlib
import dataclasses
import importlib.util
import inspect
import json
import types

# Recursive type for canonicalized structures
from typing import Any

from zvic.type_normalization import CANONICAL, normalize_type

PYDANTIC_AVAILABLE = importlib.util.find_spec("pydantic") is not None


def canonicalize(obj: Any) -> CANONICAL:
    """
    Canonicalize any object using the type normalization layer.
    """

    if isinstance(obj, types.ModuleType):
        return {
            attr_name: canonicalize(attr)
            for attr_name, attr in vars(obj).items()
            if inspect.isclass(attr) or inspect.isfunction(attr)
        }
    else:
        return normalize_type(obj)


def canonicalize_enum(obj: Any) -> CANONICAL:
    # Canonicalize enum using type normalization for values
    return {
        "name": obj.__name__,
        "type": "enum",
        "members": [e.name for e in obj],
        "values": [normalize_type(e.value) for e in obj],
    }


def canonicalize_dataclass(dc: type) -> CANONICAL:
    return {
        "name": dc.__name__,
        "type": "dataclass",
        "fields": {f.name: normalize_type(f.type) for f in dataclasses.fields(dc)},
    }


def is_pydantic_model(obj: Any) -> bool:
    if not PYDANTIC_AVAILABLE:
        return False
    import importlib

    pydantic = importlib.import_module("pydantic")
    BaseModel = getattr(pydantic, "BaseModel", None)
    if BaseModel is None:
        return False
    return isinstance(obj, type) and issubclass(obj, BaseModel)


def canonicalize_pydantic_model(model: type) -> CANONICAL:
    # Canonicalize pydantic model using type normalization for fields
    try:
        fields = model.__annotations__
    except AttributeError:
        fields = {}
    return {
        "name": model.__name__,
        "type": "pydantic_model",
        "fields": {k: normalize_type(v) for k, v in fields.items()},
    }


def canonical_signature(func: Any, name: str | None = None) -> CANONICAL:
    sig = inspect.signature(func)
    params = []
    for param in sig.parameters.values():
        param_info = {
            "kind": param.kind.name,
            "type": normalize_type(param.annotation)
            if param.annotation != inspect._empty
            else None,
        }
        if param.kind in (
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        ):
            param_info["name"] = param.name
        if param.default != inspect._empty:
            param_info["default"] = repr(param.default)
        params.append(param_info)
    return_type = (
        normalize_type(sig.return_annotation)
        if sig.return_annotation != inspect._empty
        else None
    )
    return {
        "name": name or func.__name__,
        "params": params,
        "return": return_type,
    }


def canonicalized_to_json(obj: Any) -> str:
    return json.dumps(canonicalize(obj), indent=2)


def json_to_canonicalized(json_str: str) -> CANONICAL:
    """
    Reverse of canonicalize_to_json: takes a JSON string and returns the canonical dict.
    """
    return json.loads(json_str)


def is_compatible(
    a: object,
    b: object,
) -> bool:
    """
    Returns True if b is forward compatible with a (i.e., b can safely replace a).
    Accepts functions, classes, or canonicalized dicts. If given functions, compares their canonical signatures.
    If given dicts with multiple entries (e.g., module/class dicts), checks all entries.
    """
    # If both are functions or methods, compare their canonical signatures
    import inspect

    if (inspect.isfunction(a) or inspect.ismethod(a)) and (
        inspect.isfunction(b) or inspect.ismethod(b)
    ):
        a_sig = canonical_signature(a)
        b_sig = canonical_signature(b)
        return is_signature_compatible(a_sig, b_sig)

    # If both are dicts, treat as canonicalized module/class dicts
    if isinstance(a, dict) and isinstance(b, dict):
        # If these are canonical signatures (have 'name', 'params', 'return'), compare directly
        if {"name", "params", "return"}.issubset(a.keys()) and {
            "name",
            "params",
            "return",
        }.issubset(b.keys()):
            return is_signature_compatible(a, b)
        # Otherwise, treat as mapping of names to signatures
        for name, a_sig in a.items():
            b_sig = b.get(name)
            if not b_sig:
                return False
            if not is_signature_compatible(a_sig, b_sig):
                return False
        return True

    # Otherwise, canonicalize and recurse
    return is_compatible(canonicalize(a), canonicalize(b))


def is_signature_compatible(
    a_sig: dict[str, Any],
    b_sig: dict[str, Any],
) -> bool:
    """
    Returns True if b_sig is compatible with a_sig (forwards compatible).
    Checks name, params (names, kinds, types, defaults), and return type.
    """

    a_params = a_sig.get("params", [])
    b_params = b_sig.get("params", [])

    def is_any_or_missing(t):
        return (
            t is None
            or t == {"type": "any"}
            or t == {"type": "object"}
            or t == {}
            or t == "any"
        )

    def is_subtype(sub, sup):
        # Covariant: b_return (sub) must be subtype of a_return (sup)
        if is_any_or_missing(sub) or is_any_or_missing(sup):
            return True  # Any/missing matches anything in either direction
        if sub == sup:
            return True
        sub_cls = sub.get("class") if isinstance(sub, dict) else None
        sup_cls = sup.get("class") if isinstance(sup, dict) else None
        if sub_cls and sup_cls:
            with contextlib.suppress(Exception):
                sub_type = eval(sub_cls)
                sup_type = eval(sup_cls)
                return issubclass(sub_type, sup_type)
        return False

    def is_supertype(sup, sub):
        # Contravariant: b_param (sup) must be supertype of a_param (sub)
        if is_any_or_missing(sub) or is_any_or_missing(sup):
            return True  # Any/missing matches anything in either direction
        if sup == sub:
            return True
        sup_cls = sup.get("class") if isinstance(sup, dict) else None
        sub_cls = sub.get("class") if isinstance(sub, dict) else None
        if sup_cls and sub_cls:
            with contextlib.suppress(Exception):
                sup_type = eval(sup_cls)
                sub_type = eval(sub_cls)
                return issubclass(sub_type, sup_type)
        return False

    # Split params by kind
    def split_params(params):
        posonly = []
        pos_or_kw = []
        kwonly = []
        for p in params:
            kind = p.get("kind")
            if kind == "POSITIONAL_ONLY":
                posonly.append(p)
            elif kind == "POSITIONAL_OR_KEYWORD":
                pos_or_kw.append(p)
            elif kind == "KEYWORD_ONLY":
                kwonly.append(p)
        return posonly, pos_or_kw, kwonly

    a_posonly, a_pos_or_kw, a_kwonly = split_params(a_params)
    b_posonly, b_pos_or_kw, b_kwonly = split_params(b_params)

    # Helper: is required (no default)
    def is_required(p):
        return "default" not in p

    # 1. Positional-only: match by type and order, ignore names
    # All a's positional-only must be present in b, in order and type
    if len(a_posonly) != len(b_posonly):
        return False
    for i in range(len(a_posonly)):
        a_p = a_posonly[i]
        b_p = b_posonly[i]
        if a_p.get("kind") != b_p.get("kind"):
            return False
        # Contravariant: b's param type must be a supertype of a's
        if not is_supertype(b_p.get("type"), a_p.get("type")):
            return False
        # If a requires, b must require (cannot add required param in b)
        if is_required(a_p) and not is_required(b_p):
            continue  # b can be more permissive
        if not is_required(a_p) and is_required(b_p):
            return False

    # If b has fewer positional-only than a, but more positional-or-keyword, allow matching if types/kinds align
    # (for normal vs posonly/kwonly)
    if len(a_posonly) < len(b_posonly):
        # Already handled above (extra b_posonly must be defaulted)
        pass
    elif len(a_posonly) > len(b_posonly):
        # Try to match a's extra posonly to b's pos_or_kw
        needed = len(a_posonly) - len(b_posonly)
        if needed > len(b_pos_or_kw):
            return False
        for i in range(needed):
            a_p = a_posonly[len(b_posonly) + i]
            b_p = b_pos_or_kw[i]
            if b_p.get("kind") != "POSITIONAL_OR_KEYWORD":
                return False
            if not is_supertype(b_p.get("type"), a_p.get("type")):
                return False
            if is_required(a_p) and not is_required(b_p):
                continue
            if not is_required(a_p) and is_required(b_p):
                return False
        # Remove matched b_pos_or_kw
        b_pos_or_kw = b_pos_or_kw[needed:]
        a_posonly = a_posonly[: len(b_posonly)]

    # 2. Positional-or-keyword: match by name if possible, else by position
    if len(a_pos_or_kw) > len(b_pos_or_kw):
        return False
    used_b_indices = set()
    for i, a_p in enumerate(a_pos_or_kw):
        # Try to match by name first
        b_idx = next(
            (
                j
                for j, p in enumerate(b_pos_or_kw)
                if p["name"] == a_p["name"] and j not in used_b_indices
            ),
            None,
        )
        if b_idx is None:
            # Fallback: match by position if available
            if i < len(b_pos_or_kw) and i not in used_b_indices:
                b_idx = i
            else:
                return False
        b_p = b_pos_or_kw[b_idx]
        used_b_indices.add(b_idx)
        if b_p.get("kind") not in ("POSITIONAL_OR_KEYWORD", "KEYWORD_ONLY"):
            return False
        # Contravariant: b's param type must be a supertype of a's
        if not is_supertype(b_p.get("type"), a_p.get("type")):
            return False
        # If a requires, b must require (cannot add required param in b)
        if is_required(a_p) and not is_required(b_p):
            continue  # b can be more permissive
        if not is_required(a_p) and is_required(b_p):
            return False
    # b can have extra positional-or-keyword, but only if they are defaulted
    for j, b_p in enumerate(b_pos_or_kw):
        if j not in used_b_indices and is_required(b_p):
            return False

    # 3. Keyword-only: match by name, kind, and type (order does not matter)
    a_kw_map = {p["name"]: p for p in a_kwonly}
    b_kw_map = {p["name"]: p for p in b_kwonly}
    for name, a_p in a_kw_map.items():
        b_p = b_kw_map.get(name)
        if not b_p:
            # Try to match a's kwonly to b's pos_or_kw
            b_p = next((p for p in b_pos_or_kw if p["name"] == name), None)
            if not b_p:
                return False
        if b_p.get("kind") not in ("KEYWORD_ONLY", "POSITIONAL_OR_KEYWORD"):
            return False
        # Contravariant: b's param type must be a supertype of a's
        if not is_supertype(b_p.get("type"), a_p.get("type")):
            return False
        # If a requires, b must require (cannot add required param in b)
        if is_required(a_p) and not is_required(b_p):
            continue  # b can be more permissive
        if not is_required(a_p) and is_required(b_p):
            return False
    # b can have extra keyword-only, but only if they are defaulted
    for name, b_p in b_kw_map.items():
        if name not in a_kw_map and is_required(b_p):
            return False

    # Return type: covariant (b_return type must be subtype of a_return type)
    a_return = a_sig.get("return")
    b_return = b_sig.get("return")
    return bool(is_subtype(b_return, a_return))
