# TDD tests: known to fail, for unimplemented features


import pytest

from zvic import canonical_signature, is_signature_compatible


@pytest.mark.xfail(reason="Feature not implemented: canonical_signature")
def test_canonical_signature(mod_a):
    sig = canonical_signature(mod_a.foo)
    assert isinstance(sig, dict)


@pytest.mark.xfail(reason="Feature not implemented: signature_compatibility_check")
def test_signature_compatibility(mod_a, mod_b):
    assert is_signature_compatible(mod_a.foo, mod_b.foo)


@pytest.mark.xfail(reason="Feature not implemented: signature_incompatibility_check")
def test_signature_incompatibility(mod_a, mod_c):
    assert not is_signature_compatible(mod_a.foo, mod_c.foo)
