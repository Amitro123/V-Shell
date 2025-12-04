import logging
import git
from typing import Any, Dict, Optional
from app.core.models import ToolCall, GitTool, CommandResult, AppConfig

logger = logging.getLogger(__name__)

class GitExecutor:
    """Executes Git commands safely."""
    
    def __init__(self, config: AppConfig):
        self.config = config
        try:
            self.repo = git.Repo(search_parent_directories=True)
            logger.info(f"Initialized GitExecutor in repo: {self.repo.working_dir}")
        except git.InvalidGitRepositoryError:
            logger.error("Not a valid git repository.")
            self.repo = None
        except Exception as e:
            logger.error(f"Failed to initialize Git repo: {e}")
            self.repo = None

    def execute(self, tool_call: ToolCall) -> CommandResult:
        """Executes the requested tool."""
        if not self.repo:
            return CommandResult(success=False, stderr="Current directory is not a git repository.")
        
        tool = tool_call.tool
        params = tool_call.params
        
        logger.info(f"Executing tool: {tool} with params: {params}")
        
        try:
            if tool == GitTool.STATUS:
                return self._git_status()
            elif tool == GitTool.LOG:
                return self._git_log(**params)
            elif tool == GitTool.DIFF:
                return self._git_diff(**params)
            elif tool == GitTool.ADD_ALL:
                return self._git_add_all()
            elif tool == GitTool.COMMIT:
                return self._git_commit(**params)
            elif tool == GitTool.PUSH:
                return self._git_push(**params)
            elif tool == GitTool.RESET:
                return self._git_reset(**params)
            elif tool == GitTool.CHECKOUT_BRANCH:
                return self._git_checkout(**params)
            elif tool == GitTool.CREATE_BRANCH:
                return self._git_create_branch(**params)
            elif tool == GitTool.HELP:
                return CommandResult(success=True, stdout="I can help you with git commands. Try 'git status' or 'commit changes'.")
            else:
                return CommandResult(success=False, stderr=f"Unknown tool: {tool}")
        except git.GitCommandError as e:
            logger.error(f"Git command failed: {e}")
            return CommandResult(success=False, stderr=str(e), exit_code=e.status)
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            return CommandResult(success=False, stderr=str(e))

    def _git_status(self) -> CommandResult:
        status = self.repo.git.status()
        return CommandResult(success=True, stdout=status)

    def _git_log(self, n: int = 5) -> CommandResult:
        log = self.repo.git.log(f"-n {n}", "--pretty=format:%h - %an, %ar : %s")
        return CommandResult(success=True, stdout=log)

    def _git_diff(self, file: Optional[str] = None) -> CommandResult:
        if file:
            diff = self.repo.git.diff(file)
        else:
            diff = self.repo.git.diff()
        return CommandResult(success=True, stdout=diff)

    def _git_add_all(self) -> CommandResult:
        self.repo.git.add(".")
        return CommandResult(success=True, stdout="Staged all changes.")

    def _git_commit(self, message: str) -> CommandResult:
        if not message:
            return CommandResult(success=False, stderr="Commit message is required.")
        output = self.repo.git.commit("-m", message)
        return CommandResult(success=True, stdout=output)

    def _git_push(self, remote: str = "origin", branch: Optional[str] = None) -> CommandResult:
        if not branch:
            branch = self.repo.active_branch.name
        output = self.repo.git.push(remote, branch)
        return CommandResult(success=True, stdout=output)

    def _git_reset(self, mode: str = "soft", commits: int = 1) -> CommandResult:
        # HEAD~N
        target = f"HEAD~{commits}"
        if mode == "hard":
            self.repo.git.reset("--hard", target)
        elif mode == "mixed":
            self.repo.git.reset("--mixed", target)
        else: # soft
            self.repo.git.reset("--soft", target)
        return CommandResult(success=True, stdout=f"Reset {mode} to {target}")

    def _git_checkout(self, branch: str) -> CommandResult:
        self.repo.git.checkout(branch)
        return CommandResult(success=True, stdout=f"Switched to branch '{branch}'")

    def _git_create_branch(self, branch: str) -> CommandResult:
        self.repo.git.checkout("-b", branch)
        return CommandResult(success=True, stdout=f"Created and switched to branch '{branch}'")
