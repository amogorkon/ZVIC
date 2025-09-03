import json
import sys

print("START RUN_TEST")

# Import the module; sample_mod calls constrain_this_module() at import time
import sample_mod as sm

print("imported sample_mod:", sm)
print("sample_mod.foo id:", id(getattr(sm, "foo", None)))

# Keep a lingering reference by importing the function into local name
from sample_mod import foo as saved_foo

print("saved_foo id:", id(saved_foo))

# Now invoke the replace flow using the transform_replace helper
from zvic import replace_module

res = replace_module("sample_mod", force=True, dry_run=False)
print("replace_module result:")
print(json.dumps(res, indent=2))

# The replacement may install the new module under either 'sample_mod' or a
# package-qualified name. Check both keys and report what we find.
for key in ("sample_mod", "llm_playground.sample_mod"):
    m = sys.modules.get(key)
    print(f"sys.modules['{key}']:", m)
    if m is not None:
        print(f"  m.foo id: {id(getattr(m, 'foo', None))}")
        print(f"  saved_foo is m.foo? {saved_foo is getattr(m, 'foo', None)}")
    else:
        print("  (not present)")

print("END RUN_TEST")
