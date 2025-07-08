import pytest
import importlib.util
import sys
import os

# Fixtures to provide mod_a, mod_b, mod_c for tdd_test.py
@pytest.fixture
def mod_a():
    path = os.path.join(os.path.dirname(__file__), 'stuff', 'mod_a.py')
    spec = importlib.util.spec_from_file_location('mod_a', path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules['mod_a'] = mod
    spec.loader.exec_module(mod)
    return mod

@pytest.fixture
def mod_b():
    path = os.path.join(os.path.dirname(__file__), 'stuff', 'mod_b.py')
    spec = importlib.util.spec_from_file_location('mod_b', path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules['mod_b'] = mod
    spec.loader.exec_module(mod)
    return mod

@pytest.fixture
def mod_c():
    path = os.path.join(os.path.dirname(__file__), 'stuff', 'mod_c.py')
    spec = importlib.util.spec_from_file_location('mod_c', path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules['mod_c'] = mod
    spec.loader.exec_module(mod)
    return mod
