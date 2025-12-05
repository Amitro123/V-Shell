from mcp.server.fastmcp import FastMCP
from typing import Optional
from app.mcp.tools import (
    mcp_git_status,
    mcp_run_tests,
    mcp_git_diff,
    mcp_smart_commit_push,
    mcp_git_pull,
)

# Initialize FastMCP server
server = FastMCP("gitvoice")

@server.tool()
async def git_status() -> dict:
    """Show concise git status for the current repository."""
    return await mcp_git_status()

@server.tool()
async def run_tests(command: Optional[str] = None) -> dict:
    """Run the configured test command (e.g. pytest or npm test)."""
    return await mcp_run_tests(command)

@server.tool()
async def git_diff(path: Optional[str] = None) -> dict:
    """Show git diff since last commit."""
    return await mcp_git_diff(path)

@server.tool()
async def smart_commit_push(auto_stage: bool = True, push: bool = True) -> dict:
    """
    Stage changes, generate a commit message, commit, and (optionally) push.
    Clients are expected to obtain human confirmation before calling this tool.
    """
    return await mcp_smart_commit_push(auto_stage=auto_stage, push=push)

@server.tool()
async def git_pull(remote: Optional[str] = None, branch: Optional[str] = None) -> dict:
    """Pull latest changes from the remote."""
    return await mcp_git_pull(remote, branch)

def main():
    server.run()

if __name__ == "__main__":
    main()
