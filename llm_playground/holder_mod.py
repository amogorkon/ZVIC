from __future__ import annotations

# This module holds a reference to sample_mod.foo in an attribute named `held`.
# We'll use it to demonstrate patch_refs behavior: after replacing sample_mod,
# holder_mod.held should point to the new function when patch_refs=True.
import sample_mod

held = sample_mod.foo
