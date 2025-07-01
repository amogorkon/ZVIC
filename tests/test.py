import inspect

from zvic import canonicalize

# ================================


def simple_func(a: int, b: str = "x") -> bool:
    return str(a) == b


class SimpleClass:
    def foo(self, x: int) -> int:
        return x + 1

    def bar(self, y: str) -> str:
        return y.upper()


def test_canonicalize_function():
    result = canonicalize(simple_func)
    assert result["name"] == "simple_func"
    assert any(p.get("name") == "a" for p in result["params"])
    assert result["return"] == "<class 'bool'>"


def test_canonicalize_class():
    result = canonicalize(SimpleClass)
    assert result["__class__"] == "SimpleClass"
    assert "foo" in result["methods"]
    assert "bar" in result["methods"]


# ================================
if __name__ == "__main__":
    for name, func in globals().copy().items():
        if name.startswith("test_"):
            print(f" ↓↓↓↓↓↓↓ {name} ↓↓↓↓↓↓")
            print(inspect.getsource(func))
            func()
            print(f"↑↑↑↑↑↑ {name} ↑↑↑↑↑↑")
            print()
