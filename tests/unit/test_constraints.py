from __future__ import annotations

from zvic import _, constrain_this_module

constrain_this_module()


def foo(x: int(_ > 0), y: int(_ > x)) -> int:
    return x, y


def bar(a: int(_ % 2 == 0), b: int(_ > a and _ < 10)) -> int(_ < 10):
    return a + b


def baz(p: int(_ >= 0), q: int(_ >= 0 and _ <= p)) -> int:
    return p - q


if __name__ == "__main__":
    from crosshair.core_and_libs import analyze_function

    for fn in [foo, bar, baz]:
        print(f"\nAnalyzing {fn.__name__}...")
        if msgs := list(analyze_function(fn)):
            print("Counterexample(s) found:")
            for msg in msgs:
                print(msg)
        else:
            print("No counterexample found: all constraints hold.")

    print("\nManual function calls with valid and invalid arguments:")
    # foo: x > 0, y > x
    try:
        print("foo(1, 2):", foo(1, 2))  # valid
    except AssertionError as e:
        print("foo(1, 2) failed:", e)
    try:
        print("foo(0, 2):", foo(0, 2))  # invalid x
    except AssertionError as e:
        print("foo(0, 2) failed:", e)
    try:
        print("foo(1, 1):", foo(1, 1))  # invalid y
    except AssertionError as e:
        print("foo(1, 1) failed:", e)

    # bar: a % 2 == 0, b > a and b < 10
    try:
        print("bar(2, 5):", bar(2, 5))  # valid
    except AssertionError as e:
        print("bar(2, 5) failed:", e)
    try:
        print("bar(3, 5):", bar(3, 5))  # invalid a
    except AssertionError as e:
        print("bar(3, 5) failed:", e)
    try:
        print("bar(2, 2):", bar(2, 2))  # invalid b
    except AssertionError as e:
        print("bar(2, 2) failed:", e)

    # baz: p >= 0, q >= 0 and q <= p
    try:
        print("baz(3, 2):", baz(3, 2))  # valid
    except AssertionError as e:
        print("baz(3, 2) failed:", e)
    try:
        print("baz(-1, 0):", baz(-1, 0))  # invalid p
    except AssertionError as e:
        print("baz(-1, 0) failed:", e)
    try:
        print("baz(3, 4):", baz(3, 4))  # invalid q
    except AssertionError as e:
        print("baz(3, 4) failed:", e)
