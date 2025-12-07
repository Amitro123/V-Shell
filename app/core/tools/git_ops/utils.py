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
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",      # force utf-8
            errors="replace",      # avoid UnicodeDecodeError
        )
        
        stdout = (proc.stdout or "") + (proc.stderr or "")
        stdout = stdout.strip()

        if proc.returncode != 0:
            logger.error(f"Git command failed with code {proc.returncode}: {stdout}")

        return stdout, proc.returncode
    except FileNotFoundError:
        logger.error("git command not found")
        return "git command not found", 127
    except Exception as e:
        logger.error(f"Git command failed: {e}")
        return str(e), 1
