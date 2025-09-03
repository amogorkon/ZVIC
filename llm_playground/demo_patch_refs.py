from __future__ import annotations

import importlib
import json
import sys

# Import the helper from zvic
import zvic

# Ensure sample_mod is imported fresh
if "sample_mod" in sys.modules:
    del sys.modules["sample_mod"]

import holder_mod
import sample_mod

print("Before replace:")
print("  holder_mod.held is sample_mod.foo?", holder_mod.held is sample_mod.foo)
print("  sample_mod.foo id", id(sample_mod.foo))
print("  holder_mod.held id", id(holder_mod.held))

print("\nDoing replace with patch_refs=False (dry_run=False):")
res = zvic.replace_module("sample_mod", force=True, dry_run=False, patch_refs=False)
print(json.dumps(res, indent=2))
# Re-import the module object from sys.modules to reflect the installed module
try:
    sample_mod = importlib.import_module("sample_mod")
except Exception:
    sample_mod = None
print("After replace (no patch):")
print("  holder_mod.held is sample_mod.foo?", holder_mod.held is sample_mod.foo)
print("  sample_mod.foo id", id(sample_mod.foo))
print("  holder_mod.held id", id(holder_mod.held))

print("\nNow replace with patch_refs=True:")
res2 = zvic.replace_module("sample_mod", force=True, dry_run=False, patch_refs=True)
print(json.dumps(res2, indent=2))
# Re-import to reflect any change
try:
    sample_mod = importlib.import_module("sample_mod")
except Exception:
    sample_mod = None
print("After replace (with patch):")
print("  holder_mod.held is sample_mod.foo?", holder_mod.held is sample_mod.foo)
print("  sample_mod.foo id", id(sample_mod.foo))
print("  holder_mod.held id", id(holder_mod.held))
