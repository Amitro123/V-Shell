from typing import Tuple, Optional, List
from .utils import run_git

async def git_fetch(remote: Optional[str] = None, extra_args: Optional[List[str]] = None) -> Tuple[str, int]:
    """
    Run `git fetch`.
    
    Args:
        remote: Optional remote name.
        extra_args: Optional list of extra git arguments.
    """
    args = ["fetch"]
    if remote:
        args.append(remote)
    if extra_args:
        args.extend(extra_args)
    return await run_git(args)
