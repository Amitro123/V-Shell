import subprocess
import sys
from typing import Tuple

async def run_tests() -> Tuple[str, int]:
    """
    Run project tests using pytest.
    Returns (stdout, exit_code).
    """
    try:
        # Using sys.executable ensures we use the same venv
        cmd = [sys.executable, "-m", "pytest"]
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            check=False
        )
        
        output = result.stdout
        if result.returncode != 0:
            output += "\n" + result.stderr
            
        return output, result.returncode
    except Exception as e:
        return str(e), 1

