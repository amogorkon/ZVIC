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
                param_type = None
                if (
                    isinstance(new_ann, ast.Subscript)
                    and getattr(new_ann.value, "id", None) == "Annotated"
                ):
                    # Extract type and constraint
                    if (
                        isinstance(new_ann.slice, ast.Tuple)
                        and len(new_ann.slice.elts) == 2
                    ):
                        base_type_node = new_ann.slice.elts[0]
                        constraint_node = new_ann.slice.elts[1]
                        # Try to get type name from base_type_node
                        if isinstance(base_type_node, ast.Name):
                            param_type = base_type_node.id
                        elif isinstance(base_type_node, ast.Attribute):
                            param_type = ast.unparse(base_type_node)
                        constraint = (
                            constraint_node.value
                            if isinstance(constraint_node, ast.Constant)
                            else None
                        )
                        if constraint:
                            param_constraint = str(constraint).replace("_", arg.arg)
                            constraints.append((arg.arg, param_type, param_constraint))
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
            # Compose a PEP 316 docstring for CrossHair
            doc_lines = []
            for param_name, _, constraint in constraints:
                doc_lines.append(f"pre: {constraint}")
            if return_constraint:
                doc_lines.append(f"post: {return_constraint}")
            docstring = "\n".join(doc_lines) if doc_lines else None
            # Only insert assertions if __debug__ is True at transformation time
            type_asserts = []
            constraint_asserts = []
            if __debug__:
                for param_name, param_type, _ in constraints:
                    if param_type:
                        type_asserts.append(ast.Assert(
                            test=ast.Call(
                                func=ast.Name(id="assumption", ctx=ast.Load()),
                                args=[
                                    ast.Name(id=param_name, ctx=ast.Load()),
                                    ast.Name(id=param_type, ctx=ast.Load()),
                                ],
                                keywords=[],
                            ),
                            msg=ast.Constant(
                                value=f"Type assertion failed for {param_name}: expected {param_type}"
                            ),
                        ))
                for param_name, _, constraint in constraints:
                    expr_ast = ast.parse(str(constraint), mode="eval")
                    constraint_expr = expr_ast.body
                    constraint_asserts.append(ast.Assert(
                        test=constraint_expr,
                        msg=ast.Constant(value=f"'{constraint}' not satisfied."),
                    ))
            # Compose new body: docstring, type asserts, constraint asserts, then rest
            new_body = []
            if docstring:
                doc_node = ast.Expr(value=ast.Constant(value=docstring))
                new_body.append(doc_node)
            new_body.extend(type_asserts)
            new_body.extend(constraint_asserts)
            # Add the rest of the original body, skipping any old docstring
            orig_body = node.body
            if orig_body and isinstance(orig_body[0], ast.Expr) and isinstance(orig_body[0].value, ast.Constant) and isinstance(orig_body[0].value.value, str):
                orig_body = orig_body[1:]
            new_body.extend(orig_body)
            node.body = new_body

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
                            value=f"Return constraint '{return_constraint}' not satisfied (_ = {ret_var}))."
                        ),
                    )
                    # Only insert return assertion if __debug__ is True at transformation time
                    if __debug__:
                        new_body.extend([assign, assert_node, ast.Return(value=ast.Name(id=ret_var, ctx=ast.Load()))])
                    else:
                        new_body.append(stmt)
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
            # Find the last __future__ import
            insert_at = 0
            for idx, stmt in enumerate(new_node.body):
                if (
                    isinstance(stmt, ast.ImportFrom)
                    and stmt.module == "__future__"
                ):
                    insert_at = idx + 1
            imp = ast.ImportFrom(
                module="typing",
                names=[ast.alias(name="Annotated", asname=None)],
                level=0,
            )
            new_node.body.insert(insert_at, imp)
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
