from zvic import _


def foo(x: int(_ < 10), y: str(len(_) > 5)) -> None:
    """Function for testing type normalization and annotation constraints."""
    x += 1
    print(x)


def bar(x: int, *, b=2, c=1, a=23) -> int:
    return x + 1


def baz(y: str) -> int(_ > 3):
    return len(y) if len(y) > 3 else 10


class Foo:
    """A class with methods to test type normalization."""

    def method_x(self, a: int) -> str:
        return str(a)

    def method_a(self, b: str) -> int:
        return len(b)

    @staticmethod
    def method_d(c: float) -> float:
        return c * 2.0


# Callable class for testing
class CallableClass:
    def __call__(self, x: int, y: str) -> int:
        return x + len(y)
