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

    def visit_FunctionDef(self, node: ast.FunctionDef):
        # Track constraints for this function
        constraints = []
        # Transform argument- and return-annotations
        for arg in node.args.args + node.args.kwonlyargs:
            if arg.annotation:
                new_ann = self._transform_ann(arg.annotation)
                # If annotation is Annotated with a constraint, extract it
                if (
                    isinstance(new_ann, ast.Subscript)
                    and getattr(new_ann.value, "id", None) == "Annotated"
                    and isinstance(new_ann.slice, ast.Tuple)
                    and len(new_ann.slice.elts) == 2
                    and isinstance(new_ann.slice.elts[1], ast.Constant)
                    and new_ann.slice.elts[1].value
                ):
                    if constraint := new_ann.slice.elts[1].value:
                        # Replace _ with the argument name in the constraint
                        param_constraint = str(constraint).replace("_", arg.arg)
                        constraints.append(param_constraint)
                arg.annotation = ast.copy_location(new_ann, arg.annotation)
        return_constraint = None
        if node.returns:
            new_ret = self._transform_ann(node.returns)
            if (
                isinstance(new_ret, ast.Subscript)
                and getattr(new_ret.value, "id", None) == "Annotated"
                and isinstance(new_ret.slice, ast.Tuple)
                and len(new_ret.slice.elts) == 2
                and isinstance(new_ret.slice.elts[1], ast.Constant)
                and new_ret.slice.elts[1].value
            ):
                if constraint := new_ret.slice.elts[1].value:
                    return_constraint = str(constraint)
            node.returns = ast.copy_location(new_ret, node.returns)
        # Insert assert statements for constraints if __debug__ is True
        if constraints:
            # Compose a single assertion for each constraint
            for constraint in constraints:
                # Parse the constraint expression for the assert
                expr_ast = ast.parse(str(constraint), mode="eval")
                constraint_expr = expr_ast.body
                # Add the constraint as the assertion message
                assert_node = ast.Assert(
                    test=constraint_expr,
                    msg=ast.Constant(value=f"'{constraint}' not satisfied."),
                )
                # Wrap in if __debug__:
                debug_if = ast.If(
                    test=ast.Name(id="__debug__", ctx=ast.Load()),
                    body=[assert_node],
                    orelse=[],
                )
                node.body.insert(0, debug_if)

        if return_constraint:
            # Replace _ with a unique variable name
            ret_var = "__zvic_retval"
            constraint_expr_str = return_constraint.replace("_", ret_var)
            # Wrap the entire function body to check the return value
            new_body = []
            for stmt in node.body:
                if isinstance(stmt, ast.Return):
                    # Assign return value to ret_var
                    assign = ast.Assign(
                        targets=[ast.Name(id=ret_var, ctx=ast.Store())],
                        value=stmt.value,
                    )
                    # Assert on ret_var
                    expr_ast = ast.parse(str(constraint_expr_str), mode="eval")
                    assert_node = ast.Assert(
                        test=expr_ast.body,
                        msg=ast.Constant(
                            value=f"Return constraint '{return_constraint}' not satisfied."
                        ),
                    )
                    debug_if = ast.If(
                        test=ast.Name(id="__debug__", ctx=ast.Load()),
                        body=[assert_node],
                        orelse=[],
                    )
                    # Return ret_var
                    ret_stmt = ast.Return(value=ast.Name(id=ret_var, ctx=ast.Load()))
                    new_body.extend([assign, debug_if, ret_stmt])
                else:
                    new_body.append(stmt)
            node.body = new_body
        return node

    def _transform_ann(self, ann: ast.AST) -> ast.expr:
        """
        Recursively transforms annotation AST nodes. Always returns ast.expr or raises TypeError.
        """
        # Prevent infinite recursion: if already Annotated, do not transform again
        if (
            isinstance(ann, ast.Subscript)
            and getattr(ann.value, "id", None) == "Annotated"
        ):
            return ann
        # Prevent re-wrapping: if this is a Call and already wrapped, do not wrap again
        if isinstance(ann, ast.Call):
            base = ann.func
            # Only transform arguments and keywords, not recursively wrap
            ann.args = [self._transform_ann(arg) for arg in ann.args]
            for kw in ann.keywords:
                if hasattr(kw, "value"):
                    kw.value = self._transform_ann(kw.value)
            # Extract the full argument string (including keywords)
            try:
                call_src = ast.unparse(ann)
                constraint = call_src[call_src.find("(") + 1 : -1]
            except Exception:
                constraint = ""
            self.need_imports = True
            # Wrap the base in a new Annotated, but do not recursively process the result
            new_annotated = ast.Subscript(
                value=ast.Name(id="Annotated", ctx=ast.Load()),
                slice=ast.Tuple(
                    elts=[base, ast.Constant(value=constraint)], ctx=ast.Load()
                ),
                ctx=ast.Load(),
            )
            return ast.copy_location(new_annotated, ann)
        if isinstance(ann, ast.Subscript):
            new_value = self._transform_ann(ann.value)
            new_slice = self._transform_ann(ann.slice)
            new_sub = ast.Subscript(
                value=new_value,
                slice=new_slice,
                ctx=ann.ctx,
            )
            return ast.copy_location(new_sub, ann)
        # If it's a Tuple of types (e.g. Tuple[A,B])
        if isinstance(ann, ast.Tuple):
            new_elts = [self._transform_ann(e) for e in ann.elts]
            new_tuple = ast.Tuple(elts=new_elts, ctx=ann.ctx)
            return ast.copy_location(new_tuple, ann)
        # Everything else untouched
        if isinstance(ann, ast.expr):
            return ann
        raise TypeError(f"Annotation node is not an ast.expr: {ann!r}")

    def visit_Module(self, node: ast.Module) -> ast.Module:
        new_node = self.generic_visit(node)
        assert isinstance(new_node, ast.Module), (
            "Expected ast.Module after generic_visit"
        )
        if self.need_imports:
            # inject `from typing import Annotated`
            imp = ast.ImportFrom(
                module="typing",
                names=[ast.alias(name="Annotated", asname=None)],
                level=0,
            )
            new_node.body.insert(0, imp)
        return new_node


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
