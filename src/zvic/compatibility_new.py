from inspect import Signature

from .exception import SignatureIncompatible
from .utils import Scenario, prepare_params, prepare_scenario


def is_signature_compatible(a_sig: Signature, b_sig: Signature) -> bool:
    """
    Compatibility logic using match/case for parameter kind scenarios.
    """
    a = prepare_params(a_sig)
    b = prepare_params(b_sig)
    scenario = prepare_scenario(a, a_sig, b, b_sig)
    print("DEBUG scenario tuple:", scenario)

    match scenario:
        # |PK5| Fewer required PK args in B | A(a, b) -> B(a) | ✗
        case Scenario(
            a_pos_or_kw_required=a_req,
            b_pos_or_kw_required=b_req,
            b_has_varargs=False,
            b_has_varkw=False,
        ) if b_req < a_req:
            raise SignatureIncompatible(
                message="B has fewer required positional-or-keyword parameters than A",
                context={"A": str(a_sig), "B": str(b_sig)},
            )

        # |PK6| B has fewer total PK parameters than A | A(a, b, c=1) -> B(a, b) | ✗
        case Scenario(
            a_pos_or_kw=a_total,
            b_pos_or_kw=b_total,
            b_has_varargs=False,
            b_has_varkw=False,
        ) if b_total < a_total:
            raise SignatureIncompatible(
                message="B has fewer total positional-or-keyword parameters than A",
                context={"A": str(a_sig), "B": str(b_sig)},
            )
        # BLACKLIST: explicitely incompatible scenarios
        # | P2| Additional required args in B             | A(a, b,/) -> B(x, y, z,/) | ✗
        case Scenario(
            a_posonly_required=a_po,
            a_pos_or_kw_required=a_pk,
            a_kwonly_required=a_ko,
            b_posonly_required=b_po,
            b_pos_or_kw_required=b_pk,
            b_kwonly_required=b_ko,
        ) if (b_po + b_pk + b_ko) > (a_po + a_pk + a_ko):
            print(
                f"DEBUG: Global required param check failed: a_required={a_po + a_pk + a_ko}, b_required={b_po + b_pk + b_ko}"
            )
            raise SignatureIncompatible(
                message="B has more required parameters than A",
                context={"A": str(a_sig), "B": str(b_sig)},
            )

        # | P3| Fewer required args in B, but no optional to compensate | A(a,b,/) -> B(x,/)        | ✗
        case Scenario(
            a_posonly_required=a_req,
            b_posonly_required=b_req,
            a_posonly=a_total,
            b_posonly=b_total,
            b_has_varargs=False,
            b_has_varkw=False,
        ) if b_req < a_req and b_total <= a_total:
            raise SignatureIncompatible(
                message="B has fewer required positional-only parameters than A",
                context={"A": str(a_sig), "B": str(b_sig)},
            )

        # | P5| Fewer optional args in B                  | A(a,b=1,/) -> B(x,/)      | ✗
        case Scenario(
            a_posonly_required=a_req,
            a_posonly=a_total,
            b_posonly_required=b_req,
            b_posonly=b_total,
            b_has_varargs=False,
            b_has_varkw=False,
        ) if (b_total - b_req) < (a_total - a_req):
            raise SignatureIncompatible(
                message="B has fewer optional positional-only parameters than A",
                context={"A": str(a_sig), "B": str(b_sig)},
            )

        # |PK2| and |K2|: Same count, different names (PK or KW)
        case Scenario(
            a_pos_or_kw_required=a_pk_req,
            a_pos_or_kw=a_pk_total,
            b_pos_or_kw_required=b_pk_req,
            b_pos_or_kw=b_pk_total,
            a_kwonly_required=a_ko_req,
            a_kwonly=a_ko_total,
            b_kwonly_required=b_ko_req,
            b_kwonly=b_ko_total,
            b_has_varargs=False,
            b_has_varkw=False,
        ):
            # PK: same count, different names
            if a_pk_total == b_pk_total and a_pk_req == b_pk_req and a_pk_total > 0:
                a_names = [p["name"] for p in prepare_params(a_sig).pos_or_kw]
                b_names = [p["name"] for p in prepare_params(b_sig).pos_or_kw]
                if a_names != b_names:
                    raise SignatureIncompatible(
                        message="PK parameter names differ",
                        context={"A": str(a_sig), "B": str(b_sig)},
                    )
            # KW: same count, different names
            if a_ko_total == b_ko_total and a_ko_req == b_ko_req and a_ko_total > 0:
                a_names = sorted(p["name"] for p in prepare_params(a_sig).kwonly)
                b_names = sorted(p["name"] for p in prepare_params(b_sig).kwonly)
                if a_names != b_names:
                    raise SignatureIncompatible(
                        message="Keyword-only parameter names differ",
                        context={"A": str(a_sig), "B": str(b_sig)},
                    )

        # |K6| B has fewer total keyword-only parameters than A
        case Scenario(
            a_kwonly=a_total,
            b_kwonly=b_total,
            b_has_varargs=False,
            b_has_varkw=False,
        ) if b_total < a_total:
            raise SignatureIncompatible(
                message="B has fewer total keyword-only parameters than A",
                context={"A": str(a_sig), "B": str(b_sig)},
            )

        # PK6: B has fewer total PK parameters than A
        case Scenario(
            a_pos_or_kw=a_total,
            b_pos_or_kw=b_total,
            b_has_varargs=False,
            b_has_varkw=False,
        ) if b_total < a_total:
            raise SignatureIncompatible(
                message="B has fewer total positional-or-keyword parameters than A",
                context={"A": str(a_sig), "B": str(b_sig)},
            )

        # PK, B has fewer required
        case Scenario(
            a_pos_or_kw_required=a_req,
            b_pos_or_kw_required=b_req,
            b_has_varargs=False,
            b_has_varkw=False,
        ) if b_req < a_req:
            raise SignatureIncompatible(
                message="B has fewer required positional-or-keyword parameters than A",
                context={"A": str(a_sig), "B": str(b_sig)},
            )

        # PK, B has fewer optional
        case Scenario(
            a_pos_or_kw_required=a_req,
            a_pos_or_kw=a_total,
            b_pos_or_kw_required=b_req,
            b_pos_or_kw=b_total,
            b_has_varargs=False,
            b_has_varkw=False,
        ) if (b_total - b_req) < (a_total - a_req):
            raise SignatureIncompatible(
                message="B has fewer optional positional-or-keyword parameters than A",
                context={"A": str(a_sig), "B": str(b_sig)},
            )

        # |K5| Fewer required args in B                  | A(*, a, b) -> B(*, a)         | ✗
        case Scenario(
            a_kwonly_required=a_req,
            a_kwonly=a_total,
            b_kwonly_required=b_req,
            b_kwonly=b_total,
            b_has_varargs=False,
            b_has_varkw=False,
        ) if b_req < a_req and b_total < a_total:
            raise SignatureIncompatible(
                message="B has fewer optional keyword-only parameters than A",
                context={"A": str(a_sig), "B": str(b_sig)},
            )

        # WHITELIST - these are explicitely compatible scenarios

        # XP1: Positional-only for both, same required and total
        case Scenario(
            a_posonly_required=a_req,
            a_posonly=a_total,
            b_posonly_required=b_req,
            b_posonly=b_total,
            b_has_varargs=False,
            b_has_varkw=False,
        ) if a_req == b_req and a_total == b_total:
            return True

        # KW, B has more optional
        case Scenario(
            a_kwonly_required=a_req,
            a_kwonly=a_total,
            b_kwonly_required=b_req,
            b_kwonly=b_total,
            b_has_varargs=False,
            b_has_varkw=False,
        ) if (b_total - b_req) > (a_total - a_req):
            return True

        # Positional-only, B has more optional (P4, compatible)
        case Scenario(
            a_posonly_required=a_req,
            a_posonly=a_total,
            b_posonly_required=b_req,
            b_posonly=b_total,
            b_has_varargs=False,
            b_has_varkw=False,
        ) if b_total > a_total and b_req <= a_req:
            return True

        # Positional-only for both, same required and total (P1, compatible)
        case Scenario(
            a_posonly_required=a_req,
            a_posonly=a_total,
            b_posonly_required=b_req,
            b_posonly=b_total,
            b_has_varargs=False,
            b_has_varkw=False,
        ) if a_req == b_req and a_total == b_total:
            return True

        # PK, B has more optional
        case Scenario(
            a_pos_or_kw_required=a_req,
            a_pos_or_kw=a_total,
            b_pos_or_kw_required=b_req,
            b_pos_or_kw=b_total,
            b_has_varargs=False,
            b_has_varkw=False,
        ) if (b_total - b_req) > (a_total - a_req):
            return True

        # KW, B has more optional
        case Scenario(
            a_kwonly_required=a_req,
            a_kwonly=a_total,
            b_kwonly_required=b_req,
            b_kwonly=b_total,
            b_has_varargs=False,
            b_has_varkw=False,
        ) if (b_total - b_req) > (a_total - a_req):
            return True

        # B is empty
        case Scenario(
            b_posonly_required=0,
            b_posonly=0,
            b_pos_or_kw_required=0,
            b_pos_or_kw=0,
            b_kwonly_required=0,
            b_kwonly=0,
            b_has_varargs=False,
            b_has_varkw=False,
        ):
            return True

        # PK, B has more optional
        case Scenario(
            a_pos_or_kw_required=a_req,
            a_pos_or_kw=a_total,
            b_pos_or_kw_required=b_req,
            b_pos_or_kw=b_total,
            b_has_varargs=False,
            b_has_varkw=False,
        ) if (b_total - b_req) > (a_total - a_req):
            return True

        # Fallback
        case _:
            raise AssertionError("Unhandled Scenario??")
    return False
