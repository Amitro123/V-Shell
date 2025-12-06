import git
from typing import Tuple, Optional

async def git_pull(repo: git.Repo, remote: str = "origin", branch: Optional[str] = None) -> Tuple[str, int]:
    """
    Run `git pull`.
    Returns (stdout, exit_code).
    """
    try:
        if not branch:
            branch = repo.active_branch.name
        output = repo.git.pull(remote, branch)
        return output, 0
    except git.GitCommandError as e:
        return str(e), e.status
    except Exception as e:
        return str(e), 1
