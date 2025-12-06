from typing import Tuple, Optional
import subprocess

async def run_tests(command: Optional[str] = None) -> Tuple[str, int]:
    """
    Run tests using the configured command (e.g. 'pytest').
    """
    cmd = (command or "pytest").split()
    # Using specific handling for tests as requested (not run_git)
    # But using subprocess directly as per prompt example for tests.py
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
        stdout = proc.stdout
        if proc.stderr:
             stdout += "\n" + proc.stderr
        return stdout, proc.returncode
    except Exception as e:
        return str(e), 1
