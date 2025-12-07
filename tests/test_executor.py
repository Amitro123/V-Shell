import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.core.executor import execute_tool
from app.core.models import ToolCall, AppConfig

@pytest.fixture
def mock_tools():
    mock_status = AsyncMock()
    mock_commit = AsyncMock()
    mock_tests = AsyncMock()
    mock_diff = AsyncMock()
    mock_branch = AsyncMock()
    mock_log = AsyncMock()
    mock_add = AsyncMock()
    mock_reset = AsyncMock()
    
    return {
        "git.status": mock_status,
        "git.smart_commit_push": mock_commit,
        "git.run_tests": mock_tests,
        "git.diff": mock_diff,
        "git.branch": mock_branch,
        "git.log": mock_log,
        "git.add_all": mock_add,
        "git.reset": mock_reset
    }

@pytest.fixture
def mock_config():
    return AppConfig(
        llm_provider="groq",
        auto_confirm_read_only=True,
        require_confirmation_writes=True
    )

@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_execute_status(mock_config, mock_tools):
    mock_tools["git.status"].return_value = ("On branch main", 0)
    
    tool_call = ToolCall(tool="git.status")
    result = await execute_tool(tool_call, config=mock_config, _registry=mock_tools)
    
    assert result["success"]
    assert result["stdout"] == "On branch main"
    mock_tools["git.status"].assert_called_once()

@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_execute_commit(mock_config, mock_tools):
    mock_tools["git.smart_commit_push"].return_value = ("test commit", "master 1234567", 0)
    brain_mock = MagicMock()
    
    tool_call = ToolCall(tool="git.smart_commit_push", params={"push": False})
    
    result = await execute_tool(tool_call, config=mock_config, brain=brain_mock, _registry=mock_tools)
    
    assert result["success"]
    assert result["stdout"] == "master 1234567"
    mock_tools["git.smart_commit_push"].assert_called_once()
    call_kwargs = mock_tools["git.smart_commit_push"].call_args[1]
    assert call_kwargs["push"] is False
    assert call_kwargs["brain"] == brain_mock

@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_execute_branch(mock_config, mock_tools):
    mock_tools["git.branch"].return_value = ("Switched to branch new-feature", 0)
    
    tool_call = ToolCall(tool="git.branch", params={"name": "new-feature", "create": True})
    result = await execute_tool(tool_call, config=mock_config, _registry=mock_tools)
    
    assert result["success"]
    assert "Switched" in result["stdout"]
    mock_tools["git.branch"].assert_called_with(name="new-feature", create=True)

@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_execute_diff(mock_config, mock_tools):
    mock_tools["git.diff"].return_value = ("diff output", 0)
    
    tool_call = ToolCall(tool="git.diff", params={"path": "app/main.py", "since_origin_main": True})
    result = await execute_tool(tool_call, config=mock_config, _registry=mock_tools)
    
    assert result["success"]
    mock_tools["git.diff"].assert_called()
    args = mock_tools["git.diff"].call_args
    assert args[1]["path"] == "app/main.py"
    assert args[1]["since_origin_main"] is True

@pytest.mark.asyncio
async def test_execute_unknown_tool(mock_config, mock_tools):
    tool_call = ToolCall(tool="unknown_tool")
    result = await execute_tool(tool_call, config=mock_config)
    assert not result["success"]
    assert "Unknown tool" in result["stderr"]

@pytest.mark.asyncio
async def test_execute_simple_tool(mock_config):
    # Test SIMPLE_GIT_TOOLS like git.fetch
    with patch("app.core.tools.git_ops.utils.run_git", new_callable=AsyncMock) as mock_run_git:
        mock_run_git.return_value = ("fetch output", 0)
        
        tool_call = ToolCall(tool="git.fetch", params={"extra_args": ["--all"]})
        result = await execute_tool(tool_call, config=mock_config)
        
        assert result["success"]
        assert result["stdout"] == "fetch output"
        # Check that it combined default args ["fetch"] with extra args ["--all"]
        mock_run_git.assert_called_once_with(["fetch", "--all"])

@pytest.mark.asyncio
async def test_execute_branch_missing_name(mock_config, mock_tools):
    # Test handling of missing 'name' parameter for git.branch
    tool_call = ToolCall(tool="git.branch", params={})
    
    result = await execute_tool(tool_call, config=mock_config)
    
    assert not result["success"]
    assert "git.branch requires a 'name' parameter" in result["stderr"]
    # Ensure tool was NOT called
    mock_tools["git.branch"].assert_not_called()

@pytest.mark.asyncio
async def test_execute_log(mock_config, mock_tools):
    mock_tools["git.log"].return_value = ("commit 123", 0)
    
    tool_call = ToolCall(tool="git.log")
    result = await execute_tool(tool_call, config=mock_config, _registry=mock_tools)
    assert result["success"]
    assert result["stdout"] == "commit 123"

@pytest.mark.asyncio
async def test_execute_add_all(mock_config, mock_tools):
    mock_tools["git.add_all"].return_value = ("", 0)

    tool_call = ToolCall(tool="git.add_all")
    result = await execute_tool(tool_call, config=mock_config, _registry=mock_tools)
    assert result["success"]

@pytest.mark.asyncio
async def test_execute_reset(mock_config, mock_tools):
    mock_tools["git.reset"].return_value = ("HEAD is now...", 0)
    
    tool_call = ToolCall(tool="git.reset", params={"mode": "soft", "steps": 2})
    result = await execute_tool(tool_call, config=mock_config, _registry=mock_tools)
    assert result["success"]
    
@pytest.mark.asyncio
async def test_execute_run_tests_summary(mock_config, mock_tools):
    # run_tests now returns a dict
    mock_tools["git.run_tests"].return_value = {
        "stdout": "output", 
        "exit_code": 0, 
        "summary": "All tests passed"
    }

    tool_call = ToolCall(tool="git.run_tests")
    result = await execute_tool(tool_call, config=mock_config, _registry=mock_tools)
    assert result["success"]
    assert result["summary"] == "All tests passed"
    
    # Fail case
    mock_tools["git.run_tests"].return_value = {
        "stdout": "fail", 
        "exit_code": 1, 
        "summary": "Tests failed"
    }
    result = await execute_tool(tool_call, config=mock_config, _registry=mock_tools)
    assert result["summary"] == "Tests failed"
