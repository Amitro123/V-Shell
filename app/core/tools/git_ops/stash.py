from typing import Tuple, Optional
from .utils import run_git

async def git_stash_push(message: Optional[str] = None) -> Tuple[str, int]:
    """
    Stash current changes. Optionally attach a message.
    
    Args:
        message: Optional message to describe the stash.
    
    Returns:
        Tuple of (stdout, exit_code)
    """
    args = ["stash", "push"]
    if message:
        args.extend(["-m", message])
    return await run_git(args)

async def git_stash_pop() -> Tuple[str, int]:
    """
    Apply and drop the most recent stash (git stash pop).
    
    Returns:
        Tuple of (stdout, exit_code)
    """
    return await run_git(["stash", "pop"])
