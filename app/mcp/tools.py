from typing import Dict, Any, Optional, Tuple
from app.core.models import AppConfig, GitTool, ToolCall
from app.core.executor import GitExecutor
from app.llm.router import Brain

# Global instance for MCP reuse
_executor: Optional[GitExecutor] = None

def get_executor() -> GitExecutor:
    global _executor
    if not _executor:
        config = AppConfig() # Load defaults/env
        brain = Brain(config) # Need brain for smart commits
        # Console=None means less printing side-effects
        _executor = GitExecutor(config=config, brain=brain) 
    return _executor

async def mcp_git_status() -> Dict[str, Any]:
    executor = get_executor()
    result = await executor.execute(ToolCall(tool=GitTool.STATUS))
    return {"status_text": result.stdout if result.success else result.stderr, "exit_code": 0 if result.success else 1}

async def mcp_run_tests(command: Optional[str] = None) -> Dict[str, Any]:
    # command param currently unused in executor, implementation detail
    executor = get_executor()
    result = await executor.execute(ToolCall(tool=GitTool.RUN_TESTS))
    return {"output_text": result.stdout if result.success else result.stderr, "exit_code": 0 if result.success else 1}

async def mcp_git_diff(path: Optional[str] = None) -> Dict[str, Any]:
    executor = get_executor()
    params = {"file": path} if path else {}
    result = await executor.execute(ToolCall(tool=GitTool.DIFF, params=params))
    return {"diff_text": result.stdout if result.success else result.stderr, "exit_code": 0 if result.success else 1}

async def mcp_smart_commit_push(auto_stage: bool = True, push: bool = True) -> Dict[str, Any]:
    # Currently _smart_commit_push does everything.
    # Future work: decompose parameters. For now, it respects the built-in flow.
    executor = get_executor()
    result = await executor.execute(ToolCall(tool=GitTool.SMART_COMMIT_PUSH))
    return {
        "commit_message": "Refer to stdout", # simplified
        "stdout": result.stdout if result.success else result.stderr,
        "exit_code": 0 if result.success else 1
    }

async def mcp_git_pull(remote: Optional[str] = None, branch: Optional[str] = None) -> Dict[str, Any]:
    executor = get_executor()
    params = {}
    if remote: params["remote"] = remote
    if branch: params["branch"] = branch
    
    result = await executor.execute(ToolCall(tool=GitTool.PULL, params=params))
    return {"stdout": result.stdout if result.success else result.stderr, "exit_code": 0 if result.success else 1}
