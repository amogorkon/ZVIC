import ast
import importlib.abc
import importlib.machinery
import importlib.util
from pathlib import Path

from .ast_utils import strip_constrain_calls, transform_module_source


class ZvicLoader(importlib.abc.Loader):
    def __init__(self, fullname: str, path: str):
        self.fullname = fullname
        self.path = path

    def create_module(self, spec):
        # Default module creation
        return None

    def exec_module(self, module):
        filename = self.path
        source = Path(filename).read_text(encoding="utf-8")
        # Apply the annotation constraints transformer using central helper
        new_tree = transform_module_source(source, filename)
        strip_constrain_calls(new_tree)
        ast.fix_missing_locations(new_tree)
        code = compile(new_tree, filename, "exec")
        # Execute in module namespace
        module.__dict__["__file__"] = filename
        exec(code, module.__dict__)


class ZvicFinder(importlib.abc.MetaPathFinder):
    """A MetaPathFinder that applies ZvIC annotation constraints to source
    modules before they are executed. It delegates to PathFinder to locate
    the source file and then returns a spec with ZvicLoader for .py files.
    """

    def __init__(
        self, *, exclude_prefix: str | None = None, allow_roots: list[str] | None = None
    ):
        # Exclude transforming zvic itself to avoid recursion
        self.exclude_prefix = exclude_prefix or "zvic"
        # Allowlist for roots we will transform. Default to the CIDStore project
        # src path so third-party packages are not rewritten. Consumers may
        # provide explicit `allow_roots` to include other locations (e.g.
        # tests directory).
        self.allow_roots = [] if allow_roots is None else allow_roots

    def find_spec(self, fullname, path, target=None):
        # Never transform the zvic package itself
        if fullname.startswith(self.exclude_prefix):
            return None
        # Use PathFinder to find source module without recursion into meta_path
        spec = importlib.machinery.PathFinder.find_spec(fullname, path)
        if not spec:
            return None
        # Only transform regular .py source files and only those under allow_roots
        origin = getattr(spec, "origin", None)
        if not origin or not origin.endswith(".py"):
            return None
        # Only transform files under configured roots to avoid touching third-party packages
        origin_low = origin.replace("\\", "/").lower()
        allowed = any(
            root.replace("\\", "/").lower() in origin_low for root in self.allow_roots
        )
        if not allowed:
            return None
        # Create a new spec that uses our loader
        loader = ZvicLoader(fullname, origin)
        return importlib.util.spec_from_loader(fullname, loader, origin=origin)
