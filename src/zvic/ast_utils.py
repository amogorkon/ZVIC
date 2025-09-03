import ast
from pathlib import Path
from types import ModuleType

from .annotation_constraints import AnnotateCallsTransformer


def transform_module_source(source: str, filename: str = "<string>") -> ast.Module:
    """Parse source text and return a transformed ast.Module.

    This function is pure in the sense that it does not exec the module or mutate
    global interpreter state; it only returns a transformed AST that callers may
    compile/exec as desired.
    """
    tree = ast.parse(source, filename=filename)
    transformer = AnnotateCallsTransformer()
    new_tree = transformer.visit(tree)
    ast.fix_missing_locations(new_tree)
    return new_tree


def strip_constrain_calls(
    module: ast.Module, func_name: str = "constrain_this_module"
) -> None:
    """Remove top-level bare calls to `constrain_this_module()` from an AST module in-place.

    This keeps the function signature simple (operates directly on the AST) and
    callers can choose when to call it.
    """
    new_body = []
    for stmt in module.body:
        removed = False
        # Bare expression: `constrain_this_module()`
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            func = stmt.value.func
            if (isinstance(func, ast.Name) and func.id == func_name) or (
                isinstance(func, ast.Attribute) and func.attr == func_name
            ):
                removed = True
        # Assignment: `x = constrain_this_module()`
        elif isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call):
            func = stmt.value.func
            if (isinstance(func, ast.Name) and func.id == func_name) or (
                isinstance(func, ast.Attribute) and func.attr == func_name
            ):
                removed = True
        # Annotated assignment: `x: T = constrain_this_module()`
        elif isinstance(stmt, ast.AnnAssign) and isinstance(stmt.value, ast.Call):
            func = stmt.value.func
            if (isinstance(func, ast.Name) and func.id == func_name) or (
                isinstance(func, ast.Attribute) and func.attr == func_name
            ):
                removed = True
        if not removed:
            new_body.append(stmt)
    module.body = new_body


def transform_module(
    module: ModuleType, target: ModuleType | None = None
) -> tuple[ModuleType, ast.Module]:
    """Transform the source for `module` (reads module.__file__) and execute
    the transformed code into `target` ModuleType (if provided) or a new
    ModuleType. Returns a tuple of (executed_module, transformed_ast).

    This function does not mutate the input `module` object itself unless it is
    passed as the `target` parameter. By default it creates a fresh module and
    executes transformed code there, leaving the input module unchanged.
    """
    filename = getattr(module, "__file__", None)
    if not filename:
        raise RuntimeError("Module has no __file__ attribute; cannot transform")
    source = Path(filename).read_text(encoding="utf-8")
    new_tree = transform_module_source(source, filename)
    strip_constrain_calls(new_tree)
    ast.fix_missing_locations(new_tree)
    code = compile(new_tree, str(filename), "exec")

    exec_mod = ModuleType(module.__name__) if target is None else target
    exec_mod.__dict__["__file__"] = str(filename)
    exec(code, exec_mod.__dict__)
    setattr(exec_mod, "__original_source__", source)
    return exec_mod, new_tree
