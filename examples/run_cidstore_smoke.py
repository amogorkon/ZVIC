from pathlib import Path
import sys

# Ensure local zvic and cidstore sources are importable
sys.path.insert(0, r"e:\Dropbox\code\ZVIC\src")
sys.path.insert(0, r"e:\Dropbox\code\cidstore\src")

from zvic import load_module, canonicalize

p = Path(r"e:\Dropbox\code\cidstore\src\cidstore\utils.py")
print('Loading', p)
mod = load_module(p, "cidstore_utils_test")
print('Module loaded:', mod)
print('Module name:', mod.__name__)

can = canonicalize(mod)
print('Canonical representation:')
import pprint
pprint.pprint(can)

# If function exists, print its canonical signature
if hasattr(mod, 'assumption'):
    print('\nassumption signature:')
    pprint.pprint(canonicalize(mod.assumption))
else:
    print('\nassumption not present in transformed module')
