import logging
import git
from rich.console import Console
from app.core.models import ToolCall, AppConfig
from app.core.tools.git.status import git_status
from app.core.tools.git.diff import git_diff
from app.core.tools.git.test_runner import run_tests
from app.core.tools.git.commit_push import smart_commit_push
from app.core.tools.git.pull import git_pull

logger = logging.getLogger(__name__)

# Global repo instance to avoid re-opening on every call (optional optimization)
_repo = None

def get_repo() -> git.Repo:
    global _repo
    if _repo is None:
        try:
            _repo = git.Repo(search_parent_directories=True)
            logger.info(f"Initialized Git repo: {_repo.working_dir}")
        except git.InvalidGitRepositoryError:
            logger.error("Not a valid git repository.")
            raise ValueError("Current directory is not a git repository.")
        except Exception as e:
            logger.error(f"Failed to initialize Git repo: {e}")
            raise e
    return _repo

async def execute_tool(tool_call: ToolCall, config: AppConfig = None, brain=None, console=None) -> dict:
    """
    Dispatch a ToolCall to the correct underlying implementation.
    Returns a dict with at least { "stdout": str, "exit_code": int } and any extra fields.
    """
    name = tool_call.tool
    logger.info(f"Executing tool: {name} with params: {tool_call.params}")

    try:
        repo = get_repo()
    except Exception as e:
        return {"stdout": "", "stderr": str(e), "exit_code": 1, "success": False}

    try:
        if name == "git.status":
            stdout, code = await git_status(repo)
            return {"stdout": stdout, "exit_code": code, "success": code == 0}

        if name == "git.diff":
            path = tool_call.params.get("path")
            # Handle empty path if params has it but it's None
            stdout, code = await git_diff(repo, path=path)
            return {"stdout": stdout, "exit_code": code, "success": code == 0}

        if name == "git.run_tests":
            stdout, code = await run_tests()
            return {"stdout": stdout, "exit_code": code, "success": code == 0}

        if name == "git.smart_commit_push":
            auto_stage = tool_call.params.get("auto_stage", True)
            push = tool_call.params.get("push", True)
            confirm_callback = tool_call.params.get("confirm_callback")
            
            if not brain:
                return {"stdout": "", "stderr": "Brain (LLM) required for smart commit.", "exit_code": 1, "success": False}

            commit_message, stdout, code = await smart_commit_push(
                repo=repo,
                brain=brain,
                auto_stage=auto_stage,
                push=push,
                confirm_callback=confirm_callback
            )
            return {
                "commit_message": commit_message,
                "stdout": stdout,
                "exit_code": code,
                "success": code == 0
            }

        if name == "git.pull":
            remote = tool_call.params.get("remote", "origin")
            branch = tool_call.params.get("branch")
            stdout, code = await git_pull(repo, remote=remote, branch=branch)
            return {"stdout": stdout, "exit_code": code, "success": code == 0}

        if name == "help":
             return {"stdout": "I can help you with git commands. Try 'git status' or 'commit changes'.", "exit_code": 0, "success": True}

        # Future: docker/system tools or legacy/unimplemented git tools
        return {"stdout": "", "stderr": f"Unknown or unimplemented tool: {name}", "exit_code": 1, "success": False}
        
    except Exception as e:
        logger.exception(f"Tool execution failed: {e}")
        return {"stdout": "", "stderr": str(e), "exit_code": 1, "success": False}

# Keep GitExecutor class for backward compatibility if needed, but we should remove it per plan.
# Plan says: "Remove GitExecutor class".

