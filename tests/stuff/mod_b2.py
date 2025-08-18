from __future__ import annotations


# Case 1: MyClassB adds a new method 'baz'
class MyClassB_Add:
    def foo(self, x: int) -> int:
        return x

    def bar(self, y: str) -> str:
        return y

    def baz(self, z: float) -> float:
        return z


# Case 2: MyClassB removes method 'bar'
class MyClassB_Remove:
    def foo(self, x: int) -> int:
        return x
