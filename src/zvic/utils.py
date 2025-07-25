# type: ignore
"""Utility functions and universal placeholder for ZVIC."""

import ast
import contextlib
import sys
from collections import namedtuple
from dataclasses import dataclass
from inspect import Parameter, Signature
from typing import Any


def assumption(obj: Any, expected: type) -> bool:
    """
    Check if obj is an instance of expected type or any type in a union.
    Usage:
        assert assumption(a, int)
        assert assumption(b, str | float)
    """
    types = (
        expected.__args__
        if hasattr(expected, "__origin__")
        and expected.__origin__ is type(None).__class__
        else None
    )
    if types is None and hasattr(expected, "__args__"):
        types = expected.__args__
    if types is None:
        types = (expected,)
    for exp in types:
        if isinstance(obj, exp):
            return True
    msg = (
        f"Expected {expected}, instead got {type(obj).__name__} (value: {obj})"
        if len(types) == 1
        else f"Expected one of {types}, instead got {type(obj).__name__} (value: {obj})"
    )
    raise AssertionError(msg)


def normalize_constraint(expr: str) -> str:
    """
    Normalize a constraint string by parsing and unparsing it via AST.
    This ensures a canonical form for expressions like '_ < 10'.
    """
    return ast.unparse(ast.parse(expr, mode="eval"))


# Universal placeholder that supports all operations and comparisons
class _:
    def __getattr__(self, name):
        return self

    def __setattr__(self, name, value):
        pass  # intentionally does nothing

    def __call__(self, *a, **k):
        return self

    def __getitem__(self, k):
        return self

    def __setitem__(self, k, v):
        pass  # intentionally does nothing

    def __delitem__(self, k):
        pass  # intentionally does nothing

    def __contains__(self, item):
        return True

    def __iter__(self):
        return iter([])

    def __next__(self):
        raise StopIteration

    def __reversed__(self):
        return iter([])

    def __bool__(self):
        return True

    def __len__(self):
        return 0

    def __eq__(self, o):
        return True

    def __ne__(self, o):
        return False

    def __lt__(self, o):
        return True

    def __le__(self, o):
        return True

    def __gt__(self, o):
        return True

    def __ge__(self, o):
        return True

    def __add__(self, o):
        return self

    def __sub__(self, o):
        return self

    def __mul__(self, o):
        return self

    def __matmul__(self, o):
        return self

    def __truediv__(self, o):
        return self

    def __floordiv__(self, o):
        return self

    def __mod__(self, o):
        return self

    def __divmod__(self, o):
        return (self, self)

    def __pow__(self, o, m=None):
        return self

    def __lshift__(self, o):
        return self

    def __rshift__(self, o):
        return self

    def __and__(self, o):
        return self

    def __xor__(self, o):
        return self

    def __or__(self, o):
        return self

    def __neg__(self):
        return self

    def __pos__(self):
        return self

    def __abs__(self):
        return self

    def __invert__(self):
        return self

    def __complex__(self):
        return 0j

    def __int__(self):
        return 0

    def __float__(self):
        return 0.0

    def __index__(self):
        return 0

    def __round__(self, n=None):
        return 0

    def __trunc__(self):
        return 0

    def __floor__(self):
        return 0

    def __ceil__(self):
        return 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def __await__(self):
        yield self

    def __aiter__(self):
        return self

    def __anext__(self):
        raise StopAsyncIteration

    def __hash__(self):
        return 0

    def __str__(self):
        return "_"

    def __repr__(self):
        return "_"


_ = _()


Params = namedtuple(
    "Params",
    [
        "posonly",
        "pos_or_kw",
        "kwonly",
        "posonly_required",
        "pos_or_kw_required",
        "kwonly_required",
        "p_min",
        "p_max",
        "pk_min",
        "pk_max",
        "k_min",
        "k_max",
    ],
)


@dataclass(frozen=True)
class Scenario:
    a_posonly_required: int
    a_posonly: int
    a_pos_or_kw_required: int
    a_pos_or_kw: int
    a_kwonly_required: int
    a_kwonly: int
    b_posonly_required: int
    b_posonly: int
    b_pos_or_kw_required: int
    b_pos_or_kw: int
    b_kwonly_required: int
    b_kwonly: int
    b_has_varargs: bool
    b_has_varkw: bool


def prepare_scenario(
    a: Params, a_sig: Signature, b: Params, b_sig: Signature
) -> Scenario:
    """
    Accepts Params and Signature objects for a and b, uses Signature for varargs/varkw detection.
    Returns Scenario for matching.
    """
    return Scenario(
        a_posonly_required=len(a.posonly_required),
        a_posonly=len(a.posonly),
        a_pos_or_kw_required=len(a.pos_or_kw_required),
        a_pos_or_kw=len(a.pos_or_kw),
        a_kwonly_required=len(a.kwonly_required),
        a_kwonly=len(a.kwonly),
        b_posonly_required=len(b.posonly_required),
        b_posonly=len(b.posonly),
        b_pos_or_kw_required=len(b.pos_or_kw_required),
        b_pos_or_kw=len(b.pos_or_kw),
        b_kwonly_required=len(b.kwonly_required),
        b_kwonly=len(b.kwonly),
        b_has_varargs=has_varargs(b_sig),
        b_has_varkw=has_varkw(b_sig),
    )


def prepare_params(sig: Signature) -> Params:
    params = [
        {
            "name": p.name,
            "kind": p.kind.name,
            "type": p.annotation,  # Store the actual annotation object
            "type_name": get_type_name(
                p.annotation
            ),  # Optionally keep the name for debugging
            "default": get_default(p.default),
        }
        for p in sig.parameters.values()
    ]
    posonly = [p for p in params if p["kind"] == "POSITIONAL_ONLY"]
    pos_or_kw = [p for p in params if p["kind"] == "POSITIONAL_OR_KEYWORD"]
    kwonly = [p for p in params if p["kind"] == "KEYWORD_ONLY"]
    posonly_required = [p for p in posonly if is_required(p)]
    pos_or_kw_required = [p for p in pos_or_kw if is_required(p)]
    kwonly_required = [p for p in kwonly if is_required(p)]
    p_min = len(posonly_required)
    p_max = len(posonly)
    pk_min = len(pos_or_kw_required)
    pk_max = len(pos_or_kw)
    k_min = len(kwonly_required)
    k_max = len(kwonly)
    return Params(
        posonly,
        pos_or_kw,
        kwonly,
        posonly_required,
        pos_or_kw_required,
        kwonly_required,
        p_min,
        p_max,
        pk_min,
        pk_max,
        k_min,
        k_max,
    )


def get_class_str(d: Any) -> str | None:
    if isinstance(d, dict) and "class" in d:
        val: Any = d["class"]
        if val is not None:
            return val if isinstance(val, str) else str(val)
    return d if isinstance(d, str) else None


def is_supertype(sup: Any, sub: Any) -> bool:
    if is_any_or_missing(sub) or is_any_or_missing(sup):
        return True
    if sup == sub:
        return True
    sup_cls: str | None = get_class_str(sup)
    sub_cls: str | None = get_class_str(sub)
    if sup_cls is not None and sub_cls is not None:
        with contextlib.suppress(Exception):
            sup_type: Any = eval(sup_cls)
            sub_type: Any = eval(sub_cls)
            return issubclass(sub_type, sup_type)
    return False


def is_subtype(sub: Any, sup: Any) -> bool:
    if is_any_or_missing(sub) or is_any_or_missing(sup):
        return True
    if sub == sup:
        return True
    sub_cls: str | None = get_class_str(sub)
    sup_cls: str | None = get_class_str(sup)
    if sub_cls is not None and sup_cls is not None:
        with contextlib.suppress(Exception):
            sub_type: Any = eval(sub_cls)
            sup_type: Any = eval(sup_cls)
            return issubclass(sub_type, sup_type)
    return False


def is_required(p: dict[str, Any]) -> bool:
    return (p.get("default") is None or p.get("default") == Parameter.empty) and p.get(
        "kind"
    ) not in ("VAR_POSITIONAL", "VAR_KEYWORD")


def debug_print(*args, **kwargs):
    print(*args, **kwargs, file=sys.stdout)


def get_type_name(annotation: Any) -> str | None:
    if annotation is Signature.empty:
        return None
    if isinstance(annotation, str):
        return annotation
    return getattr(annotation, "__name__", str(annotation) if annotation else None)


def get_default(default: Any) -> Any:
    return None if default is Signature.empty else default


def has_varargs(sig: Signature) -> bool:
    return any(p.kind == Parameter.VAR_POSITIONAL for p in sig.parameters.values())


def has_varkw(sig: Signature) -> bool:
    return any(p.kind == Parameter.VAR_KEYWORD for p in sig.parameters.values())


def count_required(params: list[dict[str, Any]]) -> int:
    return sum(
        (p.get("default") is None or p.get("default") == Parameter.empty)
        and p.get("kind")
        in ("POSITIONAL_ONLY", "POSITIONAL_OR_KEYWORD", "KEYWORD_ONLY")
        for p in params
    )


def count_total(params: list[dict[str, Any]]) -> int:
    return sum(
        (p.get("kind") in ("POSITIONAL_ONLY", "POSITIONAL_OR_KEYWORD", "KEYWORD_ONLY"))
        for p in params
    )


def is_any_or_missing(t: Any) -> bool:
    return (
        t is None
        or t == {"type": "any"}
        or t == {"type": "object"}
        or t == {}
        or t == "any"
    )
