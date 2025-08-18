from __future__ import annotations

from pathlib import Path

from zvic.main import canonicalize, load_module

foo_path = Path(__file__).parent / "stuff" / "foo_module.py"
mod = load_module(foo_path, "foo_module")
canonical = canonicalize(mod)


from zvic.main import pprint_recursive

pprint_recursive(canonical)
