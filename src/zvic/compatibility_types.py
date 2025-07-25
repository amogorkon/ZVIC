"""compatibility.types.py

Everything we need to check for compatibility between types of a single parameter or return value.
"""

import contextlib
from typing import Any

from .exception import SignatureIncompatible


def is_any_or_missing(t: Any) -> bool:
    import inspect

    return (
        t is None
        or t == {"type": "any"}
        or t == {"type": "object"}
        or t == {}
        or t == "any"
        or t == inspect._empty
    )


def get_class_str(d: Any) -> str | None:
    if isinstance(d, dict) and "class" in d:
        val: Any = d["class"]
        if val is not None:
            return val if isinstance(val, str) else str(val)
    return d if isinstance(d, str) else None


def is_subtype(sub: Any, sup: Any) -> bool:
    if is_any_or_missing(sub) or is_any_or_missing(sup):
        return True
    if sub == sup:
        return True
    # Accept class objects directly
    if isinstance(sub, type) and isinstance(sup, type):
        return issubclass(sub, sup)
    # Fallback: resolve strings via globals
    sub_cls: str | None = get_class_str(sub)
    sup_cls: str | None = get_class_str(sup)
    if sub_cls is not None and sup_cls is not None:
        with contextlib.suppress(Exception):
            sub_type: Any = globals().get(sub_cls)
            sup_type: Any = globals().get(sup_cls)
            if isinstance(sub_type, type) and isinstance(sup_type, type):
                return issubclass(sub_type, sup_type)
    return False


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


def is_type_compatible(a, b) -> bool:
    # T8: Adjacent types | A: uint8 → B: uint16 | ✗ | Behavioral differences matter
    # If both are types, not primitive, not subtypes, and not equal, fail
    if (
        isinstance(a, type)
        and isinstance(b, type)
        and a != b
        and not issubclass(b, a)
        and not issubclass(a, b)
        and a.__name__.startswith("uint")
        and b.__name__.startswith("uint")
    ):
        raise SignatureIncompatible(
            message="T8: Adjacent types (e.g., uint8 vs uint16) are not compatible.",
            context={"A_type": a, "B_type": b},
            suggestion="Use explicit conversion or match types exactly.",
        )
    # T6: Implicit conversion | A: int → B: float | ✗ | No explicit subtype relationship
    primitive_types = {int, float, str, bool}
    if (
        isinstance(a, type)
        and isinstance(b, type)
        and a in primitive_types
        and b in primitive_types
        and a != b
        and not issubclass(b, a)
        and not issubclass(a, b)
    ):
        raise SignatureIncompatible(
            message="T6: Implicit conversion between primitive types is not allowed.",
            context={"A_type": a, "B_type": b},
            suggestion="Use explicit conversion or ensure types match exactly.",
        )
    # T0: Untyped/Any → Specific type | A: Any → B: int | ✗ | Type constraint added
    if is_any_or_missing(a) and not is_any_or_missing(b):
        raise SignatureIncompatible(
            message="T0: Untyped/Any parameter cannot be narrowed to a specific type without breaking compatibility.",
            context={"A_type": a, "B_type": b},
            suggestion="Start with a narrow type and explicitely go from there as baseline. There is nothing we can do from here.",
        )
    if is_any_or_missing(b):
        return True
    # | T1 | Same type | A: int → B: int | ✓ | Exact match
    if a == b:
        return True
    # | T2 | Base → Derived (narrowing) | A: Animal → B: Cat | ✗ | New function requires specific subtype
    print(
        f"T2 DEBUG: {a=}, {b=}, {is_subtype(b, a)=}, {is_subtype(a, b)=}, {type(a)=}, {type(b)=}"
    )
    if is_subtype(b, a) and a != b:
        raise SignatureIncompatible(
            message="T2: Cannot narrow parameter type from base to derived (contravariant narrowing).",
            context={"A_type": a, "B_type": b},
            suggestion="Relax the target type to the base type or use a union type to allow all valid inputs.",
        )

    # T3: Interface → Concrete | A: Sized → B: list | ✗ | Implementation restricts valid inputs
    # If A is an ABC/protocol/interface and B is a concrete type, and B is not a subtype of A, fail
    import collections.abc

    if (
        isinstance(a, type)
        and hasattr(collections.abc, a.__name__)
        and isinstance(b, type)
        and not issubclass(b, a)
    ):
        raise SignatureIncompatible(
            message="T3: Interface/ABC cannot be replaced by a concrete type unless it is a subtype.",
            context={"A_type": a, "B_type": b},
            suggestion="Use a protocol or ABC as the target type, or ensure the concrete type is a valid subtype.",
        )

    # | T3 | Interface → Concrete | A: Sized → B: list | ✗ | Implementation restricts valid inputs
    # | T4 | Type → Wider union | A: int → B: int|str | ✓ | Accepts original type + more
    # | T5 | Required → Optional | A: int → B: int|None | ✓ | Original callers already pass required type
    # | T6 | Implicit conversion | A: int → B: float | ✗ | No explicit subtype relationship
    # | T7 | ABC hierarchy | A: Integral → B: Real | ✓ | Explicit subtyping via ABCs
    # | T8 | Adjacent types | A: uint8 → B: uint16 | ✗ | Behavioral differences matter
    # | T9 | Derived → Base (widening) | A: Cat → B: Animal | ✓ | Contravariant parameter acceptance
    # | T10 | Container invariance | A: list[int] → B: list[str] | ✗ | Generic parameters invariant
    # | T11 | Container contravariance | A: list[Dog] → B: list[Animal] | ✓ | List of Dog is compatible with list of Animal

    # Handle union types (e.g., int|str)
    if isinstance(b, str) and "|" in b:
        b_types = [t.strip() for t in b.split("|")]
        # Accept if a_type matches any type in the union or is subtype
        for bt in b_types:
            if is_type_compatible(a, bt):
                return True
        # Optionals: None in union
        return a == "None" and "None" in b_types
    # Optionals: e.g., int|None
    if isinstance(b, str) and b.endswith("|None"):
        base_type = b[:-5]
        if is_type_compatible(a, base_type) or a == "None":
            return True

    # Container types: e.g., list[int], dict[str, int]
    import types

    def parse_container(t):
        # Handle Python 3.9+ generics (e.g., list[int])
        if isinstance(t, types.GenericAlias):
            base = t.__origin__
            args = t.__args__
            return base, args
        # Handle string-based generics (legacy)
        if not isinstance(t, str) or "[" not in t or not t.endswith("]"):
            return t, None
        base, inner = t.split("[", 1)
        inner = inner[:-1]
        parts = []
        depth = 0
        buf = ""
        for c in inner:
            if c == "," and depth == 0:
                parts.append(buf.strip())
                buf = ""
            else:
                if c == "[":
                    depth += 1
                elif c == "]":
                    depth -= 1
                buf += c
        if buf:
            parts.append(buf.strip())
        return base.strip(), parts

    a_base, a_args = parse_container(a)
    b_base, b_args = parse_container(b)
    # T10: Container invariance (list[int] vs list[str])
    if a_args and b_args:
        if a_base != b_base or len(a_args) != len(b_args):
            raise SignatureIncompatible(
                message="T10: Container types must match exactly (invariant).",
                context={"A_type": a, "B_type": b},
                suggestion="Ensure container base types and all type arguments match exactly.",
            )
        for aa, ba in zip(a_args, b_args):
            if not is_type_compatible(aa, ba):
                raise SignatureIncompatible(
                    message="T10: Container type arguments must match exactly (invariant).",
                    context={"A_type": aa, "B_type": ba},
                    suggestion="Ensure all container type arguments match exactly.",
                )
        return True
    # T11: Container contravariance (list[Dog] vs list[Animal])
    # Accept if a_args and b_args, and each a_arg is subtype of b_arg
    if a_args and b_args and (a_base == b_base and len(a_args) == len(b_args)):
        for aa, ba in zip(a_args, b_args):
            if not (is_type_compatible(aa, ba) or is_subtype(aa, ba)):
                return False
        return True

    return True
