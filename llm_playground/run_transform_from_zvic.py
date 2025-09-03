"""Small runner to exercise the zvic.tools.transform_replace via zvic.main.

This script prepares `sys.path` (adds local `src`) so the `zvic` package in
this workspace is importable, then calls the lazy shim in `zvic.main`.
"""

from __future__ import annotations

import os
import sys


def main():
    # add local src dir so `import zvic` resolves to workspace package
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    src_dir = os.path.join(repo_root, "src")
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

    import importlib
    import json
    import traceback

    # verify the target module importability first and report any exception
    try:
        importlib.import_module("cidstore.utils")
        print("cidstore.utils import OK")
    except Exception:
        print("cidstore.utils failed to import:")
        traceback.print_exc()

    import zvic

    # call the wrapper in zvic.main; default to dry-run so it is safe
    res = zvic.main.transform_replace("cidstore.utils", dry_run=True)
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
