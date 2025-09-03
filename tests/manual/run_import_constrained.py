from pathlib import Path

from zvic import install_import_hook

# Install the import hook (harmless) and then explicitly transform & load the
# constrained module using `load_module` so this script works even if the
# import hook's allowlist doesn't include the test path.
test_dir = str(Path(__file__).parent.resolve()).replace("\\", "/")
# Allow the import hook to transform files in the tests manual folder
install_import_hook(allow_roots=[test_dir])

from import_constrained import foo

foo(10)
print("Success!")
