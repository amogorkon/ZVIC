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
    print(f"is_constraint_compatible DEBUG: a_param={a_param}, b_param={b_param}, a_con={a_con}, b_con={b_con}")
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
        func_code = (
            "import icontract\n"
            "@icontract.require(lambda x: {a})\n"
            "def _chk(x: int):\n"
            "    assert {b}\n"
            "    return True\n"
        ).format(a=a_con.replace('_', 'x'), b=b_con.replace('_', 'x'))
        print(f"is_constraint_compatible DEBUG: func_code=\n{func_code}")
        print(f"is_constraint_compatible DEBUG: func_code=\n{func_code}")
        try:
            from .crosshair_subprocess import run_crosshair_on_code
            crosshair_result = run_crosshair_on_code(func_code, '_chk')
            print(f"is_constraint_compatible DEBUG: crosshair_result={crosshair_result}")
            if crosshair_result:
                # No counterexample found: B is at least as permissive as A
                return True
            else:
                # Counterexample found: B is not as permissive as A
                raise SignatureIncompatible(
                    f"[ZV1001]: Constraint mismatch for parameter {a_param.get('name')}: {a_con} vs {b_con}\nSuggestions how to recover: ['Check parameter kinds (positional-only, PK, keyword-only) and their order per spec08.', 'Compare parameter names and required/optional status exactly as in the spec matrix.', 'For type errors, analyze if the types are compatible (subtype, union, optional, container).', 'For container types, check invariance/contravariance rules (e.g., list[int] vs list[str]).', 'For constraints, compare constraint expressions and ranges (C0a–C4).', 'If using an LLM, ask for a step-by-step explanation of the incompatibility and possible fixes.', 'Suggest concrete code changes to make B compatible with A, or vice versa, based on the spec08 scenario.', 'If unsure, output the full context and ask for a compatibility matrix walkthrough.']"
                )
        except Exception as e:
            print(f"is_constraint_compatible: subprocess crosshair failed: {e}")
            # Fallback: if CrossHair fails, fall back to string equality
            pass
        # Fallback: if CrossHair not available or fails, require exact match
        if a_con != b_con:
            raise SignatureIncompatible(
                f"Constraint mismatch for parameter {a_param.get('name')}: {a_con} vs {b_con}"
            )
        return True
    return True
