import ast

from zvic.annotation_constraints import AnnotateCallsTransformer

src = "def foo(x: list[int(0 < _ < 100)](len(_) == 3)) -> None: pass"
mod = ast.parse(src)
func = mod.body[0]
ann = func.args.args[0].annotation
print("Original annotation unparse:", ast.unparse(ann))
print("Original annotation AST dump:")
print(ast.dump(ann, include_attributes=False, indent=2))

tr = AnnotateCallsTransformer()
new_ann = tr._transform_ann(ann)
print("\nTransformed annotation unparse:", ast.unparse(new_ann))
print("Transformed annotation AST dump:")
print(ast.dump(new_ann, include_attributes=False, indent=2))
