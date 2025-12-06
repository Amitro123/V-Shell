from typing import Tuple
from .utils import run_git

async def git_log(limit: int = 20) -> Tuple[str, int]:
    """
    Show recent git log (oneline, decorated).

    Args:
        limit: number of commits to show (default 20).
    """
    args = ["log", "--oneline", "--decorate", f"-n{limit}"]
    return await run_git(args)
