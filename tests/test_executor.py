import pytest
from unittest.mock import MagicMock, patch
from app.core.executor import execute_tool
from app.core.models import ToolCall, AppConfig

# Mock Git functions directly to avoid initializing Repo
@pytest.fixture
def mock_git_modules():
    with patch("app.core.executor.git_status") as mock_status, \
         patch("app.core.executor.smart_commit_push") as mock_commit, \
         patch("app.core.executor.get_repo") as mock_repo, \
         patch("app.core.executor.run_tests") as mock_tests:
        
        mock_repo.return_value = MagicMock()
        yield {
            "status": mock_status,
            "commit": mock_commit,
            "repo": mock_repo,
            "tests": mock_tests
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
    # smart_commit_push returns 3 values now: msg, stdout, code
    
    result = await execute_tool(tool_call, config=mock_config, brain=brain_mock)
    
    assert result["success"]
    assert result["stdout"] == "master 1234567"
    mock_git_modules["commit"].assert_called_once()

@pytest.mark.asyncio
async def test_execute_unknown_tool(mock_config, mock_git_modules):
    tool_call = ToolCall(tool="unknown_tool")
    
    result = await execute_tool(tool_call, config=mock_config)
    assert not result["success"]
    assert "Unknown or unimplemented tool" in result["stderr"]
