from __future__ import annotations
# 1. Inheritance/Overriding
class InheritA:
    def foo(self, x: int) -> int:
        return x

class InheritBGood(InheritA):
    def foo(self, x: int) -> int:
        return x + 1

class InheritBBad(InheritA):
    def foo(self, x: str) -> int:
        return len(x)

# 2. Method Addition/Removal
class AddRemoveA:
    def foo(self): return 1

class AddRemoveBGood(AddRemoveA):
    def foo(self): return 2
    def bar(self): return 3  # extra method, should be fine

class AddRemoveBBad(AddRemoveA):
    pass  # removes foo, should fail

# 3. Dunder Methods
class DunderA:
    def __call__(self, x: int) -> int: return x

class DunderBGood(DunderA):
    def __call__(self, x: int) -> int: return x + 1

class DunderBBad(DunderA):
    def __call__(self, x: str) -> int: return len(x)

# 4. Class-level Attributes
class AttrA:
    value: int = 1

class AttrBGood(AttrA):
    value: int = 2

class AttrBBad(AttrA):
    value: str = "bad"

# 5. Multiple Inheritance
class MIBase1: pass
class MIBase2: pass
class MIA(MIBase1, MIBase2):
    def foo(self, x: int) -> int: return x

class MIBGood(MIA):
    def foo(self, x: int) -> int: return x + 1

class MIBBad(MIA):
    def foo(self, x: str) -> int: return len(x)

# 6. Method Decorators
def my_decorator(f):
    def wrapper(*a, **k): return f(*a, **k)
    return wrapper

class DecorA:
    @my_decorator
    def foo(self, x: int) -> int: return x

class DecorBGood(DecorA):
    @my_decorator
    def foo(self, x: int) -> int: return x + 1

class DecorBBad(DecorA):
    @my_decorator
    def foo(self, x: str) -> int: return len(x)

# 7. Return Type Compatibility
class ReturnA:
    def foo(self) -> int: return 1

class ReturnBGood(ReturnA):
    def foo(self) -> int: return 2

class ReturnBBad(ReturnA):
    def foo(self) -> str: return "bad"

# 8. Method Signature Evolution
class SigA:
    def foo(self, x: int) -> int: return x

class SigBGood(SigA):
    def foo(self, x: int, y: int = 0) -> int: return x + y

class SigBBad(SigA):
    def foo(self, x: int, y: int) -> int: return x + y

# 9. Class-level Constraints
class ConstraintA:
    def __init__(self, x: int): assert x > 0

class ConstraintBGood(ConstraintA):
    def __init__(self, x: int): assert x > -10

class ConstraintBBad(ConstraintA):
    def __init__(self, x: int): assert x > 10

# 10. Property Methods
class PropA:
    @property
    def foo(self) -> int: return 1

class PropBGood(PropA):
    @property
    def foo(self) -> int: return 2

class PropBBad(PropA):
    @property
    def foo(self) -> str: return "bad"



class MyClassAIncompatible:
    def method(self, x: int) -> str:
        return str(x)

class MyClassA:
    def method(self, x: int) -> int:
        return x * 2

    @staticmethod
    def static_method(x: int) -> int:
        return x * 2

    @staticmethod
    def static_method_incompatible(x: str) -> int:
        return len(x)

    @classmethod
    def class_method(cls, x: int) -> int:
        return x * 2

    @classmethod
    def class_method_incompatible(cls, x: int) -> str:
        return str(x)

def cx_kwargs(**kwargs):
    assert kwargs["x"] > 10
    return kwargs

class MyClassAIncompatible:
    def method(self, x: int) -> str:
        return str(x)

class MyClassA:
    def method(self, x: int) -> int:
        return x * 2

def cx_kwargs(**kwargs):
    assert kwargs["x"] > 10
    return kwargs
