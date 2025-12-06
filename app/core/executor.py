import logging
import asyncio
from typing import Callable, Awaitable, Any, Dict
from app.core.models import ToolCall, AppConfig

# Import Git tool functions
# Note: Using git_ops as the directory name per codebase reality
from app.core.tools.git_ops.status import git_status
from app.core.tools.git_ops.diff import git_diff
from app.core.tools.git_ops.pull import git_pull
from app.core.tools.git_ops.test_runner import run_tests  
from app.core.tools.git_ops.commit_push import smart_commit_push
from app.core.tools.git_ops.branch import git_checkout_branch
from app.core.tools.git_ops.log import git_log
from app.core.tools.git_ops.add import git_add_all
from app.core.tools.git_ops.reset import git_reset

logger = logging.getLogger(__name__)

ToolFunc = Callable[..., Awaitable[Any]]

# Tool Registry
TOOL_REGISTRY: Dict[str, ToolFunc] = {
    "git.status": git_status,
    "git.diff": git_diff,
    "git.pull": git_pull,
    "git.run_tests": run_tests,
    "git.smart_commit_push": smart_commit_push,
    "git.branch": git_checkout_branch,
    "git.log": git_log,
    "git.add_all": git_add_all,
    "git.reset": git_reset,
}

# Simple tools config
SIMPLE_GIT_TOOLS: Dict[str, list[str]] = {
    "git.fetch": ["fetch"],
}

async def execute_tool(tool_call: ToolCall, config: AppConfig = None, brain=None, console=None, _registry: Dict[str, ToolFunc] = None) -> dict:
    """
    Dispatch ToolCall via TOOL_REGISTRY.
    """
    name = tool_call.tool
    params = tool_call.params or {}
    
    logger.info(f"Executing tool: {name} with params: {params}")

    try:
        # 1. Check SIMPLE_GIT_TOOLS
        if name in SIMPLE_GIT_TOOLS:
            from app.core.tools.git_ops.utils import run_git
            extra_args = params.get("extra_args", [])
            # If params has other keys that are list of strings, maybe append them? 
            # But usually params for simple tools might be just extra arguments.
            # For safety, let's just stick to what the user prompt suggested or basic list.
            # The prompt example: `extra_args = params.get("extra_args", [])`
            cmd = SIMPLE_GIT_TOOLS[name] + list(extra_args)
            stdout, code = await run_git(cmd)
            return {"stdout": stdout, "exit_code": code, "success": code == 0}

        # 2. Check TOOL_REGISTRY
        registry = _registry if _registry is not None else TOOL_REGISTRY
        func = registry.get(name)
        if func is None:
            # Fallback for help or unknown
            if name == "help":
                return {"stdout": "I can help you with git commands. Try 'git status' or 'commit changes'.", "exit_code": 0, "success": True}
            
            return {"stdout": "", "stderr": f"Unknown tool: {name}", "exit_code": 1, "success": False}

        # Prepare arguments
        call_params = params.copy()
        
        # Inject dependencies if needed
        # commit_push needs 'brain'
        if name == "git.smart_commit_push":
            if not brain:
                 return {"stdout": "", "stderr": "Brain (LLM) required for smart commit.", "exit_code": 1, "success": False}
            call_params["brain"] = brain
            # confirm_callback might be in params (if passed locally) or we might need it? 
            # Previous executor execution: 
            # confirm_callback = tool_call.params.get("confirm_callback")
            # This is already in params, so copy() preserved it.

        if name == "git.branch":
            branch_name = params.get("name")
            if not branch_name:
                 return {"stdout": "", "stderr": "git.branch requires a 'name' parameter", "exit_code": 1, "success": False}

        if name == "git.run_tests":
             result = await func(**call_params)
             # Result is (stdout, exit_code)
             stdout, code = result
             summary = "All tests passed" if code == 0 else "Tests failed"
             return {"stdout": stdout, "exit_code": code, "success": code == 0, "summary": summary}

        # Execute
        result = await func(**call_params)

        # Normalize result
        # Tuple[str, int] -> {"stdout": ..., "exit_code": ...}
        # Tuple[str, str, int] (commit_push) -> {"commit_message": ..., "stdout": ..., "exit_code": ...}
        # dict -> return as is

        if isinstance(result, tuple):
            if len(result) == 2:
                stdout, code = result
                return {"stdout": stdout, "exit_code": code, "success": code == 0}
            elif len(result) == 3:
                # smart_commit_push returns (commit_msg, stdout, code)
                msg, stdout, code = result
                return {
                    "commit_message": msg,
                    "stdout": stdout,
                    "exit_code": code,
                    "success": code == 0
                }
            else:
                # Unexpected tuple length
                return {"stdout": str(result), "exit_code": 0, "success": True} # Fallback

        if isinstance(result, dict):
            result.setdefault("exit_code", 0)
            if "success" not in result:
                result["success"] = result["exit_code"] == 0
            return result
            
        # Fallback
        return {"stdout": str(result), "exit_code": 0, "success": True}

    except Exception as e:
        logger.exception(f"Tool execution failed: {e}")
        return {"stdout": "", "stderr": str(e), "exit_code": 1, "success": False}
