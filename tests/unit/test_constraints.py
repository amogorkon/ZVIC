from __future__ import annotations

from crosshair.core_and_libs import analyze_function

from zvic import _, constrain_this_module

code = constrain_this_module()


def always_fails(x: int(_ > 0)) -> int(_ > 10):
    return 5


def sometimes_fails(x: int(_ > 0)) -> int(_ > 10):
    return x


def unreachable_pre(x: int(_ < 0)) -> int:
    return x


def contradictory_pre(x: int(_ > 0), y: int(_ < 0 and _ > 0)) -> int:
    return x + y


def foo(x: int(_ > 0), y: int(_ > x)) -> int:  # not an int but a tuple - sic!
    return x, y


def bar(a: int(_ % 2 == 0), b: int(_ > a and _ < 10)) -> int(_ < 10):
    return a + b


def baz(p: int(_ >= 0), q: int(_ >= 0 and _ <= p)) -> int:
    return p - q


if __name__ == "__main__":
    for fn in [
        foo,
        bar,
        baz,
        always_fails,
        sometimes_fails,
        unreachable_pre,
        contradictory_pre,
    ]:
        print(f"\nAnalyzing {fn.__name__}...")
        if msgs := list(analyze_function(fn)):
            print("Counterexample(s) found:")
            for msg in msgs:
                print(msg)
        else:
            print("No counterexample found: all constraints hold.")
