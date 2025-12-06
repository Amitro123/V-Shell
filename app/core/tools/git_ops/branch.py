from typing import Tuple
from .utils import run_git

async def git_checkout_branch(name: str, create: bool = False) -> Tuple[str, int]:
    """
    Switch to an existing branch, or create it if create=True.

    Args:
        name: target branch name (required).
        create: if True, run `git checkout -b <name>`, else `git checkout <name>`.
    """
    if not name:
        raise ValueError("Branch name is required for git_checkout_branch")

    args = ["checkout"]
    if create:
        args.append("-b")
    args.append(name)

    return await run_git(args)
