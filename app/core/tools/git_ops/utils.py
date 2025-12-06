import subprocess
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

async def run_git(args: List[str]) -> Tuple[str, int]:
    """
    Run a git command with the given arguments.

    Returns:
        stdout_or_stderr: str
        exit_code: int
    """
    cmd = ["git", *args]
    logger.info("Running git command: %s", " ".join(cmd))
    # We use subprocess.run (synchronous) here but wrap it if needed or assume it's fast enough.
    # The user prompt example used synchronous subprocess.run inside an async def.
    # In a real async app we might want asyncio.create_subprocess_exec, but I will stick to the user's provided snippet
    # which uses subprocess.run.
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
        stdout = proc.stdout
        if proc.stderr:
            stdout += "\n" + proc.stderr
        return stdout.strip(), proc.returncode
    except FileNotFoundError:
        return "git command not found", 127
    except Exception as e:
        logger.error(f"Git command failed: {e}")
        return str(e), 1
