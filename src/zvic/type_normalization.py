"""
type_normalization.py

Type Normalization Layer for ZVIC

Maps Python built-in types, NumPy dtypes, ctypes, and common custom types to JSON Schema–style dicts.
Supports extensibility for custom formats, C types, and shape metadata.

"""

import collections.abc
import types
import typing
from enum import Enum
from typing import Any, Callable

try:
    import numpy as numpy

    NP_AVAILABLE = True
except ImportError:
    NP_AVAILABLE = False

try:
    import ctypes as ctypes

    CTYPES_AVAILABLE = True
except ImportError:
    CTYPES_AVAILABLE = False

type CANONICAL_LEAF = (
    str | int | float | bool | None | list[CANONICAL_LEAF] | dict[str, CANONICAL_LEAF]
)
type CANONICAL = dict[str, CANONICAL_LEAF]


# Type aliases for clarity

TypeHandler = Callable[[Any], CANONICAL | None]


# Handler for typing.Annotated

# Handler for typing.Annotated

class TypeNormalizer:
    """Central type normalization service with handler registry"""

    def __init__(self):
        self.handlers: list[TypeHandler] = []
        self._register_core_handlers()

    def _register_core_handlers(self):
        """Register default type handlers in priority order"""
        self.register_handler(special_case_handler)  # Any, callables, etc.
        self.register_handler(annotated_type_handler)  # <--- NEW: handle Annotated
        self.register_handler(primitive_type_handler)
        self.register_handler(enum_type_handler)
        self.register_handler(numpy_type_handler)
        self.register_handler(generic_type_handler)
        self.register_handler(annotated_class_handler)
        self.register_handler(class_fallback_handler)
# Handler for typing.Annotated
def annotated_type_handler(tp: Any) -> CANONICAL | None:
    """Handle typing.Annotated types, extracting base type and constraint string."""
    import typing
    get_origin = getattr(typing, "get_origin", None)
    get_args = getattr(typing, "get_args", None)
    origin = get_origin(tp) if get_origin else getattr(tp, "__origin__", None)
    args = get_args(tp) if get_args else getattr(tp, "__args__", None)
    if origin is getattr(typing, "Annotated", None) and args and len(args) >= 2:
        base_type = args[0]
        constraint = args[1]
        base_schema = normalize_type(base_type)
        # Add constraint string to the schema
        if isinstance(base_schema, dict):
            base_schema = dict(base_schema)  # copy
            base_schema["constraint"] = constraint
            return base_schema
    return None

    def register_handler(self, handler: TypeHandler):
        """Add custom type handler to processing pipeline"""
        self.handlers.append(handler)
        return self  # Enable fluent interface

    def normalize(self, tp: Any) -> CANONICAL:
        """Main normalization entry point"""
        for handler in self.handlers:
            if result := handler(tp):
                return result
        return {"type": "object", "class": str(type(tp))}


# ---------------------------
# Core Type Handlers
# ---------------------------


def primitive_type_handler(tp: Any) -> CANONICAL | None:
    """Handle built-in types and registered custom types"""
    PRIMITIVE_MAP: dict[str, CANONICAL_LEAF] = {
        "int": {"type": "integer"},
        "float": {"type": "number"},
        "str": {"type": "string"},
        "bool": {"type": "boolean"},
        "list": {"type": "array"},
        "dict": {"type": "object"},
        "none": {"type": "null"},
        "any": {"type": "any"},
    }
    if CTYPES_AVAILABLE:
        PRIMITIVE_MAP["ctypes.c_uint32"] = {"type": "integer", "format": "uint32_t"}
    if NP_AVAILABLE:
        PRIMITIVE_MAP["numpy.int32"] = {"type": "integer", "format": "int32"}
        PRIMITIVE_MAP["numpy.int64"] = {"type": "integer", "format": "int64"}
        PRIMITIVE_MAP["numpy.float32"] = {"type": "number", "format": "float32"}
        PRIMITIVE_MAP["numpy.float64"] = {"type": "number", "format": "double"}

    # Helper to get string key for type using dict lookup for builtins
    _builtin_type_map = {
        int: "int",
        float: "float",
        str: "str",
        bool: "bool",
        list: "list",
        dict: "dict",
        type(None): "none",
        typing.Any: "any",
    }
    key = _builtin_type_map.get(tp)
    if key is None:
        if hasattr(tp, "__module__") and hasattr(tp, "__name__"):
            key = f"{tp.__module__}.{tp.__name__}"
        else:
            key = str(tp)
    if key in PRIMITIVE_MAP:
        val = PRIMITIVE_MAP[key]
        if isinstance(val, dict):
            return val  # already CANONICAL
        return {"type": type(val).__name__, "value": val}

    # Allow runtime registrations
    if tp in CUSTOM_TYPE_REGISTRY:
        return CUSTOM_TYPE_REGISTRY[tp]
    return None


def enum_type_handler(tp: Any) -> CANONICAL | None:
    """Handle Enum types with proper value extraction"""
    if isinstance(tp, type) and issubclass(tp, Enum):
        return {
            "type": "object",
            "class": tp.__name__,
            "properties": {e.name: {"const": e.value} for e in tp},
        }
    if isinstance(tp, Enum):
        return {"type": "enum_value", "class": type(tp).__name__, "value": tp.value}
    return None


def generic_type_handler(tp: Any) -> CANONICAL | None:
    """Handle modern generics and type annotations"""
    # Use typing.get_origin/get_args for generic introspection (Python 3.8+)
    get_origin = getattr(typing, "get_origin", None)
    get_args = getattr(typing, "get_args", None)
    origin = get_origin(tp) if get_origin else getattr(tp, "__origin__", None)
    args = get_args(tp) if get_args else getattr(tp, "__args__", None)

    # Handle Optional and Union
    if origin is typing.Union:
        union_args = args or []
        types = [normalize_type(a) for a in union_args]
        type_names = [t.get("type", str(t)) for t in types]
        if len(types) == 2 and any(tn == "null" for tn in type_names):
            non_null = [t for t in types if t.get("type") != "null"]
            return {"type": [non_null[0]["type"], "null"]}
        return {"type": [t.get("type", str(t)) for t in types]}

    # Sequence detection (ABC/protocol approach)
    if (
        origin
        and isinstance(origin, type)
        and issubclass(origin, collections.abc.Sequence)
        and not issubclass(origin, (str, bytes))
    ):
        if args:
            return {"type": "sequence", "items": normalize_type(args[0])}
        else:
            return {"type": "sequence"}

    # Mapping detection (ABC/protocol approach)
    if (
        origin
        and isinstance(origin, type)
        and issubclass(origin, collections.abc.Mapping)
    ):
        if not args or len(args) != 2:
            return {"type": "mapping"}

        key_type = normalize_type(args[0])
        value_type = normalize_type(args[1])
        if key_type.get("type") == "string":
            return {"type": "mapping", "additionalProperties": value_type}
        return {"type": "mapping", "additionalProperties": value_type}
    return None


def annotated_class_handler(tp: Any) -> CANONICAL | None:
    """Handle classes with type annotations (dataclasses, Pydantic, etc.)"""
    # Accept both classes and instances
    cls = tp if isinstance(tp, type) else type(tp)
    # ABC/protocol support
    if isinstance(cls, type):
        if issubclass(cls, collections.abc.Sequence) and not issubclass(
            cls, (str, bytes)
        ):
            return {"type": "sequence"}
        if issubclass(cls, collections.abc.Mapping):
            return {"type": "mapping"}
        if hasattr(cls, "__annotations__") and cls.__annotations__:
            return {
                "type": "object",
                "class": getattr(cls, "__name__", str(cls)),
                "properties": {
                    k: normalize_type(v) for k, v in cls.__annotations__.items()
                },
            }
    return None


def numpy_type_handler(tp: Any) -> CANONICAL | None:
    """Handle NumPy-specific types"""
    if hasattr(tp, "__module__") and tp.__module__.startswith("numpy"):
        np_name = getattr(tp, "__name__", str(tp))
        if "int" in np_name:
            return {"type": "integer", "format": np_name}
        if "float" in np_name:
            return {"type": "number", "format": np_name}
        return {"type": "array", "format": np_name}
    return None


def special_case_handler(tp: Any) -> CANONICAL | None:
    """Handle edge cases and special types"""
    if tp is typing.Any:
        return {"type": "any"}

    # Handle callables and functions, but not classes
    if isinstance(
        tp,
        (
            types.FunctionType,
            types.MethodType,
            types.BuiltinFunctionType,
            types.BuiltinMethodType,
        ),
    ):
        return {"type": "callable", "name": getattr(tp, "__name__", "anonymous")}

    return {"type": "unknown_special_case", "python_type": str(tp)}


def class_fallback_handler(tp: Any) -> CANONICAL | None:
    """Final fallback for class-based types"""
    if isinstance(tp, type) or hasattr(tp, "__class__"):
        cls = tp if isinstance(tp, type) else type(tp)
        # If the class has no __annotations__, fallback to string
        if not getattr(cls, "__annotations__", None):
            return {"type": "string", "class": getattr(cls, "__name__", str(cls))}
        if cls.__module__ not in ("builtins", "typing"):
            return {
                "type": "object",
                "class": getattr(cls, "__name__", str(cls)),
                "module": cls.__module__,
            }
    return None


# ---------------------------
# Global Registry & Interface
# ---------------------------

CUSTOM_TYPE_REGISTRY: dict[type, CANONICAL] = {}


def register_type(py_type: type, schema: CANONICAL) -> None:
    """Register custom type mapping"""
    CUSTOM_TYPE_REGISTRY[py_type] = schema


# Create default normalizer instance
_default_normalizer = TypeNormalizer()


def normalize_type(tp: Any) -> CANONICAL:
    """Public interface for type normalization"""
    return _default_normalizer.normalize(tp)


# ---------------------------
# Run doctest if executed as a script
# ---------------------------

if __name__ == "__main__":
    import doctest

    doctest.testmod()
