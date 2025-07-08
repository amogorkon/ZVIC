def foo(x: int, y: int = 0) -> int:
    return x + y


def bar(y: str, z: float = 1.0) -> str:
    return y[::-1] * int(z)
