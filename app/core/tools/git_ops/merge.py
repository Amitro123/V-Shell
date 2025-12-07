from typing import Tuple
from .utils import run_git

async def git_merge(branch: str) -> Tuple[str, int]:
    """
    Merge the given branch into the current branch.
    
    Does not handle conflicts yet; just runs `git merge <branch>`.
    
    Args:
        branch: Name of the branch to merge.
    
    Returns:
        Tuple of (stdout, exit_code)
    """
    if not branch:
        raise ValueError("git.merge requires a branch name")
    return await run_git(["merge", branch])
