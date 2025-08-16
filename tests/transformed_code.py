from __future__ import annotations

from math import inf, nan

from crosshair.core_and_libs import AnalysisKind, AnalysisOptions, analyze_function

# print(constrain_this_module())


def implication_check(x: int, y: int):
    """
    pre: x > 30
    pre: 0 < y < x
    post: _ > 0
    """
    return x + y


msgs = list(analyze_function(implication_check))
options = AnalysisOptions(
    analysis_kind=(AnalysisKind.PEP316,),
    enabled=True,
    specs_complete=False,
    per_condition_timeout=inf,
    max_iterations=9223372036854775807,
    report_all=False,
    report_verbose=False,
    timeout=inf,
    per_path_timeout=nan,
    max_uninteresting_iterations=9223372036854775807,
    deadline=inf,
    stats=None,
)

# Run analysis
msgs = list(analyze_function(implication_check, options=options))
for msg in msgs:
    for m in msg.analyze():
        print(m.state)
