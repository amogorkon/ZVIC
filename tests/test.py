# WIP

# ================================
import inspect
from inspect import signature
from pathlib import Path

from zvic import is_signature_compatible, load_module

mod_a_path = Path(__file__).parent / "stuff" / "mod_a.py"
mod_b_path = Path(__file__).parent / "stuff" / "mod_b.py"

mod_a = load_module(mod_a_path, "mod_a")
mod_b = load_module(mod_b_path, "mod_b")


def test_():
    scenario = "T2"
    a = signature(getattr(mod_a, scenario))
    b = signature(getattr(mod_b, scenario))
    is_signature_compatible(a, b)


# ================================
if __name__ == "__main__":
    for name, func in globals().copy().items():
        if name.startswith("test_"):
            print(f" ↓↓↓↓↓↓↓ {name} ↓↓↓↓↓↓")
            print(inspect.getsource(func))
            func()
            print(f"↑↑↑↑↑↑ {name} ↑↑↑↑↑↑")
            print()
