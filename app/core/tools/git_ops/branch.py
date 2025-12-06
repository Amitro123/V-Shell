from typing import Tuple
import subprocess
import logging

logger = logging.getLogger(__name__)

async def git_checkout_branch(name: str, create: bool = False) -> Tuple[str, int]:
    """
    Switch to an existing branch, or create it if create=True.
    - create=False: git checkout <name>
    - create=True:  git checkout -b <name>
    """
    cmd = ["git", "checkout"]
    if create:
        cmd.append("-b")
    cmd.append(name)

    logger.info("Running: %s", " ".join(cmd))
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
        stdout = proc.stdout
        if proc.stderr:
            stdout += "\n" + proc.stderr
        return stdout, proc.returncode
    except Exception as e:
        logger.error(f"git checkout failed: {e}")
        return str(e), 1
