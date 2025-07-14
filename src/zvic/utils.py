# type: ignore
"""Utility functions and universal placeholder for ZVIC."""

import ast
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
