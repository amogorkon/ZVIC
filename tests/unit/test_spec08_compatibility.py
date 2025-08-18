# type: ignore


from pathlib import Path

import pytest

from zvic import load_module
from zvic.compatibility import is_compatible
from zvic.compatibility_params import SignatureIncompatible

stuff = Path(__file__).parent.parent / "stuff"

mod_a_path = stuff / "mod_a.py"
mod_b_path = stuff / "mod_b.py"

mod_a = load_module(mod_a_path, "mod_a")
mod_b = load_module(mod_b_path, "mod_b")


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
    ("C0a", True),
    ("C0b", True),
    ("C1", False),
    ("C2", True),
    ("C3", True),
    ("C4", False),
]


# Compatibility specification (stub: should be replaced with actual logic)

# Individual scenario tests generated from SCENARIOS


def test_P1():
    # Compatible: should not raise
    is_compatible(mod_a.P1, mod_b.P1)


def test_P2():
    # Incompatible: should raise
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.P2, mod_b.P2)


def test_P3():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.P3, mod_b.P3)


def test_P4():
    is_compatible(mod_a.P4, mod_b.P4)


def test_P5():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.P5, mod_b.P5)


def test_P6():
    is_compatible(mod_a.P6, mod_b.P6)


def test_P7():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.P7, mod_b.P7)


def test_PK1():
    is_compatible(mod_a.PK1, mod_b.PK1)


def test_PK2():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.PK2, mod_b.PK2)


def test_PK3():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.PK3, mod_b.PK3)


def test_PK4():
    is_compatible(mod_a.PK4, mod_b.PK4)


def test_PK5():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.PK5, mod_b.PK5)


def test_PK6():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.PK6, mod_b.PK6)


def test_PK7():
    is_compatible(mod_a.PK7, mod_b.PK7)


def test_PK8():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.PK8, mod_b.PK8)


def test_PK9():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.PK9, mod_b.PK9)


def test_K1():
    is_compatible(mod_a.K1, mod_b.K1)


def test_K2():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.K2, mod_b.K2)


def test_K3():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.K3, mod_b.K3)


def test_K4():
    is_compatible(mod_a.K4, mod_b.K4)


def test_K5():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.K5, mod_b.K5)


def test_K6():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.K6, mod_b.K6)


def test_K7():
    is_compatible(mod_a.K7, mod_b.K7)


def test_K8():
    is_compatible(mod_a.K8, mod_b.K8)


def test_K9():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.K9, mod_b.K9)


def test_AP1():
    is_compatible(mod_a.AP1, mod_b.AP1)


def test_AP2():
    is_compatible(mod_a.AP2, mod_b.AP2)


def test_AP3():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.AP3, mod_b.AP3)


def test_AP4():
    is_compatible(mod_a.AP4, mod_b.AP4)


def test_AP5():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.AP5, mod_b.AP5)


def test_AP6():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.AP6, mod_b.AP6)


def test_AP7():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.AP7, mod_b.AP7)


def test_AP8():
    is_compatible(mod_a.AP8, mod_b.AP8)


def test_AP9():
    is_compatible(mod_a.AP9, mod_b.AP9)


def test_AP10():
    is_compatible(mod_a.AP10, mod_b.AP10)


def test_AP11():
    is_compatible(mod_a.AP11, mod_b.AP11)


def test_APK1():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.APK1, mod_b.APK1)


def test_APK2():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.APK2, mod_b.APK2)


def test_APK3():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.APK3, mod_b.APK3)


def test_APK4():
    is_compatible(mod_a.APK4, mod_b.APK4)


def test_APK5():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.APK5, mod_b.APK5)


def test_APK6():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.APK6, mod_b.APK6)


def test_APK7():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.APK7, mod_b.APK7)


def test_APK8():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.APK8, mod_b.APK8)


def test_AK1():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.AK1, mod_b.AK1)


def test_AK2():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.AK2, mod_b.AK2)


def test_AK3():
    is_compatible(mod_a.AK3, mod_b.AK3)


def test_AK4():
    is_compatible(mod_a.AK4, mod_b.AK4)


def test_AK5():
    is_compatible(mod_a.AK5, mod_b.AK5)


def test_AK6():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.AK6, mod_b.AK6)


def test_AK7():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.AK7, mod_b.AK7)


def test_AK8():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.AK8, mod_b.AK8)


def test_T0():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.T0, mod_b.T0)


def test_T1():
    is_compatible(mod_a.T1, mod_b.T1)


def test_T2():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.T2, mod_b.T2)


def test_T3():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.T3, mod_b.T3)


def test_T4():
    is_compatible(mod_a.T4, mod_b.T4)


def test_T5():
    is_compatible(mod_a.T5, mod_b.T5)


def test_T6():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.T6, mod_b.T6)


def test_T7():
    is_compatible(mod_a.T7, mod_b.T7)


def test_T8():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.T8, mod_b.T8)


def test_T9():
    is_compatible(mod_a.T9, mod_b.T9)


def test_T10():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.T10, mod_b.T10)


def test_T11():
    is_compatible(mod_a.T11, mod_b.T11)


def test_C0a():
    is_compatible(mod_a.C0a, mod_b.C0a)


def test_C0b():
    is_compatible(mod_a.C0b, mod_b.C0b)


def test_C1():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.C1, mod_b.C1)


def test_C2():
    is_compatible(mod_a.C2, mod_b.C2)


def test_C3():
    is_compatible(mod_a.C3, mod_b.C3)


def test_C4():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.C4, mod_b.C4)


# --- Additional Mixed Tests ---
def test_X1():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.X1, mod_b.X1)


def test_X2():
    is_compatible(mod_a.X2, mod_b.X2)


def test_snail():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.Snail, mod_b.Snail)


def test_bird():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.Bird, mod_b.Bird)


def test_bird2():
    is_compatible(mod_a.Bird2, mod_b.Bird2)


def test_noodle():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.Noodle, mod_b.Noodle)


def test_M1():
    mod_a_path = stuff / "mod_a_M1.py"
    mod_b_path = stuff / "mod_b_M1.py"

    mod_a = load_module(mod_a_path, "mod_a")
    mod_b = load_module(mod_b_path, "mod_b")

    is_compatible(mod_a, mod_b)


def test_M2():
    mod_a_path = stuff / "mod_a_M2.py"
    mod_b_path = stuff / "mod_b_M2.py"

    mod_a = load_module(mod_a_path, "mod_a")
    mod_b = load_module(mod_b_path, "mod_b")

    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a, mod_b)


def test_M3():
    mod_a_path = stuff / "mod_a_M3.py"
    mod_b_path = stuff / "mod_b_M3.py"

    mod_a = load_module(mod_a_path, "mod_a")
    mod_b = load_module(mod_b_path, "mod_b")

    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a, mod_b)


def test_M4():
    mod_a_path = stuff / "mod_a_M4.py"
    mod_b_path = stuff / "mod_b_M4.py"

    mod_a = load_module(mod_a_path, "mod_a")
    mod_b = load_module(mod_b_path, "mod_b")

    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a, mod_b)


def test_M5_constant():
    mod_a_path = stuff / "mod_a_M5.py"
    mod_b_path = stuff / "mod_b_M5_constant.py"

    mod_a = load_module(mod_a_path, "mod_a")
    mod_b = load_module(mod_b_path, "mod_b")

    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a, mod_b)


def test_M5_class():
    mod_a_path = stuff / "mod_a_M5.py"
    mod_b_path = stuff / "mod_b_M5_class.py"

    mod_a = load_module(mod_a_path, "mod_a")
    mod_b = load_module(mod_b_path, "mod_b")

    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a, mod_b)


def test_M6():
    mod_a_path = stuff / "mod_a_M5.py"
    mod_b_path = stuff / "mod_b_M5_private.py"

    mod_a = load_module(mod_a_path, "mod_a")
    mod_b = load_module(mod_b_path, "mod_b")

    is_compatible(mod_a, mod_b)


def test_M7_add():
    mod_a_path = stuff / "mod_a_M7.py"
    mod_b_path = stuff / "mod_b_M7_add.py"

    mod_a = load_module(mod_a_path, "mod_a")
    mod_b = load_module(mod_b_path, "mod_b")

    is_compatible(mod_a, mod_b)


def test_M7_del():
    mod_a_path = stuff / "mod_a_M7.py"
    mod_b_path = stuff / "mod_b_M7_del.py"

    mod_a = load_module(mod_a_path, "mod_a")
    mod_b = load_module(mod_b_path, "mod_b")

    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a, mod_b)


def test_M8():
    mod_a_path = stuff / "mod_a_M8.py"
    mod_b_path = stuff / "mod_b_M8_add.py"

    mod_a = load_module(mod_a_path, "mod_a")
    mod_b = load_module(mod_b_path, "mod_b")

    is_compatible(mod_a, mod_b)


def test_M9():
    mod_a_path = stuff / "mod_a_M8.py"
    mod_b_path = stuff / "mod_b_M8_del.py"

    mod_a = load_module(mod_a_path, "mod_a")
    mod_b = load_module(mod_b_path, "mod_b")

    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a, mod_b)


def test_M10():
    mod_a_path = stuff / "mod_a_M8.py"
    mod_b_path = stuff / "mod_b_M8_reorder.py"

    mod_a = load_module(mod_a_path, "mod_a")
    mod_b = load_module(mod_b_path, "mod_b")

    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a, mod_b)
