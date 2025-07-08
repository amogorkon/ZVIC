
# ZVIC Annotation Constraints

This spec describes the ZVIC approach to supporting arbitrary constraints and refinements in type annotations, using a generic AST transformation to rewrite any `Call` inside a type annotation as an `Annotated[BaseType, "constraint"]`, where `constraint` is the string inside the parentheses of the call. This enables expressive, composable, and runtime-reflectable constraints for all types, including containers and user-defined types.

---


## 1. The General AST Rewrite

The transformation walks the AST and, for any type annotation of the form `Type(constraint)`, rewrites it as:

```python
Annotated[Type, "constraint"]
```

where `constraint` is the string representation of the arguments inside the parentheses. For example:

```python
def foo(x: int(0 < _ < 100)) -> int:
    pass
# becomes
def foo(x: Annotated[int, "0 < _ < 100"]) -> int:
    pass
```

For container types, the transformation is recursive:

```python
def bar(x: list[int(0 < _ < 100)]) -> int:
    pass
# becomes
def bar(x: list[Annotated[int, "0 < _ < 100"]]) -> int:
    pass
```

For nested/complex types:

```python
def baz(x: dict[str, CustomType(config="A")]) -> None:
    pass
# becomes
def baz(x: dict[str, Annotated[CustomType, 'config="A"']]) -> None:
    pass
```

The transformer also auto-injects `from typing import Annotated` at the top if any transformation occurs.

### What this does

1.  Walks just the `FunctionDef` nodes and looks at their `.annotation` fields.
2.  Whenever it sees an `ast.Call` inside an annotation—whether that’s
    - a top‐level call (`x: Foo(bar=…)`)
    - a call *inside* a subscript (`x: List[Foo(…) ]`)—
   it replaces it with
   ```python
   Annotated[ Foo, Foo(...) ]
   ```
3.  It auto‐injects `from typing import Annotated` at the top.

---

## 2. How It Handles Container Types

Given for example:

```python
def f(
  a: list[int(0<x<100)],
  b: Dict[str, CustomType(config="A")],
) -> Union[int, float]:
    ...
```

1.  The transformer sees `ann = Subscript(value=Name("list"), slice=Call(Name("int"), ...))`.
2.  It rewrites the inner `Call(int(...))` into
    ```python
    Subscript(
      value=Name("list"),
      slice=Subscript(
        value=Name("Annotated"),
        slice=Tuple([ Name("int"), Call(Name("int"), ... ) ])
      )
    )
    ```
3.  Then `list[...]` remains as‐is, but now the element type is `Annotated[int, RangedInt(…)]`.
4.  Similarly for `Dict[str, CustomType(...)]` → `Dict[str, Annotated[CustomType, CustomType(...)]`.

At runtime, `inspect.signature(f)` will give you `Annotated` types with your metadata call baked in—which you can pick up in your `to_typerep()` logic and treat exactly like any other `Annotated`‐based refinement.

---

## 3. Putting It All Together

1.  **AST Hook**
    Install a `meta_path` finder or apply this transformer in your hot‐reload pipeline so that every module gets patched before execution.

2.  **User Code—No Extra Imports**
    ```python
    def foo(x: int(0 < x < 100), items: List[str.uppercase()]) -> int:
        …
    ```
    You’re free to call any type (even user‐defined `MyValidator(...)`) inside the annotation.

3.  **Runtime Reflection**
    ```python
    sig = inspect.signature(foo)
    ann = sig.parameters["x"].annotation
    # ann is Annotated[int, Call(int,...)]
    base, meta = get_origin(ann), get_args(ann)[1]
    # meta is the AST‐evaluated result of int(0<x<100)
    ```
    Your existing ZVIC pipeline sees that metadata and applies whatever rule you’ve registered for it—range checks, custom validations, etc.

---

### Benefits

- **Maximal Elegance**: users just write `Type(args…)` inline.
- **Zero New Syntax**: uses vanilla Python calls.
- **Universal**: works for builtins, containers, user classes—any call in an annotation.
- **Composable**: you can layer on multiple metadata calls, or even chains (`Foo(cfg)(extra=…)`) and the transformer will nest them into multiple `Annotated` layers.

---

With this generic AST hack, *any* call expression in an annotation becomes a first-class refinement, seamlessly integrated into ZVIC’s `Annotated`-driven pipeline.
