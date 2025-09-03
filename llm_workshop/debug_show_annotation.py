import textwrap

from zvic.annotation_constraints import apply_annotation_constraints

src = textwrap.dedent("""
def foo(x: list[int(0 < _ < 100)](len(_) == 3)) -> None:
    pass
""")
print(apply_annotation_constraints(src))
