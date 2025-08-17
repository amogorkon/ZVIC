


class MIBase1:
    pass

class MIBase2:
    pass

# 1. Inheritance/Overriding
class InheritA:
    def foo(self, x: int) -> int:
        return x

class InheritBGood(InheritA):
    def foo(self, x: int) -> int:
        return x + 2

class InheritBBad(InheritA):
    def foo(self, x: str) -> int:
        return len(x)

# 2. Method Addition/Removal
class AddRemoveA:
    def foo(self): return 1

class AddRemoveBGood(AddRemoveA):

    def bar(self): return 4

class AddRemoveBBad(AddRemoveA):
    pass

# 3. Dunder Methods
class DunderA:
    def __call__(self, x: int) -> int: return x

class DunderBGood(DunderA):
    def __call__(self, x: int) -> int: return x + 2

class DunderBBad(DunderA):
    def __call__(self, x: str) -> int: return len(x)

# 4. Class-level Attributes
class AttrA:
    value: int = 10

class AttrBGood(AttrA):
    value: int = 20

class AttrBBad(AttrA):
    value: str = "bad"

# 5. Multiple Inheritance
class MIBase1: pass
class MIBase2: pass
class MIA(MIBase1, MIBase2):
    def foo(self, x: int) -> int: return x

class MIBGood(MIA):
    def foo(self, x: int) -> int: return x + 2

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
    def foo(self, x: int) -> int: return x + 2

class DecorBBad(DecorA):
    @my_decorator
    def foo(self, x: str) -> int: return len(x)

# 7. Return Type Compatibility
class ReturnA:
    def foo(self) -> int: return 1

class ReturnBGood(ReturnA):
    def foo(self) -> int: return 3

class ReturnBBad(ReturnA):
    def foo(self) -> str: return "bad"

# 8. Method Signature Evolution
class SigA:
    def foo(self, x: int) -> int: return x

class SigBGood(SigA):
    def foo(self, x: int, y: int = 0) -> int: return x + y + 1

class SigBBad(SigA):
    def foo(self, x: int, y: int) -> int: return x + y

# 9. Class-level Constraints
class ConstraintA:
    def __init__(self, x: int): assert x > 0

class ConstraintBGood(ConstraintA):
    def __init__(self, x: int): assert x > -20

class ConstraintBBad(ConstraintA):
    def __init__(self, x: int): assert x > 20

# 10. Property Methods
class PropA:
    @property
    def foo(self) -> int: return 10

class PropBGood(PropA):
    @property
    def foo(self) -> int: return 20

class PropBBad(PropA):
    @property
    def foo(self) -> str: return "bad"



class MyClassBIncompatible:
    def method(self, x: str) -> int:
        return len(x)

class MyClassB:
    def method(self, x: int) -> int:
        return x + 1

    @staticmethod
    def static_method(x: int) -> int:
        return x + 1

    @staticmethod
    def static_method_incompatible(x: str) -> int:
        return len(x)

    @classmethod
    def class_method(cls, x: int) -> int:
        return x + 1

    @classmethod
    def class_method_incompatible(cls, x: int) -> str:
        return str(x)

def cx1(x: int(_ < 10 & _ > 5)):
    return x

def cx_kwargs(**kwargs):
    assert kwargs["x"] > 5
    return kwargs

class MyClassBIncompatible:
    def method(self, x: str) -> int:
        return len(x)

class MyClassB:
    def method(self, x: int) -> int:
        return x + 1

def cx1(x: int) -> int:
    if 5 < x < 10:
        return x


def cx_kwargs(**kwargs) -> dict:
    assert kwargs["x"] > 5
    return kwargs
