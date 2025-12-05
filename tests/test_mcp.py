import pytest
from unittest.mock import AsyncMock, Mock, patch
from app.core.models import GitTool, ToolCall, CommandResult
from app.mcp.tools import (
    mcp_git_status,
    mcp_run_tests,
    mcp_git_diff,
    mcp_smart_commit_push,
    mcp_git_pull
)

@pytest.fixture
def mock_executor():
    with patch("app.mcp.tools.get_executor") as mock_get:
        executor = Mock()
        executor.execute = AsyncMock()
        mock_get.return_value = executor
        yield executor

@pytest.mark.asyncio
async def test_mcp_git_status(mock_executor):
    mock_executor.execute.return_value = CommandResult(success=True, stdout="On branch main")
    
    result = await mcp_git_status()
    
    assert result == {"status_text": "On branch main", "exit_code": 0}
    mock_executor.execute.assert_called_once()
    call_args = mock_executor.execute.call_args[0][0]
    assert call_args.tool == GitTool.STATUS

@pytest.mark.asyncio
async def test_mcp_run_tests(mock_executor):
    mock_executor.execute.return_value = CommandResult(success=True, stdout="Tests passed")
    
    result = await mcp_run_tests(command="pytest")
    
    assert result == {"output_text": "Tests passed", "exit_code": 0}
    mock_executor.execute.assert_called_once()
    call_args = mock_executor.execute.call_args[0][0]
    assert call_args.tool == GitTool.RUN_TESTS

@pytest.mark.asyncio
async def test_mcp_git_diff(mock_executor):
    mock_executor.execute.return_value = CommandResult(success=True, stdout="diff output")
    
    result = await mcp_git_diff(path="file.py")
    
    assert result == {"diff_text": "diff output", "exit_code": 0}
    mock_executor.execute.assert_called_once()
    call_args = mock_executor.execute.call_args[0][0]
    assert call_args.tool == GitTool.DIFF
    assert call_args.params == {"file": "file.py"}

@pytest.mark.asyncio
async def test_mcp_smart_commit_push(mock_executor):
    mock_executor.execute.return_value = CommandResult(success=True, stdout="Committed")
    
    result = await mcp_smart_commit_push()
    
    assert result["stdout"] == "Committed"
    assert result["exit_code"] == 0
    mock_executor.execute.assert_called_once()
    call_args = mock_executor.execute.call_args[0][0]
    assert call_args.tool == GitTool.SMART_COMMIT_PUSH

@pytest.mark.asyncio
async def test_mcp_git_pull(mock_executor):
    mock_executor.execute.return_value = CommandResult(success=False, stderr="Merge conflict")
    
    result = await mcp_git_pull(remote="upstream", branch="dev")
    
    assert result == {"stdout": "Merge conflict", "exit_code": 1}
    mock_executor.execute.assert_called_once()
    call_args = mock_executor.execute.call_args[0][0]
    assert call_args.tool == GitTool.PULL
    assert call_args.params == {"remote": "upstream", "branch": "dev"}
