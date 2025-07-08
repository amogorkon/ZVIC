# TDD tests: known to fail, for unimplemented features


from zvic import canonicalize, is_compatible


def test_canonical_signature(mod_a):
    sig = canonicalize(mod_a.foo)
    assert isinstance(sig, dict)


def test_signature_compatibility(mod_a, mod_b):
    assert is_compatible(mod_a.foo, mod_b.foo)


def test_signature_incompatibility(mod_a, mod_c):
    assert not is_compatible(mod_a.foo, mod_c.foo)
