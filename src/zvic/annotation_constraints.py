"""
annotation_constraints.py

Implements the AST transformation described in spec-07-Annotation-Constraints.md:
Rewrites any Call inside a type annotation as Annotated[BaseType, MetaExpr].
"""

import ast


class AnnotateCallsTransformer(ast.NodeTransformer):
    """
    AST transformer that rewrites any Call inside a type annotation as
    Annotated[BaseType, MetaExpr], as described in ZVIC spec-07.
    """

    def __init__(self):
        super().__init__()
        self.need_imports = False

    def visit_FunctionDef(self, node):
        # Transform argument- and return-annotations
        for arg in node.args.args + node.args.kwonlyargs:
            if arg.annotation:
                new_ann = self._transform_ann(arg.annotation)
                if isinstance(new_ann, ast.expr):
                    arg.annotation = ast.copy_location(new_ann, arg.annotation)
        if node.returns:
            new_ret = self._transform_ann(node.returns)
            if isinstance(new_ret, ast.expr):
                node.returns = ast.copy_location(new_ret, node.returns)
        return node

    def _transform_ann(self, ann: ast.AST) -> ast.expr:
        # Recursively walk into container subscripts
        if isinstance(ann, ast.Subscript):
            new_value = self._transform_ann(ann.value)
            new_slice = self._transform_ann(ann.slice)
            new_sub = ast.Subscript(
                value=new_value if isinstance(new_value, ast.expr) else ann.value,
                slice=new_slice if isinstance(new_slice, ast.expr) else ann.slice,
                ctx=ann.ctx,
            )
            return ast.copy_location(new_sub, ann)
        # If it's a Tuple of types (e.g. Tuple[A,B])
        if isinstance(ann, ast.Tuple):
            new_elts = [
                self._transform_ann(e)
                if isinstance(self._transform_ann(e), ast.expr)
                else e
                for e in ann.elts
            ]
            new_tuple = ast.Tuple(elts=new_elts, ctx=ann.ctx)
            return ast.copy_location(new_tuple, ann)
        if isinstance(ann, ast.Call):
            base = ann.func
            # Recursively transform arguments and keywords
            for i, arg in enumerate(ann.args):
                ann.args[i] = self._transform_ann(arg) if isinstance(arg, ast.expr) else arg
            for i, kw in enumerate(ann.keywords):
                if hasattr(kw, "value") and isinstance(kw.value, ast.expr):
                    kw.value = self._transform_ann(kw.value)
            # Extract the full argument string (including keywords)
            try:
                call_src = ast.unparse(ann)
                constraint = call_src[call_src.find("(") + 1 : -1]
            except Exception:
                constraint = ""
            self.need_imports = True
            # Always wrap the base in a new Annotated, preserving nesting
            new_annotated = ast.Subscript(
                value=ast.Name(id="Annotated", ctx=ast.Load()),
                slice=ast.Tuple(
                    elts=[base, ast.Constant(value=constraint)], ctx=ast.Load()
                ),
                ctx=ast.Load(),
            )
            return ast.copy_location(new_annotated, ann)
        # Everything else untouched
        if isinstance(ann, ast.expr):
            return ann
        raise TypeError(f"Annotation node is not an ast.expr: {ann!r}")

    def visit_Module(self, node):
        node = self.generic_visit(node)  # apply transformations
        if self.need_imports and isinstance(node, ast.Module):
            # inject `from typing import Annotated`
            imp = ast.ImportFrom(
                module="typing",
                names=[ast.alias(name="Annotated", asname=None)],
                level=0,
            )
            node.body.insert(0, imp)
        return node


def apply_annotation_constraints(source: str) -> str:
    """
    Applies the AnnotateCallsTransformer to the given Python source code string.
    Returns the transformed source as a string.
    """
    tree = ast.parse(source)
    transformer = AnnotateCallsTransformer()
    new_tree = transformer.visit(tree)
    ast.fix_missing_locations(new_tree)
    return ast.unparse(new_tree)
