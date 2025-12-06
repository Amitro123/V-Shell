from typing import Tuple
from .utils import run_git

async def git_add_all() -> Tuple[str, int]:
    """
    Stage all changes: equivalent to `git add -A`.
    """
    return await run_git(["add", "-A"])
