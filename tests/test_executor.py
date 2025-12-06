import pytest
from unittest.mock import MagicMock, patch
from app.core.executor import execute_tool
from app.core.models import ToolCall, AppConfig

# Mock Git functions directly
@pytest.fixture
def mock_git_modules():
    with patch("app.core.executor.git_status") as mock_status, \
         patch("app.core.executor.smart_commit_push") as mock_commit, \
         patch("app.core.executor.run_tests") as mock_tests, \
         patch("app.core.executor.git_diff") as mock_diff, \
         patch("app.core.executor.git_checkout_branch") as mock_branch:
        
        yield {
            "status": mock_status,
            "commit": mock_commit,
            "tests": mock_tests,
            "diff": mock_diff,
            "branch": mock_branch
        }

@pytest.fixture
def mock_config():
    return AppConfig(
        llm_provider="groq",
        auto_confirm_read_only=True,
        require_confirmation_writes=True
    )

@pytest.mark.asyncio
async def test_execute_status(mock_config, mock_git_modules):
    mock_git_modules["status"].return_value = ("On branch main", 0)
    
    tool_call = ToolCall(tool="git.status")
    result = await execute_tool(tool_call, config=mock_config)
    
    assert result["success"]
    assert result["stdout"] == "On branch main"
    mock_git_modules["status"].assert_called_once()

@pytest.mark.asyncio
async def test_execute_commit(mock_config, mock_git_modules):
    mock_git_modules["commit"].return_value = ("test commit", "master 1234567", 0)
    brain_mock = MagicMock()
    
    tool_call = ToolCall(tool="git.smart_commit_push", params={"push": False})
    
    result = await execute_tool(tool_call, config=mock_config, brain=brain_mock)
    
    assert result["success"]
    assert result["stdout"] == "master 1234567"
    # Logic in executor now passes simple params, and injects brain
    mock_git_modules["commit"].assert_called_once()
    # Check arguments
    call_kwargs = mock_git_modules["commit"].call_args[1]
    assert call_kwargs["push"] is False
    assert call_kwargs["brain"] == brain_mock

@pytest.mark.asyncio
async def test_execute_branch(mock_config, mock_git_modules):
    mock_git_modules["branch"].return_value = ("Switched to branch new-feature", 0)
    
    tool_call = ToolCall(tool="git.branch", params={"name": "new-feature", "create": True})
    result = await execute_tool(tool_call, config=mock_config)
    
    assert result["success"]
    assert "Switched" in result["stdout"]
    mock_git_modules["branch"].assert_called_with(name="new-feature", create=True)

@pytest.mark.asyncio
async def test_execute_diff(mock_config, mock_git_modules):
    mock_git_modules["diff"].return_value = ("diff output", 0)
    
    tool_call = ToolCall(tool="git.diff", params={"path": "app/main.py", "since_origin_main": True})
    result = await execute_tool(tool_call, config=mock_config)
    
    assert result["success"]
    mock_git_modules["diff"].assert_called()
    # verify args - execute_tool unpacks **params, so these should be kwargs
    args = mock_git_modules["diff"].call_args
    assert args[1]["path"] == "app/main.py"
    assert args[1]["since_origin_main"] is True

@pytest.mark.asyncio
async def test_execute_unknown_tool(mock_config, mock_git_modules):
    tool_call = ToolCall(tool="unknown_tool")
    
    result = await execute_tool(tool_call, config=mock_config)
    assert not result["success"]
    # Updated error message matcher
    assert "Unknown tool" in result["stderr"]
