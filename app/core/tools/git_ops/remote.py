from typing import Tuple
from .utils import run_git

async def git_remote_list() -> Tuple[str, int]:
    """
    Show configured remotes (git remote -v).
    
    Returns:
        Tuple of (stdout, exit_code)
    """
    return await run_git(["remote", "-v"])
