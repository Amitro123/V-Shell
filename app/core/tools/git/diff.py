import git
from typing import Tuple, Optional

async def git_diff(repo: git.Repo, path: Optional[str] = None) -> Tuple[str, int]:
    """
    Run `git diff`.
    Returns (stdout, exit_code).
    """
    try:
        if path:
            diff = repo.git.diff(path)
        else:
            diff = repo.git.diff()
        return diff, 0
    except git.GitCommandError as e:
        return str(e), e.status
    except Exception as e:
        return str(e), 1
