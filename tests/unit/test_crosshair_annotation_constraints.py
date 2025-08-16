from zvic import _, constrain_this_module

# print(constrain_this_module())


def foo(x: int(_ > 0), y: int(_ > 10)) -> int(_ > 0 and _ < 0):
    return x - y


if __name__ == "__main__":
    from crosshair.core_and_libs import analyze_function

    msgs = list(analyze_function(foo))
    if msgs:
        print("Counterexample(s) found:")
        for msg in msgs:
            print(msg)
    else:
        print("No counterexample found: all constraints hold.")
