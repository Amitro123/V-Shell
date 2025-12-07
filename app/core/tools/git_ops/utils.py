import asyncio
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

async def run_git(args: List[str]) -> Tuple[str, int]:
    """
    Run a git command with the given arguments asynchronously.

    Returns:
        stdout_or_stderr: str
        exit_code: int
    """
    cmd = ["git", *args]
    logger.info("Running git command: %s", " ".join(cmd))
    
    try:
        # Create subprocess
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Wait for completion and capture output
        stdout_bytes, stderr_bytes = await proc.communicate()
        
        # Decode output robustly
        stdout_str = stdout_bytes.decode("utf-8", errors="replace")
        stderr_str = stderr_bytes.decode("utf-8", errors="replace")
        
        # Combine stdout and stderr (mimicking previous behavior)
        output = (stdout_str + stderr_str).strip()

        if proc.returncode != 0:
            logger.error(f"Git command failed with code {proc.returncode}: {output}")

        return output, proc.returncode

    except FileNotFoundError:
        logger.error("git command not found")
        return "git command not found", 127
    except Exception as e:
        logger.error(f"Git command failed: {e}")
        return str(e), 1
