import inspect
import json
from types import ModuleType
from typing import Any


def canonicalize(obj: Any, name: str | None = None) -> dict[str, Any]:
    """
    Recursively canonicalize all functions, classes, and modules in the given object.
    Returns a JSON-serializable structure of canonicalized signatures.
    """
    results = {}
    if inspect.isfunction(obj) or inspect.ismethod(obj):
        sig = canonical_signature(obj, name)
        results[sig["name"]] = sig
    elif inspect.isclass(obj):
        for attr_name, attr in inspect.getmembers(obj):
            # Handle staticmethod and classmethod
            if isinstance(getattr(obj, attr_name, None), staticmethod):
                # staticmethod: extract the underlying function
                func = getattr(obj, attr_name).__func__
                sig = canonical_signature(func, attr_name)
                sig["method_type"] = "staticmethod"
                results[sig["name"]] = sig
            elif isinstance(getattr(obj, attr_name, None), classmethod):
                # classmethod: extract the underlying function
                func = getattr(obj, attr_name).__func__
                sig = canonical_signature(func, attr_name)
                sig["method_type"] = "classmethod"
                results[sig["name"]] = sig
            elif inspect.isfunction(attr) or inspect.ismethod(attr):
                # instance method
                sig = canonical_signature(attr, attr_name)
                sig["method_type"] = "instancemethod"
                results[sig["name"]] = sig
            # Add class-level attributes (skip methods and built-ins)
            elif not attr_name.startswith("__") and not inspect.isroutine(attr):
                # Record attribute name and type (or value if simple)
                try:
                    attr_type = type(attr).__name__
                    # Try to serialize value if it's a simple type
                    if isinstance(attr, (int, float, str, bool, type(None))):
                        results[attr_name] = {
                            "attribute_type": attr_type,
                            "value": attr,
                        }
                    else:
                        results[attr_name] = {"attribute_type": attr_type}
                except Exception:
                    results[attr_name] = {"attribute_type": "unknown"}
    elif isinstance(obj, ModuleType):
        for attr_name, attr in inspect.getmembers(obj):
            if inspect.isfunction(attr) or inspect.isclass(attr):
                sub = canonicalize(attr, attr_name)
                results |= sub
    return results

def canonicalize(obj: Any, name: str | None = None) -> dict[str, Any]:
    """
    Canonicalize functions, classes, enums, dataclasses, pydantic models, and modules.
    Uses match/case for type dispatch (Python 3.10+).
    """
    import dataclasses
    import enum
    contract: dict[str, Any] = {}
    match obj:
        case _ if inspect.isclass(obj) and hasattr(obj, "__mro__") and any(base.__name__ == "Enum" for base in obj.__mro__):
            contract[obj.__name__] = canonicalize_enum(obj)
        case _ if dataclasses.is_dataclass(obj):
            contract[obj.__name__] = canonicalize_dataclass(obj)
        case _ if is_pydantic_model(obj):
            contract[obj.__name__] = canonicalize_pydantic_model(obj)
        case _ if inspect.isfunction(obj) or inspect.ismethod(obj):
            sig = canonical_signature(obj, name)
            contract[sig["name"]] = sig
        case _ if inspect.isclass(obj):
            for attr_name, attr in inspect.getmembers(obj):
                if isinstance(attr, (classmethod, staticmethod)):
                    attr = attr.__func__
                if callable(attr) and not inspect.isclass(attr):
                    sig = canonical_signature(attr, attr_name)
                    contract[sig["name"]] = sig
        case _ if isinstance(obj, ModuleType):
            for attr_name, attr in inspect.getmembers(obj):
                if inspect.isclass(attr) and (
                    any(base.__name__ == "Enum" for base in getattr(attr, "__mro__", []))
                    or dataclasses.is_dataclass(attr)
                    or is_pydantic_model(attr)
                ):
                    contract[attr_name] = canonicalize(attr, attr_name)
                elif inspect.isfunction(attr) or inspect.isclass(attr):
                    contract.update(canonicalize(attr, attr_name))
    return contract

def canonicalize_enum(obj: Any) -> dict:
    # TODO: Implement enum canonicalization
    return {"name": obj.__name__, "type": "enum", "members": [e.name for e in obj]}

def canonicalize_dataclass(dc: type) -> dict:
    import dataclasses
    # TODO: Implement dataclass canonicalization
    return {"name": dc.__name__, "type": "dataclass", "fields": [f.name for f in dataclasses.fields(dc)]}

def is_pydantic_model(obj: Any) -> bool:
    try:
        from pydantic import BaseModel
        return isinstance(obj, type) and issubclass(obj, BaseModel)
    except ImportError:
        return False

def canonicalize_pydantic_model(model: type) -> dict:
    # TODO: Implement pydantic model canonicalization
    return {"name": model.__name__, "type": "pydantic_model", "fields": list(getattr(model, "__fields__", {}).keys())}


def canonical_signature(func: Any, name: str | None = None) -> dict:
    sig = inspect.signature(func)
    params = []
    for param in sig.parameters.values():
        param_info = {
            "kind": param.kind.name,
            "type": str(param.annotation)
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
        str(sig.return_annotation) if sig.return_annotation != inspect._empty else None
    )
    return {
        "name": name or func.__name__,
        "params": params,
        "return": return_type,
    }


def canonicalized_to_json(obj: Any, name: str | None = None) -> str:
    return json.dumps(canonicalize(obj, name), indent=2)


def json_to_canonicalized(json_str: str) -> dict[str, Any]:
    """
    Reverse of canonicalize_to_json: takes a JSON string and returns the canonical dict.
    """
    return json.loads(json_str)


def is_compatible(a: dict[str, Any], b: dict[str, Any]) -> bool:
    """
    Returns True if b is forward compatible with a (i.e., b can safely replace a).
    For every function/class in a, b must have a compatible counterpart.
    This is order-sensitive: a is the current/old implementation, b is the candidate/new one.
    """
    for name, a_sig in a.items():
        b_sig = b.get(name)
        if not b_sig:
            return False
        if not is_signature_compatible(a_sig, b_sig):
            return False
    return True


def is_signature_compatible(a_sig: dict[str, Any], b_sig: dict[str, Any]) -> bool:
    """
    Returns True if b_sig is compatible with a_sig (forwards compatible).
    Checks name, params (names, kinds, types, defaults), and return type.
    """
    if a_sig.get("name") != b_sig.get("name"):
        return False
    a_params = a_sig.get("params", [])
    b_params = b_sig.get("params", [])
    if len(a_params) > len(b_params):
        return False
    for i, a_param in enumerate(a_params):
        b_param = b_params[i]
        if a_param.get("name") != b_param.get("name"):
            return False
        if a_param.get("kind") != b_param.get("kind"):
            return False
        if a_param.get("type") != b_param.get("type"):
            return False
        # If a has a default, b must have the same default or a new one
        if "default" in a_param:
            if "default" in b_param and a_param["default"] == b_param["default"]:
                continue
            # b can add a default, but cannot remove one
            if "default" not in b_param:
                return False
    # b can have extra params with defaults
    a_return = a_sig.get("return")
    b_return = b_sig.get("return")
    return a_return == b_return
