from typing import Tuple, Optional
import subprocess

async def run_tests(command: Optional[str] = None) -> Tuple[str, int]:
    """
    Run tests using the configured command (e.g. 'pytest').

    Returns:
        stdout_or_stderr, exit_code
    """
    cmd = (command or "pytest").split()
    # Using subprocess.run directly as tests often need specific environment/config 
    # and might not just be a simple git command.
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
        stdout = proc.stdout
        if proc.stderr:
            stdout += "\n" + proc.stderr
        return stdout, proc.returncode
    except Exception as e:
        return str(e), 1
