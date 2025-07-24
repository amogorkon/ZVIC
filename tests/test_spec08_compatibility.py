# type: ignore

import importlib
from inspect import signature
from pathlib import Path

import pytest

from zvic.compatibility import is_signature_compatible
from zvic.compatibility_params import SignatureIncompatible

mod_a_path = Path(__file__).parent / "stuff" / "mod_a.py"
mod_b_path = Path(__file__).parent / "stuff" / "mod_b.py"

spec_a = importlib.util.spec_from_file_location("mod_a", mod_a_path)
mod_a = importlib.util.module_from_spec(spec_a)
spec_a.loader.exec_module(mod_a)

spec_b = importlib.util.spec_from_file_location("mod_b", mod_b_path)
mod_b = importlib.util.module_from_spec(spec_b)
spec_b.loader.exec_module(mod_b)


# List of scenarios: (ID, expected_compatibility)
SCENARIOS = [
    ("P1", True),
    ("P2", False),
    ("P3", False),
    ("P4", True),
    ("P5", False),
    ("P6", True),
    ("P7", False),
    ("PK1", True),
    ("PK2", False),
    ("PK3", False),
    ("PK4", True),
    ("PK5", False),
    ("PK6", False),
    ("PK7", True),
    ("PK8", False),
    ("PK9", False),
    ("K1", True),
    ("K2", False),
    ("K3", False),
    ("K4", True),
    ("K5", False),
    ("K6", False),
    ("K7", True),
    ("K8", True),
    ("K9", False),
    ("AP1", True),
    ("AP2", True),
    ("AP3", False),
    ("AP4", True),
    ("AP5", False),
    ("AP6", False),
    ("AP7", False),
    ("AP8", True),
    ("AP9", True),
    ("AP10", True),
    ("AP11", True),
    ("APK1", False),
    ("APK2", False),
    ("APK3", False),
    ("APK4", True),
    ("APK5", False),
    ("APK6", False),
    ("APK7", False),
    ("APK8", False),
    ("AK1", False),
    ("AK2", False),
    ("AK3", True),
    ("AK4", True),
    ("AK5", True),
    ("AK6", False),
    ("AK7", False),
    ("AK8", False),
    ("T0", False),
    ("T1", True),
    ("T2", False),
    ("T3", False),
    ("T4", True),
    ("T5", True),
    ("T6", False),
    ("T7", True),
    ("T8", False),
    ("T9", True),
    ("T10", False),
    ("T11", True),
    # ("C0a", True),
    # ("C0b", True),
    # ("C1", False),
    # ("C2", True),
    # ("C3", True),
    # ("C4", False),
]


# Compatibility specification (stub: should be replaced with actual logic)

# Individual scenario tests generated from SCENARIOS


def test_P1():
    a = signature(mod_a.P1)
    b = signature(mod_b.P1)
    # Compatible: should not raise
    is_signature_compatible(a, b)


def test_P2():
    a = signature(mod_a.P2)
    b = signature(mod_b.P2)
    # Incompatible: should raise
    with pytest.raises(SignatureIncompatible):
        is_signature_compatible(a, b)


def test_P3():
    a = signature(mod_a.P3)
    b = signature(mod_b.P3)
    with pytest.raises(SignatureIncompatible):
        is_signature_compatible(a, b)


def test_P4():
    a = signature(mod_a.P4)
    b = signature(mod_b.P4)
    is_signature_compatible(a, b)


def test_P5():
    a = signature(mod_a.P5)
    b = signature(mod_b.P5)
    with pytest.raises(SignatureIncompatible):
        is_signature_compatible(a, b)


def test_P6():
    a = signature(mod_a.P6)
    b = signature(mod_b.P6)
    is_signature_compatible(a, b)


def test_P7():
    a = signature(mod_a.P7)
    b = signature(mod_b.P7)
    with pytest.raises(SignatureIncompatible):
        is_signature_compatible(a, b)


def test_PK1():
    a = signature(mod_a.PK1)
    b = signature(mod_b.PK1)
    is_signature_compatible(a, b)


def test_PK2():
    a = signature(mod_a.PK2)
    b = signature(mod_b.PK2)
    with pytest.raises(SignatureIncompatible):
        is_signature_compatible(a, b)


def test_PK3():
    a = signature(mod_a.PK3)
    b = signature(mod_b.PK3)
    with pytest.raises(SignatureIncompatible):
        is_signature_compatible(a, b)


def test_PK4():
    a = signature(mod_a.PK4)
    b = signature(mod_b.PK4)
    is_signature_compatible(a, b)


def test_PK5():
    a = signature(mod_a.PK5)
    b = signature(mod_b.PK5)
    with pytest.raises(SignatureIncompatible):
        is_signature_compatible(a, b)


def test_PK6():
    a = signature(mod_a.PK6)
    b = signature(mod_b.PK6)
    with pytest.raises(SignatureIncompatible):
        is_signature_compatible(a, b)


def test_PK7():
    a = signature(mod_a.PK7)
    b = signature(mod_b.PK7)
    is_signature_compatible(a, b)


def test_PK8():
    a = signature(mod_a.PK8)
    b = signature(mod_b.PK8)
    with pytest.raises(SignatureIncompatible):
        is_signature_compatible(a, b)


def test_PK9():
    a = signature(mod_a.PK9)
    b = signature(mod_b.PK9)
    with pytest.raises(SignatureIncompatible):
        is_signature_compatible(a, b)


def test_K1():
    a = signature(mod_a.K1)
    b = signature(mod_b.K1)
    is_signature_compatible(a, b)


def test_K2():
    a = signature(mod_a.K2)
    b = signature(mod_b.K2)
    with pytest.raises(SignatureIncompatible):
        is_signature_compatible(a, b)


def test_K3():
    a = signature(mod_a.K3)
    b = signature(mod_b.K3)
    with pytest.raises(SignatureIncompatible):
        is_signature_compatible(a, b)


def test_K4():
    a = signature(mod_a.K4)
    b = signature(mod_b.K4)
    is_signature_compatible(a, b)


def test_K5():
    a = signature(mod_a.K5)
    b = signature(mod_b.K5)
    with pytest.raises(SignatureIncompatible):
        is_signature_compatible(a, b)


def test_K6():
    a = signature(mod_a.K6)
    b = signature(mod_b.K6)
    with pytest.raises(SignatureIncompatible):
        is_signature_compatible(a, b)


def test_K7():
    a = signature(mod_a.K7)
    b = signature(mod_b.K7)
    is_signature_compatible(a, b)


def test_K8():
    a = signature(mod_a.K8)
    b = signature(mod_b.K8)
    is_signature_compatible(a, b)


def test_K9():
    a = signature(mod_a.K9)
    b = signature(mod_b.K9)
    with pytest.raises(SignatureIncompatible):
        is_signature_compatible(a, b)


def test_AP1():
    a = signature(mod_a.AP1)
    b = signature(mod_b.AP1)
    is_signature_compatible(a, b)


def test_AP2():
    a = signature(mod_a.AP2)
    b = signature(mod_b.AP2)
    is_signature_compatible(a, b)


def test_AP3():
    a = signature(mod_a.AP3)
    b = signature(mod_b.AP3)
    with pytest.raises(SignatureIncompatible):
        is_signature_compatible(a, b)


def test_AP4():
    a = signature(mod_a.AP4)
    b = signature(mod_b.AP4)
    is_signature_compatible(a, b)


def test_AP5():
    a = signature(mod_a.AP5)
    b = signature(mod_b.AP5)
    with pytest.raises(SignatureIncompatible):
        is_signature_compatible(a, b)


def test_AP6():
    a = signature(mod_a.AP6)
    b = signature(mod_b.AP6)
    with pytest.raises(SignatureIncompatible):
        is_signature_compatible(a, b)


def test_AP7():
    a = signature(mod_a.AP7)
    b = signature(mod_b.AP7)
    with pytest.raises(SignatureIncompatible):
        is_signature_compatible(a, b)


def test_AP8():
    a = signature(mod_a.AP8)
    b = signature(mod_b.AP8)
    is_signature_compatible(a, b)


def test_AP9():
    a = signature(mod_a.AP9)
    b = signature(mod_b.AP9)
    is_signature_compatible(a, b)


def test_AP10():
    a = signature(mod_a.AP10)
    b = signature(mod_b.AP10)
    is_signature_compatible(a, b)


def test_AP11():
    a = signature(mod_a.AP11)
    b = signature(mod_b.AP11)
    is_signature_compatible(a, b)


def test_APK1():
    a = signature(mod_a.APK1)
    b = signature(mod_b.APK1)
    with pytest.raises(SignatureIncompatible):
        is_signature_compatible(a, b)


def test_APK2():
    a = signature(mod_a.APK2)
    b = signature(mod_b.APK2)
    with pytest.raises(SignatureIncompatible):
        is_signature_compatible(a, b)


def test_APK3():
    a = signature(mod_a.APK3)
    b = signature(mod_b.APK3)
    with pytest.raises(SignatureIncompatible):
        is_signature_compatible(a, b)


def test_APK4():
    a = signature(mod_a.APK4)
    b = signature(mod_b.APK4)
    is_signature_compatible(a, b)


def test_APK5():
    a = signature(mod_a.APK5)
    b = signature(mod_b.APK5)
    with pytest.raises(SignatureIncompatible):
        is_signature_compatible(a, b)


def test_APK6():
    a = signature(mod_a.APK6)
    b = signature(mod_b.APK6)
    with pytest.raises(SignatureIncompatible):
        is_signature_compatible(a, b)


def test_APK7():
    a = signature(mod_a.APK7)
    b = signature(mod_b.APK7)
    with pytest.raises(SignatureIncompatible):
        is_signature_compatible(a, b)


def test_APK8():
    a = signature(mod_a.APK8)
    b = signature(mod_b.APK8)
    with pytest.raises(SignatureIncompatible):
        is_signature_compatible(a, b)


def test_AK1():
    a = signature(mod_a.AK1)
    b = signature(mod_b.AK1)
    with pytest.raises(SignatureIncompatible):
        is_signature_compatible(a, b)


def test_AK2():
    a = signature(mod_a.AK2)
    b = signature(mod_b.AK2)
    with pytest.raises(SignatureIncompatible):
        is_signature_compatible(a, b)


def test_AK3():
    a = signature(mod_a.AK3)
    b = signature(mod_b.AK3)
    is_signature_compatible(a, b)


def test_AK4():
    a = signature(mod_a.AK4)
    b = signature(mod_b.AK4)
    is_signature_compatible(a, b)


def test_AK5():
    a = signature(mod_a.AK5)
    b = signature(mod_b.AK5)
    is_signature_compatible(a, b)


def test_AK6():
    a = signature(mod_a.AK6)
    b = signature(mod_b.AK6)
    with pytest.raises(SignatureIncompatible):
        is_signature_compatible(a, b)


def test_AK7():
    a = signature(mod_a.AK7)
    b = signature(mod_b.AK7)
    with pytest.raises(SignatureIncompatible):
        is_signature_compatible(a, b)


def test_AK8():
    a = signature(mod_a.AK8)
    b = signature(mod_b.AK8)
    with pytest.raises(SignatureIncompatible):
        is_signature_compatible(a, b)


def test_T0():
    a = signature(mod_a.T0)
    b = signature(mod_b.T0)
    with pytest.raises(SignatureIncompatible):
        is_signature_compatible(a, b)


def test_T1():
    a = signature(mod_a.T1)
    b = signature(mod_b.T1)
    is_signature_compatible(a, b)


def test_T2():
    a = signature(mod_a.T2)
    b = signature(mod_b.T2)
    with pytest.raises(SignatureIncompatible):
        is_signature_compatible(a, b)


def test_T3():
    a = signature(mod_a.T3)
    b = signature(mod_b.T3)
    with pytest.raises(SignatureIncompatible):
        is_signature_compatible(a, b)


def test_T4():
    a = signature(mod_a.T4)
    b = signature(mod_b.T4)
    is_signature_compatible(a, b)


def test_T5():
    a = signature(mod_a.T5)
    b = signature(mod_b.T5)
    is_signature_compatible(a, b)


def test_T6():
    a = signature(mod_a.T6)
    b = signature(mod_b.T6)
    with pytest.raises(SignatureIncompatible):
        is_signature_compatible(a, b)


def test_T7():
    a = signature(mod_a.T7)
    b = signature(mod_b.T7)
    is_signature_compatible(a, b)


def test_T8():
    a = signature(mod_a.T8)
    b = signature(mod_b.T8)
    with pytest.raises(SignatureIncompatible):
        is_signature_compatible(a, b)


def test_T9():
    a = signature(mod_a.T9)
    b = signature(mod_b.T9)
    is_signature_compatible(a, b)


def test_T10():
    a = signature(mod_a.T10)
    b = signature(mod_b.T10)
    with pytest.raises(SignatureIncompatible):
        is_signature_compatible(a, b)


def test_T11():
    a = signature(mod_a.T11)
    b = signature(mod_b.T11)
    is_signature_compatible(a, b)
