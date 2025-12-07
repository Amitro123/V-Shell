from typing import Tuple, Optional
from .utils import run_git

async def git_fetch(remote: Optional[str] = None) -> Tuple[str, int]:
    """
    Run `git fetch` (optionally for a specific remote).
    
    Args:
        remote: Optional remote name. If None, fetches from all remotes.
    
    Returns:
        Tuple of (stdout, exit_code)
    """
    args = ["fetch"]
    if remote:
        args.append(remote)
    return await run_git(args)
