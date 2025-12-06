"""
Tests for MCP Server integration.
Since FastMCP's @server.tool() decorator transforms functions into FunctionTool objects
(which are not directly callable), we test that the server can be imported and that
the underlying execute_tool logic is sound (covered by test_executor.py).
"""
import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from app.core.models import ToolCall, AppConfig
from app.core.executor import execute_tool


@pytest.fixture
def mock_git_modules():
    """Mock Git functions directly to avoid initializing Repo."""
    # Since we use TOOL_REGISTRY now, we can just mock the registry values
    mock_status = AsyncMock()
    mock_commit = AsyncMock()
    mock_tests = AsyncMock()
    mock_diff = AsyncMock()
    mock_pull = AsyncMock()
    
    return {
        "git.status": mock_status,
        "git.smart_commit_push": mock_commit,
        "git.run_tests": mock_tests,
        "git.diff": mock_diff,
        "git.pull": mock_pull
    }


@pytest.fixture
def mock_config():
    return AppConfig(
        llm_provider="groq",
        auto_confirm_read_only=True,
        require_confirmation_writes=False
    )


def test_mcp_server_imports():
    """Verify MCP server module can be imported without errors."""
    # This test ensures the server module is syntactically correct and imports work
    from app.mcp import server
    assert hasattr(server, 'server')
    assert hasattr(server, 'git_status')


@pytest.mark.asyncio
async def test_mcp_git_status_via_executor(mock_config, mock_git_modules):
    """Test git.status tool call that MCP would dispatch."""
    mock_git_modules["git.status"].return_value = ("On branch main", 0)
    
    with patch.dict("app.core.executor.TOOL_REGISTRY", mock_git_modules):
        tool_call = ToolCall(tool="git.status")
        result = await execute_tool(tool_call, config=mock_config)
        
        assert result["success"] is True
        assert result["stdout"] == "On branch main"
        mock_git_modules["git.status"].assert_called_once()


@pytest.mark.asyncio
async def test_mcp_run_tests_via_executor(mock_config, mock_git_modules):
    """Test git.run_tests tool call that MCP would dispatch."""
    mock_git_modules["git.run_tests"].return_value = ("All tests passed", 0)
    
    with patch.dict("app.core.executor.TOOL_REGISTRY", mock_git_modules):
        tool_call = ToolCall(tool="git.run_tests")
        result = await execute_tool(tool_call, config=mock_config)
        
        assert result["success"] is True
        assert result["stdout"] == "All tests passed"


@pytest.mark.asyncio
async def test_mcp_git_diff_via_executor(mock_config, mock_git_modules):
    """Test git.diff tool call with path parameter."""
    mock_git_modules["git.diff"].return_value = ("diff --git a/file.py", 0)
    
    with patch.dict("app.core.executor.TOOL_REGISTRY", mock_git_modules):
        tool_call = ToolCall(tool="git.diff", params={"path": "file.py"})
        result = await execute_tool(tool_call, config=mock_config)
        
        assert result["success"] is True
        assert "diff" in result["stdout"]


@pytest.mark.asyncio
async def test_mcp_smart_commit_via_executor(mock_config, mock_git_modules):
    """Test git.smart_commit_push tool call that MCP would dispatch."""
    mock_git_modules["git.smart_commit_push"].return_value = ("feat: new feature", "Committed and pushed", 0)
    brain_mock = MagicMock()
    
    with patch.dict("app.core.executor.TOOL_REGISTRY", mock_git_modules):
        tool_call = ToolCall(tool="git.smart_commit_push", params={"auto_stage": True, "push": False})
        result = await execute_tool(tool_call, config=mock_config, brain=brain_mock)
        
        assert result["success"] is True
        assert "Committed" in result["stdout"]


@pytest.mark.asyncio
async def test_mcp_git_pull_via_executor(mock_config, mock_git_modules):
    """Test git.pull tool call with remote and branch."""
    mock_git_modules["git.pull"].return_value = ("Already up to date.", 0)
    
    with patch.dict("app.core.executor.TOOL_REGISTRY", mock_git_modules):
        tool_call = ToolCall(tool="git.pull", params={"remote": "origin", "branch": "main"})
        result = await execute_tool(tool_call, config=mock_config)
        
        assert result["success"] is True
        assert "Already up to date" in result["stdout"]
