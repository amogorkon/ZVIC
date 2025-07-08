def foo(x: int = 42) -> int:
    return x


def bar(y: str, z: float = 1.0, w: int = 2) -> str:
    return y * int(z) * w
