from typing import Tuple
from .utils import run_git

async def git_status() -> Tuple[str, int]:
    """Run `git status -sb`."""
    return await run_git(["status", "-sb"])
