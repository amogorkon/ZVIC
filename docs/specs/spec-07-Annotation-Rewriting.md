
# ZVIC Annotation Constraints (v5.0)

This spec describes the ZVIC approach to supporting arbitrary constraints and refinements in type annotations, using a generic AST transformation to rewrite any `Call` inside a type annotation as an `Annotated[BaseType, MetaExpr]`. This enables expressive, composable, and runtime-reflectable constraints for all types, including containers and user-defined types.

---

## 1. The General AST Rewrite

```python
import ast

class AnnotateCallsTransformer(ast.NodeTransformer):
    def __init__(self):
        super().__init__()
        self.need_imports = False

    def visit_FunctionDef(self, node):
        # transform argument- and return-annotations
        for arg in node.args.args + node.args.kwonlyargs:
            if arg.annotation:
                arg.annotation = self._transform_ann(arg.annotation)
        if node.returns:
            node.returns = self._transform_ann(node.returns)
        return node

    def _transform_ann(self, ann: ast.AST) -> ast.AST:
        # recursively walk into container subscripts
        if isinstance(ann, ast.Subscript):
            ann.value   = self._transform_ann(ann.value)
            ann.slice   = self._transform_ann(ann.slice)
            return ann

        # if it's a Tuple of types (e.g. Tuple[A,B])
        if isinstance(ann, ast.Tuple):
            ann.elts = [self._transform_ann(e) for e in ann.elts]
            return ann

        # **THE MAGIC**: catch any Call in an annotation
        if isinstance(ann, ast.Call):
            base     = ann.func               # the type being “called”
            metadata = ann                   # the call itself becomes metadata
            self.need_imports = True

            # produce Annotated[base, metadata]
            return ast.Subscript(
                value=ast.Name(id="Annotated", ctx=ast.Load()),
                slice=ast.Tuple(
                    elts=[base, metadata],
                    ctx=ast.Load()
                ),
                ctx=ast.Load()
            )

        # everything else untouched
        return ann

    def visit_Module(self, node):
        node = self.generic_visit(node)  # apply transformations
        if self.need_imports:
            # inject `from typing import Annotated`
            imp = ast.ImportFrom(module="typing",
                                 names=[ast.alias(name="Annotated", asname=None)],
                                 level=0)
            node.body.insert(0, imp)
        return node
```

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
