import asyncio
import logging
from typing import Tuple, Any, Optional
from .utils import run_git

logger = logging.getLogger(__name__)

async def generate_commit_message_with_timeout(brain: Any, diff: str, timeout: float = 5.0) -> str:
    """
    Call generate_commit_message with a timeout.
    On timeout or error, fall back to a generic commit message.
    """
    async def _generate():
        if asyncio.iscoroutinefunction(brain.generate_commit_message):
            return await brain.generate_commit_message(diff)
        return brain.generate_commit_message(diff)

    try:
        logger.info("Generating commit message with LLM...")
        if asyncio.iscoroutinefunction(brain.generate_commit_message):
            msg = await asyncio.wait_for(_generate(), timeout=timeout)
        else:
            loop = asyncio.get_running_loop()
            msg = await asyncio.wait_for(
                loop.run_in_executor(None, brain.generate_commit_message, diff), 
                timeout=timeout
            )
        logger.info("Commit message ready.")
        return msg
    except asyncio.TimeoutError:
        logger.warning("LLM timed out while generating commit message. Falling back to generic message.")
    except Exception as e:
        logger.error(f"LLM failed while generating commit message: {e}")

    return "chore: update project files"

async def smart_commit_push(
    brain: Any,  # Removed 'repo'
    auto_stage: bool = True,
    push: bool = True,
    confirm_callback: Optional[Any] = None
) -> Tuple[str, str, int]:
    """
    Orchestrates smart commit and push with strict sequential logic.
    Returns (commit_message, stdout, exit_code).
    """
    stdout_parts = []
    
    try:
        # 1. Status (Fast local check)
        status_out, status_code = await run_git(["status", "-sb"])
        if status_code != 0:
            return "", f"Git status failed: {status_out}", status_code
        stdout_parts.append(f"== git status ==\n{status_out}")
        
        # 2. Add (if needed) and check staged
        diff_cached, _ = await run_git(["diff", "--staged"])

        if auto_stage:
            # Stage all changes
            await run_git(["add", "-A"])
            diff_cached, _ = await run_git(["diff", "--staged"])

        if not diff_cached:
            return "", "No changes to commit.", 1

        # 3. Generate Message
        commit_message = await generate_commit_message_with_timeout(brain, diff_cached)
        stdout_parts.append(f"\n== commit message ==\n{commit_message}")

        # Confirmation Step
        if confirm_callback:
            if not confirm_callback(commit_message):
                return commit_message, "Smart commit cancelled by user.", 1
        
        # 4. Commit
        _, commit_code = await run_git(["commit", "-m", commit_message])
        if commit_code != 0:
            return commit_message, f"Git commit failed.", commit_code

        # Re-construct success output loosely based on previous behavior
        commit_out = f"Committed: '{commit_message}'"
        stdout_parts.append(f"\n== git commit ==\n{commit_out}")
        
        # 5. Push (optional)
        if push:
            # Need current branch name for explicit push? 
            # Or just `git push` which defaults to current branch in most configs?
            # Existing code used `repo.active_branch.name`.
            # We can get branch name via `git branch --show-current`
            branch_name, _ = await run_git(["branch", "--show-current"])
            branch_name = branch_name.strip()
            
            # If we can't find branch name (detached head), git push might fail unless upstream set.
            # We'll just try `git push origin <branch>` if we have branch, else `git push`.
            push_args = ["push"]
            if branch_name:
                push_args.extend(["origin", branch_name])
            
            push_out, push_code = await run_git(push_args)
            if push_code != 0:
                stdout_parts.append(f"\n== git push failed ==\n{push_out}")
                # We return 0 for overall success if commit worked? Or failure?
                # Usually if push fails, it's a "partial success" or failure.
                # Previous code: return ... stdout, 0. But if push threw exception, it returned error.
                # Here if push fails, we probably should signal it.
                # However, consistent with "commit worked", maybe we just log it in stdout.
                # For now let's return error code if push fails.
                return commit_message, "\n".join(stdout_parts), push_code

            stdout_parts.append(f"\n== git push ==\n{push_out}")
        
        return commit_message, "\n".join(stdout_parts), 0
        
    except Exception as e:
        logger.exception("Smart commit failed")
        return "", str(e), 1

async def git_commit(message: str) -> Tuple[str, int]:
    """
    Commit changes with a specific message.
    """
    if not message:
         return "Commit message is required.", 1
    return await run_git(["commit", "-m", message])

async def git_push(remote: str = "origin", branch: str = "") -> Tuple[str, int]:
    """
    Push changes to remote.
    """
    args = ["push", remote]
    if branch:
        args.append(branch)
    return await run_git(args)
