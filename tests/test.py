# WIP

# ================================
import importlib
import inspect
from inspect import signature
from pathlib import Path

from zvic import is_signature_compatible

mod_a_path = Path(__file__).parent / "stuff" / "mod_a.py"
mod_b_path = Path(__file__).parent / "stuff" / "mod_b.py"

spec_a = importlib.util.spec_from_file_location("mod_a", mod_a_path)
mod_a = importlib.util.module_from_spec(spec_a)
spec_a.loader.exec_module(mod_a)

spec_b = importlib.util.spec_from_file_location("mod_b", mod_b_path)
mod_b = importlib.util.module_from_spec(spec_b)
spec_b.loader.exec_module(mod_b)


def test_():
    # | T2 | Base → Derived (narrowing) | A: Animal → B: Cat | ✗ | New function requires specific subtype
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
