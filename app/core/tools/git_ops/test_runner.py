from typing import Tuple, Optional
import subprocess
import sys

async def run_tests(command: Optional[str] = None) -> Tuple[str, int]:
    """
    Run tests using the configured command (e.g. 'pytest').

    Returns:
        stdout_or_stderr, exit_code
    """
    if command:
        cmd = command.split()
    else:
        # Safer default: run pytest via current python interpreter
        cmd = [sys.executable, "-m", "pytest"]

    # Using subprocess.run directly as tests often need specific environment/config 
    # and might not just be a simple git command.
    try:
        # Force utf-8 encoding to handle emoji/special chars on Windows
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
        stdout = proc.stdout
        if proc.stderr:
            stdout += "\n" + proc.stderr
        return stdout, proc.returncode
    except Exception as e:
        return str(e), 1

