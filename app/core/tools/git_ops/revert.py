from typing import Tuple, Optional
from .utils import run_git

async def git_revert(commit: Optional[str] = None) -> Tuple[str, int]:
    """
    Safely revert a commit by creating a new commit that undoes it.
    
    Args:
        commit: Commit hash to revert. If None, defaults to HEAD.
    
    Returns:
        Tuple of (stdout, exit_code)
    """
    target = commit or "HEAD"
    return await run_git(["revert", "--no-edit", target])
