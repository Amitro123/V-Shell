from fastmcp import FastMCP
from typing import Optional
from app.core.executor import execute_tool
from app.core.models import ToolCall, AppConfig
from app.llm.router import Brain # Needed for smart_commit_push
from app.config import load_config

# Initialize FastMCP server
server = FastMCP("gitvoice")

# Lazy load config and brain to avoid startup cost issues or side effects
_config = None
_brain = None

def get_context():
    global _config, _brain
    if not _config:
        _config = load_config()
    if not _brain:
        _brain = Brain(_config)
    return _config, _brain

@server.tool()
async def git_status() -> dict:
    """Show concise git status for the current repository."""
    config, brain = get_context()
    tc = ToolCall(tool="git.status", params={}, confirmation_required=False)
    # execute_tool logic returns dict
    return await execute_tool(tc, config=config, brain=brain)

@server.tool()
async def run_tests() -> dict:
    """Run the project test suite using pytest."""
    config, brain = get_context()
    tc = ToolCall(tool="git.run_tests", params={}, confirmation_required=False)
    return await execute_tool(tc, config=config, brain=brain)

@server.tool()
async def git_diff(path: Optional[str] = None) -> dict:
    """Show git diff since last commit."""
    config, brain = get_context()
    tc = ToolCall(tool="git.diff", params={"path": path}, confirmation_required=False)
    return await execute_tool(tc, config=config, brain=brain)

@server.tool()
async def smart_commit_push(auto_stage: bool = True, push: bool = True) -> dict:
    """
    Stage changes, generate a commit message, commit, and (optionally) push.
    Clients are expected to obtain human confirmation before calling this tool.
    """
    config, brain = get_context()
    # Confirm callback needs to be handled by client side or assumed confirmed if calling this tool
    # For MCP, we assume the agent/IDE handles "Do you want to run smart_commit?"
    # execute_tool expects a callback if we want safety, OR we can pass None and implicitly trust tool call.
    # The new prompt says "Clients are expected to obtain human confirmation".
    # So we pass None for callback, which means NO CHECK inside the tool function itself if implemented that way?
    # Wait, smart_commit_push implementation: if confirm_callback provided, it asks. If NOT provided, it proceeds?
    # checking code: `if confirm_callback: if not callback(): return cancel`
    # So if None, it proceeds automatically. This is correct for MCP where agent confirms.
    
    tc = ToolCall(tool="git.smart_commit_push", params={"auto_stage": auto_stage, "push": push}, confirmation_required=False)
    return await execute_tool(tc, config=config, brain=brain)

@server.tool()
async def git_pull(remote: Optional[str] = None, branch: Optional[str] = None) -> dict:
    """Pull latest changes from the remote."""
    config, brain = get_context()
    tc = ToolCall(tool="git.pull", params={"remote": remote, "branch": branch}, confirmation_required=False)
    return await execute_tool(tc, config=config, brain=brain)

def main():
    server.run()

if __name__ == "__main__":
    main()
