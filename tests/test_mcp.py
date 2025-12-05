import pytest
from unittest.mock import AsyncMock, Mock, patch
from app.core.models import ToolCall


@pytest.fixture
def mock_execute_tool():
    with patch("app.mcp.server.execute_tool", new_callable=AsyncMock) as mock_exec:
        # Patch the context getter too since it's used in tools
        with patch("app.mcp.server.get_context") as mock_ctx:
            mock_ctx.return_value = (Mock(), Mock())
            yield mock_exec

# Note: We are testing the mcp/server.py functions directly now, not the deleted tools.py wrappers
# So we import from app.mcp.server
from app.mcp.server import git_status, run_tests, git_diff, smart_commit_push, git_pull

@pytest.mark.asyncio
async def test_mcp_git_status(mock_execute_tool):
    mock_execute_tool.return_value = {"stdout": "On branch main", "exit_code": 0, "success": True}
    
    result = await git_status()
    
    assert result["stdout"] == "On branch main"
    mock_execute_tool.assert_called_once()
    call_args = mock_execute_tool.call_args
    # call_args[0][0] is ToolCall
    assert call_args[0][0].tool == "git.status"

@pytest.mark.asyncio
async def test_mcp_run_tests(mock_execute_tool):
    mock_execute_tool.return_value = {"stdout": "Tests passed", "exit_code": 0, "success": True}
    
    result = await run_tests()
    
    assert result["stdout"] == "Tests passed"
    mock_execute_tool.assert_called_once()
    assert mock_execute_tool.call_args[0][0].tool == "git.run_tests"

@pytest.mark.asyncio
async def test_mcp_git_diff(mock_execute_tool):
    mock_execute_tool.return_value = {"stdout": "diff output", "exit_code": 0, "success": True}
    
    result = await git_diff(path="file.py")
    
    assert result["stdout"] == "diff output"
    mock_execute_tool.assert_called_once()
    tc = mock_execute_tool.call_args[0][0]
    assert tc.tool == "git.diff"
    assert tc.params == {"path": "file.py"}

@pytest.mark.asyncio
async def test_mcp_smart_commit_push(mock_execute_tool):
    mock_execute_tool.return_value = {"commit_message": "test", "stdout": "Committed", "exit_code": 0, "success": True}
    
    result = await smart_commit_push()
    
    assert result["stdout"] == "Committed"
    mock_execute_tool.assert_called_once()
    assert mock_execute_tool.call_args[0][0].tool == "git.smart_commit_push"

@pytest.mark.asyncio
async def test_mcp_git_pull(mock_execute_tool):
    mock_execute_tool.return_value = {"stdout": "Merge conflict", "exit_code": 1, "success": False}
    
    result = await git_pull(remote="upstream", branch="dev")
    
    assert result["stdout"] == "Merge conflict"
    assert result["exit_code"] == 1
    mock_execute_tool.assert_called_once()
    tc = mock_execute_tool.call_args[0][0]
    assert tc.tool == "git.pull"
    assert tc.params == {"remote": "upstream", "branch": "dev"}
