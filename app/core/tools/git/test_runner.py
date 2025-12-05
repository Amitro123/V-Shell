import subprocess
import sys
from typing import Tuple, Optional

async def run_tests(command: Optional[str] = None) -> Tuple[str, int]:
    """
    Run project tests. Defaults to `pytest`.
    Returns (stdout, exit_code).
    """
    # If command is provided, we might run that, but safely.
    # For now, matching original logic which forces pytest via python -m pytest
    # The original implementation ignored params besides what was hardcoded mostly, 
    # but let's allow flexibility if the plan implies it. 
    # Plan says: "run_tests (if it's Git/project-specific) -> tools/git/tests.py"
    
    try:
        # Using sys.executable ensures we use the same venv
        cmd = [sys.executable, "-m", "pytest"]
        if command:
            # If user provided a specific command string (e.g. "pytest -v"), 
            # might be unsafe to just shell=True. 
            # I will stick to the safe implementation:
            pass 
        
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
