from typing import Tuple, Optional
from .utils import run_git

async def git_pull(repo=None, remote: Optional[str] = None, branch: Optional[str] = None) -> Tuple[str, int]:
    """
    Run `git pull` (optionally remote/branch).
    """
    # Note: 'repo' argument kept for signature compatibility during transition if needed, but unused.
    args = ["pull"]
    if remote:
        args.append(remote)
    if branch:
        args.append(branch)
    return await run_git(args)
