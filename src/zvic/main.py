import inspect
import json
from types import FunctionType, ModuleType
from typing import Any, Dict, List, Union


def canonicalize(obj: Any, name: str = None) -> Union[Dict, List]:
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
            if inspect.isfunction(attr) or inspect.ismethod(attr):
                sig = canonical_signature(attr, attr_name)
                results[sig["name"]] = sig
    elif isinstance(obj, ModuleType):
        for attr_name, attr in inspect.getmembers(obj):
            if inspect.isfunction(attr) or inspect.isclass(attr):
                sub = canonicalize(attr, attr_name)
                results |= sub
    return results


def canonical_signature(func: FunctionType, name: str = None) -> Dict:
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


def canonicalized_to_json(obj: Any, name: str = None) -> str:
    return json.dumps(canonicalize(obj, name), indent=2)


def json_to_canonicalized(json_str: str) -> dict:
    """
    Reverse of canonicalize_to_json: takes a JSON string and returns the canonical dict.
    """
    return json.loads(json_str)


def is_compatible(a: dict, b: dict) -> bool:
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


def is_signature_compatible(a_sig: dict, b_sig: dict) -> bool:
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


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        modname = sys.argv[1]
        mod = __import__(modname)
        print(canonicalized_to_json(mod))
    else:
        print("Usage: python main.py <module_name>")
