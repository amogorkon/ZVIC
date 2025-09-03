from zvic import constrain_this_module

constrain_this_module()


def foo(x: int(_ >= 10)) -> int(_ < 100):
    return x


foo(10)
