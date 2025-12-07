from typing import Dict, Optional
import subprocess
import sys

async def run_tests(command: Optional[str] = None) -> Dict[str, object]:
    """
    Run tests using the configured command (e.g. 'pytest').

    Returns:
        {
            "stdout": full text output,
            "exit_code": int,
            "summary": short human-readable summary
        }
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
        
        exit_code = proc.returncode
        summary = "All tests passed." if exit_code == 0 else f"Tests failed (exit code {exit_code})."
        
        return {
            "stdout": stdout,
            "exit_code": exit_code,
            "summary": summary
        }
    except Exception as e:
        return {
            "stdout": str(e),
            "exit_code": 1,
            "summary": f"Execution failed: {str(e)}"
        }


