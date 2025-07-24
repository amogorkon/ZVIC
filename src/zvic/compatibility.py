from .compatibility_constraints import is_constraint_compatible
from .compatibility_params import are_params_compatible
from .compatibility_types import is_type_compatible
from .utils import prepare_params


def is_signature_compatible(a_sig, b_sig):
    are_params_compatible(a_sig, b_sig)
    # 2. Type compatibility: zip through positional and keyword-only params

    a_params = prepare_params(a_sig)
    b_params = prepare_params(b_sig)

    # Check positional-only
    for a_p, b_p in zip(a_params.posonly, b_params.posonly):
        is_type_compatible(a_p["type"], b_p["type"])
        is_constraint_compatible(a_p, b_p)

    # Check positional-or-keyword
    for a_p, b_p in zip(a_params.pos_or_kw, b_params.pos_or_kw):
        is_type_compatible(a_p["type"], b_p["type"])
        is_constraint_compatible(a_p, b_p)

    # Check keyword-only
    for a_p, b_p in zip(a_params.kwonly, b_params.kwonly):
        is_type_compatible(a_p["type"], b_p["type"])
        is_constraint_compatible(a_p, b_p)

    return True
