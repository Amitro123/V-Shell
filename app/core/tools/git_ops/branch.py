from typing import Tuple
from .utils import run_git

async def git_checkout_branch(name: str, create: bool = False) -> Tuple[str, int]:
    """
    Switch to an existing branch, or create it if create=True.
    - create=False: git checkout <name>
    - create=True:  git checkout -b <name>
    """
    # Note: 'repo' arg unused if it was ever passed.
    cmd = ["checkout"]
    if create:
        cmd.append("-b")
    cmd.append(name)
    return await run_git(cmd)
