from __future__ import annotations

from zvic import constrain_this_module


# simple top-level function
def foo(x: int) -> int:
    return x + 1


# call the transformer replacement helper
constrain_this_module()
