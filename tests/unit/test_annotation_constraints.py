import textwrap

from zvic.annotation_constraints import apply_annotation_constraints


def test_simple_call_annotation():
    src = textwrap.dedent("""
    def foo(x: int(0 < _ < 100)) -> int:
        pass
    """)
    out = apply_annotation_constraints(src)
    assert "Annotated[int, '0 < _ < 100']" in out
    assert "from typing import Annotated" in out


def test_container_call_annotation():
    src = textwrap.dedent("""
    def bar(x: list[int(0 < _ < 100)]) -> int:
        pass
    """)
    out = apply_annotation_constraints(src)
    assert "list[Annotated[int, '0 < _ < 100']]" in out
    assert "from typing import Annotated" in out


def test_nested_container_call_annotation():
    src = textwrap.dedent("""
    def baz(x: dict[str, CustomType(config="A")]) -> None:
        pass
    """)
    out = apply_annotation_constraints(src)
    assert (
        'dict[str, Annotated[CustomType, "config="A""]]' in out
        or "dict[str, Annotated[CustomType, 'config=\"A\"']]" in out
        or "dict[str, Annotated[CustomType, \"config='A'\"]]" in out
        or "dict[str, Annotated[CustomType, 'config='A'']]" in out
        or "dict[str, Annotated[CustomType, 'config='A'']]" in out
        or "dict[str, Annotated[CustomType, \"config='A'\"]]" in out
        or "dict[str, Annotated[CustomType, 'config=\"A\"']]" in out
    )
    assert "from typing import Annotated" in out


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
