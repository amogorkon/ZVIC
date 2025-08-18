# mypy: ignore-errors
# type: ignore
# mypy: ignore-errors

from __future__ import annotations

import sys
from numbers import Real

from zvic import _

common_type = sys.modules["common_type"]

Animal = common_type.Animal


# Placeholder types for signature tests
class Cat(Animal):
    pass


class Dog(Animal):
    pass


class uint16(int):
    pass


# Module B: Implements all test scenarios from spec-08-Test-Plan.md
# Each function is annotated with its scenario ID and description


# --- Parameter Signature Compatibility ---
# Positional Only
# P1: Same parameters (names irrelevant)
def P1(x, y, /):
    pass


# P2: Additional required args in B
def P2(x, y, z, /):
    pass


# P3: Fewer required args in B
def P3(x, /):
    pass


# P4: Additional optional params in B
def P4(x, y=5, /):
    pass


# P5: Fewer optional args in B
def P5(x, /):
    pass


# P6: B has less required but more optional args
def P6(x, y=5, z=6, /):
    pass


# P7: A has less required args than B, same total
def P7(x, y, /):
    pass


# Positional & Keyword
# PK1: Same args, same names
def PK1(a, b):
    pass


# PK2: Same count, different names
def PK2(x, y):
    pass


# PK3: Additional required args in B
def PK3(a, b, c):
    pass


# PK4: Additional optional args in B
def PK4(a, b, c=0):
    pass


# PK5: Fewer required args in B
def PK5(a):
    pass


# PK6: Fewer total args in B
def PK6(a, b=1):
    pass


# PK7: Fewer required, more optional
def PK7(a, b=2, c=3):
    pass


# PK8: Same names, reordered
def PK8(b, a):
    pass


# PK9: A uses optional args, B requires them
def PK9(a, b):
    pass


# Keyword Only
# K1: Same args, same names
def K1(*, a, b):
    pass


# K2: Same count, different names
def K2(*, x, y):
    pass


# K3: Additional required args in B
def K3(*, a, b, c):
    pass


# K4: Additional optional args in B
def K4(*, a, b, c=0):
    pass


# K5: Fewer required args in B
def K5(*, a):
    pass


# K6: Fewer total args in B
def K6(*, a, b=1):
    pass


# K7: Fewer required, more optional
def K7(*, a, b=2, c=3):
    pass


# K8: Same names, reordered
def K8(*, b, a):
    pass


# K9: A uses optional args, B requires them
def K9(*, a, b):
    pass


# *args/**kwargs with Positional Only
# AP1: *args only
def AP1(*args):
    pass


# AP2: *args + prefix
def AP2(x, *args):
    pass


# AP3: **kwargs only
def AP3(**kwargs):
    pass


# AP4: *args + **kwargs
def AP4(*args, **kwargs):
    pass


# AP5: Insufficient fixed + **kwargs
def AP5(a=1, **kwargs):
    pass


# AP6: Optional keyword-only alone
def AP6(*, k=5):
    pass


# AP7: Required keyword-only
def AP7(*args, k):
    pass


# AP8: Fixed params match A_max
def AP8(x, y):
    pass


# AP9: Optional params + **kwargs
def AP9(x, y=1, **kwargs):
    pass


# AP10: Optional keyword-only + *args
def AP10(*args, k=5):
    pass


# AP11: Zero args evolution
def AP11(*, k=5):
    pass


# *args/**kwargs with Positional & Keyword
# APK1: *args only
def APK1(*args):
    pass


# APK2: *args + prefix
def APK2(x, *args):
    pass


# APK3: **kwargs only
def APK3(**kwargs):
    pass


# APK4: *args + **kwargs
def APK4(*args, **kwargs):
    pass


# APK5: Insufficient fixed + **kwargs
def APK5(a=1, **kwargs):
    pass


# APK6: Required keyword-only
def APK6(*args, k):
    pass


# APK7: Optional params + **kwargs
def APK7(x, y=1, **kwargs):
    pass


# APK8: Optional keyword-only + *args
def APK8(*args, k=5):
    pass


# *args/**kwargs with Keyword Only
# AK1: *args only
def AK1(*args):
    pass


# AK2: Fixed param + *args
def AK2(x, *args):
    pass


# AK3: **kwargs only
def AK3(**kwargs):
    pass


# AK4: *args, **kwargs
def AK4(*args, **kwargs):
    pass


# AK5: Declares a, plus **kwargs
def AK5(a=1, **kwargs):
    pass


# AK6: Adds required kw-only param
def AK6(*args, k):
    pass


# AK7: Fixed param not in A
def AK7(x, y=1, **kwargs):
    pass


# AK8: Optional kw-only + *args
def AK8(*args, k=5):
    pass


# --- Parameter Compatibility ---
# T0: Untyped/Any → Specific type
def T0(a: int):
    pass


# T1: Same type
def T1(a: int):
    pass


# T2: Base → Derived (narrowing)
def T2(a: Cat):
    pass


# T3: Interface → Concrete
def T3(a: list):
    pass


# T4: Type → Wider union
def T4(a: int | str):
    pass


# T5: Required → Optional
def T5(a: int | None):
    pass


# T6: Implicit conversion
def T6(a: float):
    pass


# T7: ABC hierarchy
def T7(a: Real):
    pass


# T8: Adjacent types
def T8(a: uint16):
    pass


# T9: Derived → Base (widening)
def T9(a: Animal):
    pass


# T10: Container invariance
def T10(a: list[str]):
    pass


# T11: Container contravariance
def T11(a: list[Animal]):
    pass


# --- Constraint Signature Compatibility ---
# C0a: No constraint in A, no constraint in B
def C0a(a: int):
    pass


# C0b: same constraint in A and B
def C0b(a: int(_ < 10)):
    pass


# C1: No constraint in A, any in B
def C1(a: int(_ < 10)):
    pass


# C2: Any constraint in A, no constraint in B
def C2(a: int):
    pass


# C3: wider constraint in B
def C3(a: int(_ < 20)):
    pass


# C4: narrower constraint in B
def C4(a: int(_ < 10)):
    pass


# --- Additional Mixed/Aux Tests ---
# M1:
def X1(x: str):
    pass


def X2(x: list(len(_) < 11)):
    return x


class Snail:
    def foo(self, x: float) -> int:
        return x


class Bird:
    def bar(self, y: str) -> str:
        return y


class Bird2:
    def foo(self, x: float) -> int:
        return x

    def bar(self, y: str) -> str:
        return y


class Noodle:
    def __init__(self, x: float):
        self.x = x
