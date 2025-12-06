import git
from typing import Tuple

async def git_status(repo: git.Repo) -> Tuple[str, int]:
    """
    Run `git status -sb` in the current repo.
    Returns (stdout, exit_code).
    """
    try:
        # Using -sb for short branch status like original implementation implied via params or default
        # Original _git_status used self.repo.git.status() which defaults to normal status
        # But _smart_commit_push used -sb. 
        # The prompt example said -sb, but existing code used default status() for the tool `git_status`.
        # I'll stick to `status()` for the main tool to match previous behavior, 
        # or -sb if I want to improve it.
        # Let's match original _git_status implementation: self.repo.git.status()
        status = repo.git.status()
        return status, 0
    except git.GitCommandError as e:
        return str(e), e.status
    except Exception as e:
        return str(e), 1
