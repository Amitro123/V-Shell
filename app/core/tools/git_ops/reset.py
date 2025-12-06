from typing import Tuple
from .utils import run_git

VALID_RESET_MODES = {"hard", "soft", "mixed"}

async def git_reset(mode: str = "hard", steps: int = 1) -> Tuple[str, int]:
    """
    Safely reset HEAD back by a small, controlled number of commits.

    Args:
        mode: one of {"hard", "soft", "mixed"}.
        steps: number of commits to go back (default 1).
    """
    if mode not in VALID_RESET_MODES:
        raise ValueError(f"Unsupported reset mode: {mode}")

    if steps < 1 or steps > 3:
        # hard limit to prevent catastrophic resets
        raise ValueError("steps must be between 1 and 3 for safety")

    target = f"HEAD~{steps}"
    return await run_git(["reset", f"--{mode}", target])
