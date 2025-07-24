from zvic import constrain_this_module
from zvic.utils import _

# Test function with type and constraint on parameter
constrain_this_module()


def foo(x: int(_ > 10)) -> int(_ < 100):
    return x * 2


def test_type_assertion():
    for val in ["string", 5.5, None]:
        try:
            foo(val)
        except AssertionError as e:
            print(f"Type assertion for {val}: PASSED ({e})")
        except Exception as e:
            print(f"Type assertion for {val}: FAILED with {type(e).__name__} ({e})")
        else:
            print(f"Type assertion for {val}: FAILED (no error)")


def test_constraint_assertion():
    for val in [5, 10]:
        try:
            foo(val)
        except AssertionError as e:
            print(f"Constraint assertion for {val}: PASSED ({e})")
        except Exception as e:
            print(
                f"Constraint assertion for {val}: FAILED with {type(e).__name__} ({e})"
            )
        else:
            print(f"Constraint assertion for {val}: FAILED (no error)")


def test_return_constraint():
    for val in [11]:
        try:
            foo(val)
        except AssertionError as e:
            print(f"Return constraint for {val}: PASSED ({e})")
        except Exception as e:
            print(f"Return constraint for {val}: FAILED with {type(e).__name__} ({e})")
        else:
            print(f"Return constraint for {val}: FAILED (no error)")


def test_all_pass():
    try:
        assert foo(11) == 22
        print("All checks pass: PASSED")
    except Exception as e:
        print(f"All checks pass: FAILED ({type(e).__name__}: {e})")


if __name__ == "__main__":
    test_type_assertion()
    test_constraint_assertion()
    test_return_constraint()
    test_all_pass()
