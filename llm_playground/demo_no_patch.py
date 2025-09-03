from __future__ import annotations

import importlib
import json
import sys

import zvic

# Fresh import
if "sample_mod" in sys.modules:
    del sys.modules["sample_mod"]
if "holder_mod" in sys.modules:
    del sys.modules["holder_mod"]

import holder_mod
import sample_mod

print("Demo: replace without patching")
print("Before replace:")
print("  holder_mod.held is sample_mod.foo?", holder_mod.held is sample_mod.foo)
print("  sample_mod.foo id", id(sample_mod.foo))
print("  holder_mod.held id", id(holder_mod.held))

res = zvic.replace_module("sample_mod", force=True, dry_run=False, patch_refs=False)
print(json.dumps(res, indent=2))
# Re-import installed module
sample_mod = importlib.import_module("sample_mod")
print("After replace (no patch):")
print("  holder_mod.held is sample_mod.foo?", holder_mod.held is sample_mod.foo)
print("  sample_mod.foo id", id(sample_mod.foo))
print("  holder_mod.held id", id(holder_mod.held))
