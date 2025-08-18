import re

from .exception import SignatureIncompatible


def is_constraint_compatible(a_param, b_param):
    """
    Returns True if constraints are compatible, else raises SignatureIncompatible.
    Assumes a_param and b_param are parameter dicts from prepare_params.
    """
    a_con = a_param.get("constraint")
    b_con = b_param.get("constraint")
    # If B has no constraint, it's permissive (covers both neither-has and only-A-has cases)
    if not b_con:
        return
    # If only B has a constraint (A does not), this is NOT compatible (B is more restrictive)
    if not a_con:
        raise SignatureIncompatible(
            f"B adds constraint for parameter {a_param.get('name')}: {b_con}"
        )
    # If both have constraints, check if B is at least as permissive as A
    if a_con and b_con:
        # To check if B is at least as permissive as A, we need to check if (B(x) => A(x)) for all x.
        # That is, there should be no x such that B(x) is True and A(x) is False.
        # So, we generate a function that asserts B(x) and not A(x), and if CrossHair finds a counterexample, B is not as permissive as A.
        func_code = (
            "def _chk(x: int):\n"
            "    '''\n"
            "    pre: {b}\n"
            "    '''\n"
            "    assert not ({a})\n"
            "    return True\n"
        ).format(a=a_con.replace("_", "x"), b=b_con.replace("_", "x"))
        try:
            from .crosshair_subprocess import run_crosshair_on_code

            crosshair_result = run_crosshair_on_code(func_code, "_chk")
            if crosshair_result is None:
                # CrossHair could not check the function, fallback to numeric range comparison if possible
                # Try to match _ < N
                pat_simple = r"^_\s*<\s*(\d+)$"
                a_match = re.match(pat_simple, a_con.strip())
                b_match = re.match(pat_simple, b_con.strip())
                if a_match and b_match:
                    a_val = int(a_match.group(1))
                    b_val = int(b_match.group(1))
                    if b_val >= a_val:
                        return
                    else:
                        raise SignatureIncompatible(
                            f"Constraint mismatch for parameter {a_param.get('name')}: {a_con} vs {b_con} (B is narrower and thus incompatible: some inputs that A accepts will not be accepted by B)"
                        )
                # Try to match len(_) < N
                pat_len = r"^len\(_\)\s*<\s*(\d+)$"
                a_match = re.match(pat_len, a_con.strip())
                b_match = re.match(pat_len, b_con.strip())
                if a_match and b_match:
                    a_val = int(a_match.group(1))
                    b_val = int(b_match.group(1))
                    if b_val >= a_val:
                        return
                    else:
                        raise SignatureIncompatible(
                            f"Constraint mismatch for parameter {a_param.get('name')}: {a_con} vs {b_con} (B is narrower and thus incompatible: some inputs that A accepts will not be accepted by B)"
                        )
                # Fallback: if not a recognized pattern, require exact match
                if a_con != b_con:
                    raise SignatureIncompatible(
                        f"Constraint mismatch for parameter {a_param.get('name')}: {a_con} vs {b_con} (B is narrower and thus incompatible: some inputs that A accepts will not be accepted by B)"
                    )
                return
            if crosshair_result:
                # No counterexample found: B is at least as permissive as A
                return
            else:
                # Counterexample found: B is not as permissive as A
                raise SignatureIncompatible(
                    f"Constraint mismatch for parameter {a_param.get('name')}: {a_con} vs {b_con} (B is narrower and thus incompatible: some inputs that A accepts will not be accepted by B)"
                )
        except Exception as e:
            # Fallback: if CrossHair fails, try numeric range comparison

            pat = r"^_\s*<\s*(\d+)$"
            a_match = re.match(pat, a_con.strip())
            b_match = re.match(pat, b_con.strip())
            if a_match and b_match:
                a_val = int(a_match[1])
                b_val = int(b_match[1])
                if b_val >= a_val:
                    return True
                else:
                    raise SignatureIncompatible(
                        f"Constraint mismatch for parameter {a_param.get('name')}: {a_con} vs {b_con} (B is narrower and thus incompatible: some inputs that A accepts will not be accepted by B)"
                    ) from e
            # Fallback: if not a recognized pattern, require exact match
            if a_con != b_con:
                raise SignatureIncompatible(
                    f"Constraint mismatch for parameter {a_param.get('name')}: {a_con} vs {b_con} (B is narrower and thus incompatible: some inputs that A accepts will not be accepted by B)"
                ) from e
            return
