import git
from typing import Tuple, Any, Optional

async def smart_commit_push(
    repo: git.Repo,
    brain: Any, # Avoid circular import, pass Brain instance
    auto_stage: bool = True,
    push: bool = True,
    confirm_callback: Optional[Any] = None
) -> Tuple[str, str, int]:
    """
    Orchestrates smart commit and push.
    Returns (commit_message, stdout, exit_code).
    """
    try:
        # 1. Status (check if repo is mostly clean)
        # 2. Add all
        if auto_stage:
            repo.git.add("-u")  # Only stage modified/deleted tracked files        
        # 3. Get diff & Generate Message
        diff = repo.git.diff("--staged")
        if not diff:
            return "", "No changes to commit.", 1
            
        message = brain.generate_commit_message(diff)
        if not brain:
            return "", "Brain (LLM) instance required for commit message generation.", 1
            
        message = brain.generate_commit_message(diff)
        
        # Confirmation Step
        if confirm_callback:
            if not confirm_callback(message): # Pass message to verify
                return message, "Smart commit cancelled by user.", 1        # 4. Commit
        repo.git.commit("-m", message)
        
        output = f"Committed: '{message}'"
        
        # 5. Push
        if push:
            branch = repo.active_branch.name
            push_output = repo.git.push("origin", branch)
            output += f"\nPushed to origin/{branch}: {push_output}"
        
        return message, output, 0
        
    except git.GitCommandError as e:
        return "", str(e), e.status
    except Exception as e:
        return "", str(e), 1
