import importlib.util
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def mod_a():
    file_path = Path(__file__).parent / "tests" / "stuff" / "mod_a.py"
    spec = importlib.util.spec_from_file_location("mod_a", str(file_path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def mod_b():
    file_path = Path(__file__).parent / "tests" / "stuff" / "mod_b.py"
    spec = importlib.util.spec_from_file_location("mod_b", str(file_path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def mod_c():
    file_path = Path(__file__).parent / "tests" / "stuff" / "mod_c.py"
    spec = importlib.util.spec_from_file_location("mod_c", str(file_path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
