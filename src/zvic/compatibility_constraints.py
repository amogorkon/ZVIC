from crosshair.core_and_libs import analyze_function
from crosshair.statespace import AnalysisMessage

from .exception import SignatureIncompatible


def is_constraint_compatible(a_param, b_param):
    """
    Returns True if constraints are compatible, else raises SignatureIncompatible.
    Assumes a_param and b_param are parameter dicts from prepare_params.
    """
    a_con = a_param.get("constraint")
    b_con = b_param.get("constraint")
    # If neither has a constraint, compatible
    if not a_con and not b_con:
        return True
    # If only A has a constraint and B does not, this is compatible (B is more permissive)
    if a_con and not b_con:
        return True
    # If only B has a constraint, this is NOT compatible (B is more restrictive)
    if not a_con and b_con:
        raise SignatureIncompatible(
            f"B adds constraint for parameter {a_param.get('name')}: {b_con}"
        )
    # If both have constraints, check if B is at least as permissive as A
    if a_con and b_con:
        # Build a function that asserts A, then asserts NOT B (to check for counterexample)
        func_code = f"def _chk(x):\n    assert {a_con.replace('_', 'x')}\n    assert not ({b_con.replace('_', 'x')})\n    return True"
        localns = {}
        try:
            exec(func_code, {}, localns)
            func = localns["_chk"]
            # CrossHair: if it finds a counterexample, B is NOT as permissive as A
            msgs = list(
                analyze_function(func, AnalysisMessage.__bases__[0], options=None)
            )
            for msg in msgs:
                if msg.state == "ERROR":
                    raise SignatureIncompatible(
                        f"Constraint mismatch for parameter {a_param.get('name')}: {a_con} vs {b_con} (CrossHair found counterexample)"
                    )
            # If no counterexample found, B is at least as permissive as A
            return True
        except Exception:
            # Fallback: if CrossHair fails, fall back to string equality
            pass
        # Fallback: if CrossHair not available or fails, require exact match
        if a_con != b_con:
            raise SignatureIncompatible(
                f"Constraint mismatch for parameter {a_param.get('name')}: {a_con} vs {b_con}"
            )
        return True
    return True
