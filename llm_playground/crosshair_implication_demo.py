# Simple CrossHair implication demo for ZVIC constraints


from crosshair.core_and_libs import analyze_function
from crosshair.libimpl.builtins import precondition


@precondition(lambda x: x > 20)
def implication_check(x: int):
    assert x > 30
    # For all x: if A holds, then B must also hold
    # A: x > 20, B: x > 30
    if x > 20:
        assert x > 30
    return True


if __name__ == "__main__":
    msgs = list(analyze_function(implication_check))
    for msg in msgs:
        print(msg)
    if not msgs:
        print(
            "No counterexample found: implication holds (B is at least as permissive as A)"
        )
