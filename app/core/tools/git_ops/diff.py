import subprocess
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

async def git_diff(repo=None, path: Optional[str] = None, since_origin_main: bool = False) -> Tuple[str, int]:
    """
    Show git diff.

    - If since_origin_main is True: diff against origin/main.
    - Else: diff against HEAD (working tree / staged depending on config).
    - If path is provided, restrict diff to that file/folder.
    """
    base_ref = "origin/main" if since_origin_main else "HEAD"

    cmd = ["git", "diff", base_ref]
    if path:
        cmd.append(path)

    logger.info("Running: %s", " ".join(cmd))
    try:
        # Use repo.working_dir as cwd if repo is provided, otherwise use current dir
        cwd = repo.working_dir if repo else None
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
        stdout = proc.stdout
        if proc.stderr:
             stdout += "\n" + proc.stderr
        return stdout, proc.returncode
    except Exception as e:
        logger.error(f"git diff failed: {e}")
        return str(e), 1
