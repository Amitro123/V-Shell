from typing import Tuple, Optional
from .utils import run_git

async def git_diff(repo=None, path: Optional[str] = None, since_origin_main: bool = False) -> Tuple[str, int]:
    """
    Show git diff.

    - if since_origin_main=True: diff vs origin/main
    - else: diff vs HEAD
    - if path is set: restrict to that file/folder
    """
    # Note: 'repo' argument is kept for compatibility with existing calls if any, 
    # but ignored by run_git logic.
    base_ref = "origin/main" if since_origin_main else "HEAD"
    args = ["diff", base_ref]
    if path:
        args.append(path)
    return await run_git(args)
