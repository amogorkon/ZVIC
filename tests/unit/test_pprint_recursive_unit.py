import io
import sys
from pathlib import Path

from zvic.main import canonicalize, load_module, pprint_recursive


def get_canonical_output():
    foo_path = Path(__file__).parent / "stuff" / "foo_module.py"
    mod = load_module(foo_path, "foo_module")
    canonical = canonicalize(mod)
    buf = io.StringIO()
    sys_stdout = sys.stdout
    sys.stdout = buf
    try:
        pprint_recursive(canonical)
    finally:
        sys.stdout = sys_stdout
    return buf.getvalue()


def test_pprint_recursive_output():
    expected = """foo:
  __call__:
    params:
      positional_only:
      positional_or_keyword:
        -
          type:
            int
          constraint:
            _ < 10
          name:
            x
        -
          type:
            str
          constraint:
            len(_) > 5
          name:
            y
      keyword_only:
    return:
      type:
        NoneType
bar:
  __call__:
    params:
      positional_only:
      positional_or_keyword:
        -
          type:
            int
          name:
            x
      keyword_only:
        -
          name:
            a
          default:
            23
        -
          name:
            b
          default:
            2
        -
          name:
            c
          default:
            1
    return:
      type:
        int
baz:
  __call__:
    params:
      positional_only:
      positional_or_keyword:
        -
          type:
            str
          name:
            y
      keyword_only:
    return:
      type:
        int
      constraint:
        _ > 3
Foo:
  method_x:
    params:
      positional_only:
      positional_or_keyword:
        -
          name:
            self
        -
          type:
            int
          name:
            a
      keyword_only:
    return:
      type:
        str
  method_a:
    params:
      positional_only:
      positional_or_keyword:
        -
          name:
            self
        -
          type:
            str
          name:
            b
      keyword_only:
    return:
      type:
        int
  method_d:
    params:
      positional_only:
      positional_or_keyword:
        -
          type:
            float
          name:
            c
      keyword_only:
    return:
      type:
        float
CallableClass:
  __call__:
    params:
      positional_only:
      positional_or_keyword:
        -
          name:
            self
        -
          type:
            int
          name:
            x
        -
          type:
            str
          name:
            y
      keyword_only:
    return:
      type:
        int
"""
    output = get_canonical_output()
    # Remove trailing whitespace for each line for robust comparison
    output = "\n".join(line.rstrip() for line in output.splitlines()) + "\n"
    expected = "\n".join(line.rstrip() for line in expected.splitlines()) + "\n"
    assert output == expected
