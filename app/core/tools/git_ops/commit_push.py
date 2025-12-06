import asyncio
import logging
import git
from typing import Tuple, Any, Optional

logger = logging.getLogger(__name__)

async def generate_commit_message_with_timeout(brain: Any, diff: str, timeout: float = 5.0) -> str:
    """
    Call generate_commit_message with a timeout.
    On timeout or error, fall back to a generic commit message.
    """
    async def _generate():
        # Wrap synchronous brain call if it's blocking, but here assuming it might allow async access 
        # or we accept it blocks the thread briefly.
        # If brain.generate_commit_message is async, await it. If sync, just call it.
        if asyncio.iscoroutinefunction(brain.generate_commit_message):
            return await brain.generate_commit_message(diff)
        return brain.generate_commit_message(diff)

    try:
        logger.info("Generating commit message with LLM...")
        # wait_for requires a coroutine
        if asyncio.iscoroutinefunction(brain.generate_commit_message):
            msg = await asyncio.wait_for(_generate(), timeout=timeout)
        else:
            # If it's sync, we can't easily timeout without running in executor
            # For MVP, just run it. If strict timeout needed for sync code, use run_in_executor
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

    # Simple, deterministic fallback
    return "chore: update project files"

async def smart_commit_push(
    repo: git.Repo,
    brain: Any, 
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
        status_out = repo.git.status("-sb")
        stdout_parts.append(f"== git status ==\n{status_out}")
        
        # 2. Add (if needed)
        # Check staged changes
        diff_cached = repo.git.diff("--staged")

        # If auto_stage is requested, we generally want to capture ALL changes
        # (modified, deleted, untracked) to ensure the commit reflects the current state.
        # However, we only do this if there are no staged changes OR if we want to ensure everything is included.
        # The previous logic only triggered if nothing was staged.
        # But if the user staged one file but forgot another, smart commit should probably stage the rest?
        # For safety/predictability, if the user MANUALLY staged something, we might respect that and NOT auto-stage others?
        # But "smart commit" usually implies "do it all".
        # Let's stick to: if nothing staged, stage everything. If something staged, assume user knows what they are doing?
        # OR: always stage everything if auto_stage=True.
        # Let's assume auto_stage=True means "Stage all changes".

        if auto_stage:
            repo.git.add("-A") # Stages all changes (modified, deleted, untracked)
            diff_cached = repo.git.diff("--staged")

        if not diff_cached:
            return "", "No changes to commit.", 1

        # 3. Generate Message (Single LLM call with timeout)
        commit_message = await generate_commit_message_with_timeout(brain, diff_cached)
        stdout_parts.append(f"\n== commit message ==\n{commit_message}")

        # Confirmation Step
        if confirm_callback:
            if not confirm_callback(commit_message):
                return commit_message, "Smart commit cancelled by user.", 1
        
        # 4. Commit
        repo.git.commit("-m", commit_message)
        commit_out = f"Committed: '{commit_message}'"
        stdout_parts.append(f"\n== git commit ==\n{commit_out}")
        
        # 5. Push (optional)
        if push:
            branch = repo.active_branch.name
            push_output = repo.git.push("origin", branch)
            stdout_parts.append(f"\n== git push ==\n{push_output}")
        
        return commit_message, "\n".join(stdout_parts), 0
        
    except git.GitCommandError as e:
        return "", str(e), e.status
    except Exception as e:
        logger.exception("Smart commit failed")
        return "", str(e), 1
