import enum
import types

from zvic.main import canonical_signature, canonicalize


def find_non_string_leaves(obj, path=None):
    """Recursively print all non-string leaves in a structure."""
    if path is None:
        path = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            find_non_string_leaves(v, path + [str(k)])
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            find_non_string_leaves(v, path + [f"[{i}]"])
    elif not isinstance(obj, str):
        print(
            f"Non-string leaf at {'.'.join(path)}: {repr(obj)} (type: {type(obj).__name__})"
        )


def test_canonicalize_simple_class():
    class Point:
        x: int
        y: int

    result = canonicalize(Point)
    print("canonicalize(Point):", result)
    find_non_string_leaves(result)
    assert isinstance(result, dict)
    assert result["class"] == "Point" or "class" in result or "type" in result


def test_canonicalize_enum():
    class Color(enum.Enum):
        RED = 1
        GREEN = 2

    result = canonicalize(Color)
    print("canonicalize(Color):", result)
    find_non_string_leaves(result)
    assert isinstance(result, dict)
    assert "members" in result or "properties" in result


def test_canonicalize_module():
    mod = types.ModuleType("mymod")

    def foo(x: int) -> int:
        return x

    mod.foo = foo
    result = canonicalize(mod)
    print("canonicalize(module):", result)
    find_non_string_leaves(result)
    assert isinstance(result, dict)
    assert "foo" in result


def test_canonical_signature():
    def bar(x: int, y: str = "hi") -> bool:
        return True

    sig = canonical_signature(bar)
    print("canonical_signature(bar):", sig)
    find_non_string_leaves(sig)
    assert isinstance(sig, dict)
    assert sig["name"] == "bar"
    assert isinstance(sig["params"], list)
    assert isinstance(sig["return"], dict) or sig["return"] is None


if __name__ == "__main__":
    print("\n--- canonicalize(Point) ---")
    test_canonicalize_simple_class()
    print("\n--- canonicalize(Color) ---")
    test_canonicalize_enum()
    print("\n--- canonicalize(module) ---")
    test_canonicalize_module()
    print("\n--- canonical_signature(bar) ---")
    test_canonical_signature()
