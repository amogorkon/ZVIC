#!/usr/bin/env python3
"""Run a few spec-08 compatibility examples and print ZVIC diagnostics.

This script uses the test modules in `tests/stuff` so it's meant to be run from
the repository on a developer machine (not a published package).
"""

import sys
from pathlib import Path

# Ensure 'src' is on sys.path so we can import the local zvic package
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from zvic import load_module
from zvic.compatibility import is_compatible
from zvic.exception import SignatureIncompatible


def run_example(mod_a_path: Path, mod_b_path: Path, symbol: str) -> None:
    mod_a = load_module(mod_a_path, f"mod_a_example_{symbol}")
    mod_b = load_module(mod_b_path, f"mod_b_example_{symbol}")
    a_obj = getattr(mod_a, symbol)
    b_obj = getattr(mod_b, symbol)

    print(f"--- Example: {symbol} ---")
    try:
        is_compatible(a_obj, b_obj)
        print("Result: compatible (no exception)")
    except SignatureIncompatible as exc:
        # SignatureIncompatible is JSON-serializable via .to_json()
        try:
            print("Result: incompatible — diagnostic:")
            print(exc.to_json())
        except Exception:
            print("Result: incompatible —", repr(exc))
    print()


def main() -> None:
    tests_dir = REPO_ROOT / "tests" / "stuff"
    mod_a = tests_dir / "mod_a.py"
    mod_b = tests_dir / "mod_b.py"

    # Run three representative scenarios from spec-08
    for sym in ("P1", "P2", "C4"):
        run_example(mod_a, mod_b, sym)


if __name__ == "__main__":
    main()
