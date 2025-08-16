import tempfile
import subprocess
import sys
import os

def run_crosshair_on_code(code: str, function_name: str) -> bool:
    """
    Write the given code to a temporary file and run crosshair check on the specified function.
    Returns True if crosshair finds no counterexample, False otherwise.
    """
    with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as tmp:
        tmp.write(code)
        tmp_path = tmp.name
    try:
        # Run crosshair check on the function
        cmd = [sys.executable, '-m', 'crosshair', 'check', tmp_path, '--analysis_kind', 'icontract', '--per_condition_timeout', '2']
        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout + '\n' + result.stderr
        print(f"run_crosshair_on_code DEBUG: cmd={' '.join(cmd)}\nreturncode={result.returncode}\noutput=\n{output}")
        # Look for 'No counterexamples found' or similar success message, or exit code 0
        if result.returncode == 0:
            return True
        if 'No counterexamples found' in output or 'No failed conditions' in output:
            return True
        return False
    finally:
        os.unlink(tmp_path)
