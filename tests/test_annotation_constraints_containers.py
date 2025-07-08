import textwrap
from zvic.annotation_constraints import apply_annotation_constraints


def test_list_length_and_item_constraint():
    src = textwrap.dedent("""
    def foo(x: list[int(0 < _ < 100)](len(_) == 3)) -> None:
        pass
    """)
    out = apply_annotation_constraints(src)
    # Outer constraint on list length, inner on int range
    assert (
        'Annotated[list[Annotated[int, "0 < _ < 100"]], "len(x) == 3"]' in out
        or "Annotated[list[Annotated[int, '0 < _ < 100']], 'len(x) == 3']" in out
    )
    assert "from typing import Annotated" in out
