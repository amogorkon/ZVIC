from typing import Any

import numpy as np

from zvic import is_compatible


# --- Any and missing type annotation cases ---
def foo_any(x: Any) -> Any:
    return x


def foo_untyped(x):
    return x


def foo_typed(x: int) -> int:
    return x


def foo_typed2(x: str) -> int:
    return 42


def foo_typed_ret_any(x: int) -> Any:
    return x


def foo_any_ret_typed(x: Any) -> int:
    return 1


def foo_untyped_ret_typed(x) -> int:
    return 1


def foo_typed_ret_untyped(x: int):
    return x


def test_any_and_missing_type_compatibility():
    cases = [
        # Any or missing is compatible with anything (permissive)
        (foo_any, foo_typed, True),
        (foo_typed, foo_any, True),
        (foo_untyped, foo_typed, True),
        (foo_typed, foo_untyped, True),
        (foo_any, foo_untyped, True),
        (foo_untyped, foo_any, True),
        (foo_typed2, foo_any, True),
        (foo_any, foo_typed2, True),
        # Return type Any or missing is compatible with anything
        (foo_typed_ret_any, foo_typed, True),
        (foo_typed, foo_typed_ret_any, True),
        (foo_untyped_ret_typed, foo_typed, True),
        (foo_typed, foo_untyped_ret_typed, True),
        (foo_typed_ret_untyped, foo_typed, True),
        (foo_typed, foo_typed_ret_untyped, True),
        # But int <-> str is not compatible
        (foo_typed, foo_typed2, False),
        (foo_typed2, foo_typed, False),
    ]
    for f1, f2, expected in cases:
        assert is_compatible(f1, f2) == expected, (
            f"{f2.__name__} should {'be' if expected else 'not be'} compatible with {f1.__name__} (Any/missing)"
        )


# --- parameter reordering and name changes ---
def foo_posonly_names(x: int, /, y: int) -> int:
    return x + y


def foo_posonly_names2(a: int, /, b: int) -> int:
    return a + b


def foo_posonly_reorder(y: int, /, x: int) -> int:
    return x + y


def foo_kwonly_names(x: int, *, y: int) -> int:
    return x + y


def foo_kwonly_names2(a: int, *, b: int) -> int:
    return a + b


def foo_kwonly_reorder(x: int, *, z: int, y: int) -> int:
    return x + y + z


# --- Explicit compatibility matrix for parameter reordering and name changes ---
def test_param_reordering_and_names():
    cases = [
        # Positional-only: order of types matters, names do not
        (foo_posonly_names, foo_posonly_names2, True),
        (foo_posonly_names2, foo_posonly_names, True),
        (foo_posonly_names, foo_posonly_reorder, False),  # order of types differs
        (foo_posonly_reorder, foo_posonly_names, False),
        # Keyword-only: order of names does not matter
        (foo_kwonly_names, foo_kwonly_names2, True),
        (foo_kwonly_names2, foo_kwonly_names, True),
        (foo_kwonly_names, foo_kwonly_reorder, True),
        (foo_kwonly_reorder, foo_kwonly_names, True),
    ]
    for f1, f2, expected in cases:
        assert is_compatible(f1, f2) == expected, (
            f"{f2.__name__} should {'be' if expected else 'not be'} compatible with {f1.__name__} (param reorder/names)"
        )


# --- positional-only and keyword-only parameter variants ---
def foo_posonly(x: int, /, y: int) -> int:
    return x + y


def foo_kwonly(x: int, *, y: int) -> int:
    return x + y


def foo_posonly_kwonly(x: int, /, y: int, *, z: int) -> int:
    return x + y + z


def foo_normal(x: int, y: int, z: int) -> int:
    return x + y + z


# --- Explicit compatibility matrix for positional-only and keyword-only ---
def test_posonly_kwonly_compatibility_matrix():
    cases = [
        # foo_posonly: (x: int, /, y: int) -> int
        (foo_posonly, foo_kwonly, False),
        (foo_posonly, foo_posonly_kwonly, False),
        (foo_posonly, foo_normal, True),  # normal can accept both positional
        # foo_kwonly: (x: int, *, y: int) -> int
        (foo_kwonly, foo_posonly, False),
        (foo_kwonly, foo_posonly_kwonly, False),
        (foo_kwonly, foo_normal, True),  # normal can accept both
        # foo_posonly_kwonly: (x: int, /, y: int, *, z: int) -> int
        (foo_posonly_kwonly, foo_posonly, False),
        (foo_posonly_kwonly, foo_kwonly, False),
        (foo_posonly_kwonly, foo_normal, True),
        # foo_normal: (x: int, y: int, z: int) -> int
        (foo_normal, foo_posonly, False),
        (foo_normal, foo_kwonly, False),
        (foo_normal, foo_posonly_kwonly, False),
    ]
    for f1, f2, expected in cases:
        assert is_compatible(f1, f2) == expected, (
            f"{f2.__name__} should {'be' if expected else 'not be'} compatible with {f1.__name__} (posonly/kwonly)"
        )


# --- Explicit compatibility matrix for foo_np_* ---
def test_foo_np_compatibility_matrix():
    cases = [
        # foo_np_int32: (x: np.int32) -> np.int32
        (foo_np_int32, foo_np_uint32, False),
        (foo_np_int32, foo_np_uint64, False),
        (foo_np_int32, foo_np_mixed, False),
        # foo_np_uint32: (x: np.uint32) -> np.uint32
        (foo_np_uint32, foo_np_int32, False),
        (foo_np_uint32, foo_np_uint64, False),
        (foo_np_uint32, foo_np_mixed, False),
        # foo_np_uint64: (x: np.uint64) -> np.uint64
        (foo_np_uint64, foo_np_int32, False),
        (foo_np_uint64, foo_np_uint32, False),
        (foo_np_uint64, foo_np_mixed, False),
        # foo_np_mixed: (x: np.uint32, y: np.int64) -> np.int64
        (foo_np_mixed, foo_np_int32, False),
        (foo_np_mixed, foo_np_uint32, False),
        (foo_np_mixed, foo_np_uint64, False),
    ]
    for f1, f2, expected in cases:
        assert is_compatible(f1, f2) == expected, (
            f"{f2.__name__} should {'be' if expected else 'not be'} compatible with {f1.__name__}"
        )


# --- Explicit compatibility matrix for bar_np_* ---
def test_bar_np_compatibility_matrix():
    cases = [
        # bar_np_uint8: (y: np.uint8) -> np.uint8
        (bar_np_uint8, bar_np_uint16, False),
        (bar_np_uint8, bar_np_float32, False),
        # bar_np_uint16: (y: np.uint16, z: np.uint32) -> np.uint32
        (bar_np_uint16, bar_np_uint8, False),
        (bar_np_uint16, bar_np_float32, False),
        # bar_np_float32: (y: np.float32) -> np.float32
        (bar_np_float32, bar_np_uint8, False),
        (bar_np_float32, bar_np_uint16, False),
    ]
    for f1, f2, expected in cases:
        assert is_compatible(f1, f2) == expected, (
            f"{f2.__name__} should {'be' if expected else 'not be'} compatible with {f1.__name__}"
        )


# --- foo variants ---
def foo_a(x: int) -> int:
    return x


def foo_b(x: int) -> int:
    return x


def foo_c(x: int, y: int) -> int:
    return x + y


def foo_d(x: int = 42) -> int:
    return x


def foo_e(x: str) -> int:
    return len(x)


def foo_f(x: int, y: int = 0) -> int:
    return x + y


def foo_g(x: int, y: int) -> int:
    return x * y


# --- numpy foo variants ---
def foo_np_int32(x: np.int32) -> np.int32:
    return x


def foo_np_uint32(x: np.uint32) -> np.uint32:
    return x


def foo_np_uint64(x: np.uint64) -> np.uint64:
    return x


def foo_np_mixed(x: np.uint32, y: np.int64) -> np.int64:
    return y


# --- bar variants ---
def bar_a(y: str, z: float = 1.0) -> str:
    return y * int(z)


def bar_b(y: str, z: float = 1.0) -> str:
    return y.upper() * int(z)


def bar_c(y: str) -> str:
    return y[::-1]


def bar_d(y: str, z: float = 1.0, w: int = 2) -> str:
    return y * int(z) * w


def bar_e(y: str, z: float = 1.0) -> int:
    return int(z)


def bar_f(y: str, z: float = 1.0) -> str:
    return y[::-1] * int(z)


def bar_g(y: str, z: float) -> str:
    return y + str(z)


# --- numpy bar variants ---
def bar_np_uint8(y: np.uint8) -> np.uint8:
    return y


def bar_np_uint16(y: np.uint16, z: np.uint32) -> np.uint32:
    return z


def bar_np_float32(y: np.float32) -> np.float32:
    return y


# --- Explicit compatibility matrix for foo_* ---
def test_foo_compatibility_matrix():
    # (f1, f2, expected)
    cases = [
        # foo_a: (x: int) -> int
        (foo_a, foo_b, True),  # identical signature
        (foo_a, foo_c, False),  # foo_c requires extra arg
        (foo_a, foo_d, True),  # foo_d adds default
        (foo_a, foo_e, False),  # type mismatch
        (foo_a, foo_f, True),  # foo_f adds default
        (foo_a, foo_g, False),  # foo_g requires extra arg
        # foo_b: (x: int) -> int
        (foo_b, foo_a, True),
        (foo_b, foo_c, False),
        (foo_b, foo_d, True),
        (foo_b, foo_e, False),
        (foo_b, foo_f, True),
        (foo_b, foo_g, False),
        # foo_c: (x: int, y: int) -> int
        (foo_c, foo_a, False),  # foo_a missing y
        (foo_c, foo_b, False),
        (foo_c, foo_d, False),
        (foo_c, foo_e, False),
        (foo_c, foo_f, True),  # foo_f adds default for y
        (foo_c, foo_g, True),  # foo_g same signature
        # foo_d: (x: int = 42) -> int
        (foo_d, foo_a, False),  # foo_a requires x
        (foo_d, foo_b, False),
        (foo_d, foo_c, False),
        (foo_d, foo_e, False),
        (foo_d, foo_f, False),
        (foo_d, foo_g, False),
        # foo_e: (x: str) -> int
        (foo_e, foo_a, False),
        (foo_e, foo_b, False),
        (foo_e, foo_c, False),
        (foo_e, foo_d, False),
        (foo_e, foo_f, False),
        (foo_e, foo_g, False),
        # foo_f: (x: int, y: int = 0) -> int
        (foo_f, foo_a, True),  # foo_a is compatible (y defaulted)
        (foo_f, foo_b, True),
        (foo_f, foo_c, False),  # foo_c missing default for y
        (foo_f, foo_d, True),  # foo_d is compatible (y defaulted, ignored)
        (foo_f, foo_e, False),
        (foo_f, foo_g, False),
        # foo_g: (x: int, y: int) -> int
        (foo_g, foo_a, False),
        (foo_g, foo_b, False),
        (foo_g, foo_c, True),
        (foo_g, foo_d, False),
        (foo_g, foo_e, False),
        (foo_g, foo_f, True),
    ]
    for f1, f2, expected in cases:
        assert is_compatible(f1, f2) == expected, (
            f"{f2.__name__} should {'be' if expected else 'not be'} compatible with {f1.__name__}"
        )


# --- Explicit compatibility matrix for bar_* ---
def test_bar_compatibility_matrix():
    cases = [
        # bar_a: (y: str, z: float = 1.0) -> str
        (bar_a, bar_b, True),  # identical signature
        (bar_a, bar_c, False),  # bar_c missing z
        (bar_a, bar_d, True),  # bar_d adds default w
        (bar_a, bar_e, False),  # return type mismatch
        (bar_a, bar_f, True),  # bar_f identical signature
        (bar_a, bar_g, False),  # bar_g z not defaulted
        # bar_b: (y: str, z: float = 1.0) -> str
        (bar_b, bar_a, True),
        (bar_b, bar_c, False),
        (bar_b, bar_d, True),
        (bar_b, bar_e, False),
        (bar_b, bar_f, True),
        (bar_b, bar_g, False),
        # bar_c: (y: str) -> str
        (bar_c, bar_a, False),
        (bar_c, bar_b, False),
        (bar_c, bar_d, False),
        (bar_c, bar_e, False),
        (bar_c, bar_f, False),
        (bar_c, bar_g, False),
        # bar_d: (y: str, z: float = 1.0, w: int = 2) -> str
        (bar_d, bar_a, True),
        (bar_d, bar_b, True),
        (bar_d, bar_c, False),
        (bar_d, bar_e, False),
        (bar_d, bar_f, True),
        (bar_d, bar_g, False),
        # bar_e: (y: str, z: float = 1.0) -> int
        (bar_e, bar_a, False),
        (bar_e, bar_b, False),
        (bar_e, bar_c, False),
        (bar_e, bar_d, False),
        (bar_e, bar_f, False),
        (bar_e, bar_g, False),
        # bar_f: (y: str, z: float = 1.0) -> str
        (bar_f, bar_a, True),
        (bar_f, bar_b, True),
        (bar_f, bar_c, False),
        (bar_f, bar_d, True),
        (bar_f, bar_e, False),
        (bar_f, bar_g, False),
        # bar_g: (y: str, z: float) -> str
        (bar_g, bar_a, True),  # bar_a has z defaulted, bar_g does not
        (bar_g, bar_b, True),
        (bar_g, bar_c, False),
        (bar_g, bar_d, True),
        (bar_g, bar_e, False),
        (bar_g, bar_f, True),
    ]
    for f1, f2, expected in cases:
        assert is_compatible(f1, f2) == expected, (
            f"{f2.__name__} should {'be' if expected else 'not be'} compatible with {f1.__name__}"
        )
