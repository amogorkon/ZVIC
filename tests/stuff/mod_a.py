# mypy: ignore-errors
# type: ignore
from __future__ import annotations

import importlib.util
import sys
from collections.abc import Sized
from numbers import Integral
from pathlib import Path

from zvic import _

spec = importlib.util.spec_from_file_location(
    "common_type", Path(__file__).parent / "common_type.py"
)
common_type = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common_type)

sys.modules["common_type"] = common_type
Animal = common_type.Animal


# Placeholder types for signature tests


class uint8(int):
    pass


class Cat(Animal):
    pass


class Dog(Animal):
    pass


# type: ignore

# Module A: Implements all test scenarios from spec-08-Test-Plan.md
# Each function is annotated with its scenario ID and description


# --- Parameter Signature Compatibility ---
# Positional Only
# P1: Same parameters (names irrelevant)
def P1(a, b, /):
    pass


# P2: Additional required args in B (A side)
def P2(a, b, /):
    pass


# P3: Fewer required args in B (A side)
def P3(a, b, /):
    pass


# P4: Additional optional params in B (A side)
def P4(a, /):
    pass


# P5: Fewer optional args in B (A side)
def P5(a, b=1, /):
    pass


# P6: B has less required but more optional args (A side)
def P6(a, b, /):
    pass


# P7: A has less required args than B, same total (A side)
def P7(a, b=1, /):
    pass


# Positional & Keyword
# PK1: Same args, same names
def PK1(a, b):
    pass


# PK2: Same count, different names
def PK2(a, b):
    pass


# PK3: Additional required args in B
def PK3(a, b):
    pass


# PK4: Additional optional args in B
def PK4(a, b):
    pass


# PK5: Fewer required args in B
def PK5(a, b):
    pass


# PK6: Fewer total args in B
def PK6(a, b=1, c=2):
    pass


# PK7: Fewer required, more optional
def PK7(a, b, c=3):
    pass


# PK8: Same names, reordered
def PK8(a, b):
    pass


# PK9: A uses optional args, B requires them
def PK9(a, b=1):
    pass


# Keyword Only
# K1: Same args, same names
def K1(*, a, b):
    pass


# K2: Same count, different names
def K2(*, a, b):
    pass


# K3: Additional required args in B
def K3(*, a, b):
    pass


# K4: Additional optional args in B
def K4(*, a, b):
    pass


# K5: Fewer required args in B
def K5(*, a, b):
    pass


# K6: Fewer total args in B
def K6(*, a, b=1, c=2):
    pass


# K7: Fewer required, more optional
def K7(*, a, b, c=3):
    pass


# K8: Same names, reordered
def K8(*, a, b):
    pass


# K9: A uses optional args, B requires them
def K9(*, a, b=1):
    pass


# *args/**kwargs with Positional Only
# AP1: *args only
def AP1(a, b, /):
    pass


# AP2: *args + prefix
def AP2(a, b, /):
    pass


# AP3: **kwargs only
def AP3(a, b, /):
    pass


# AP4: *args + **kwargs
def AP4(a, b, /):
    pass


# AP5: Insufficient fixed + **kwargs
def AP5(a, b, /):
    pass


# AP6: Optional keyword-only alone
def AP6(a, b, /):
    pass


# AP7: Required keyword-only
def AP7(a, b, /):
    pass


# AP8: Fixed params match A_max
def AP8(a, b, /):
    pass


# AP9: Optional params + **kwargs
def AP9(a, b, /):
    pass


# AP10: Optional keyword-only + *args
def AP10(a, b, /):
    pass


# AP11: Zero args evolution
def AP11():
    pass


# *args/**kwargs with Positional & Keyword
# APK1: *args only
def APK1(a, b):
    pass


# APK2: *args + prefix
def APK2(a, b):
    pass


# APK3: **kwargs only
def APK3(a, b):
    pass


# APK4: *args + **kwargs
def APK4(a, b):
    pass


# APK5: Insufficient fixed + **kwargs
def APK5(a, b):
    pass


# APK6: Required keyword-only
def APK6(a, b):
    pass


# APK7: Optional params + **kwargs
def APK7(a, b):
    pass


# APK8: Optional keyword-only + *args
def APK8(a, b):
    pass


# *args/**kwargs with Keyword Only
# AK1: *args only
def AK1(*, a, b):
    pass


# AK2: Fixed param + *args
def AK2(*, a, b):
    pass


# AK3: **kwargs only
def AK3(*, a, b):
    pass


# AK4: *args, **kwargs
def AK4(*, a, b):
    pass


# AK5: Declares a, plus **kwargs
def AK5(*, a, b):
    pass


# AK6: Adds required kw-only param
def AK6(*, a, b):
    pass


# AK7: Fixed param not in A
def AK7(*, a, b):
    pass


# AK8: Optional kw-only + *args
def AK8(*, a, b):
    pass


# --- Parameter Compatibility ---
# T0: Untyped/Any → Specific type
def T0(a):
    pass


# T1: Same type
def T1(a: int):
    pass


# T2: Base → Derived (narrowing)
def T2(a: Animal):
    pass


# T3: Interface → Concrete
def T3(a: Sized):
    pass


# T4: Type → Wider union
def T4(a: int):
    pass


# T5: Required → Optional
def T5(a: int):
    pass


# T6: Implicit conversion
def T6(a: int):
    pass


# T7: ABC hierarchy
def T7(a: Integral):
    pass


# T8: Adjacent types
def T8(a: uint8):
    pass


# T9: Derived → Base (widening)
def T9(a: Cat):
    pass


# T10: Container invariance
def T10(a: list[int]):
    pass


# T11: Container contravariance
def T11(a: list[Dog]):
    pass


# --- Constraint Signature Compatibility ---
# C0a: No constraint in A, no constraint in B
def C0a(a: int):
    pass


# C0b: same constraint in A and B
def C0b(a: int(_ < 10)):
    pass


# C1: No constraint in A, any in B
def C1(a: int):
    pass


# C2: Any constraint in A, no constraint in B
def C2(a: int(_ < 10)):
    pass


# C3: wider constraint in B
def C3(a: int(_ < 10)):
    pass


# C4: narrower constraint in B
def C4(a: int(_ < 20)):
    pass


# --- Additional Mixed/Aux Tests ---


# M1
def X1(x: int(_ > 10)):
    pass


def X2(x: list(len(_) < 10)):
    return x


class Snail:
    def foo(self, x: int) -> int:
        return x


class Bird:
    def foo(self, x: float) -> int:
        return x

    def bar(self, y: str) -> str:
        return y


class Bird2:
    def foo(self, x: float) -> int:
        return x


class Noodle:
    def __init__(self, x: int):
        self.x = x
