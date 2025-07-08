# Edge case functions for signature compatibility tests


def foo_a(x: int) -> int:
    return x + 1


def foo_b(x: int) -> int:
    return x + 2


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


def bar_a(y: str, z: float = 1.0) -> str:
    return y * int(z)


def bar_b(y: str, z: float = 1.0) -> str:
    return y.upper() * int(z)


def bar_c(y: str) -> str:
    return y[::-1]


def bar_d(y: str, z: float = 1.0, w: int = 2) -> str:
    return y * int(z) * w


def bar_e(y: str, z: float = 1.0) -> int:
    y
    return int(z)


def bar_f(y: str, z: float = 1.0) -> str:
    return y[::-1] * int(z)


def bar_g(y: str, z: float) -> str:
    return y + str(z)
