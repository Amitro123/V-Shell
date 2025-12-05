import pytest
from unittest.mock import MagicMock, patch
from app.core.executor import GitExecutor
from app.core.models import GitTool, ToolCall, AppConfig

@pytest.fixture
def mock_config():
    return AppConfig(
        llm_provider="groq",
        auto_confirm_read_only=True,
        require_confirmation_writes=True
    )

@pytest.fixture
def mock_repo():
    with patch("app.core.executor.git.Repo") as MockRepo:
        mock_repo = MockRepo.return_value
        # Default behavior
        mock_repo.working_dir = "/tmp/repo"
        yield mock_repo

@pytest.mark.asyncio
async def test_execute_status(mock_config, mock_repo):
    executor = GitExecutor(mock_config)
    mock_repo.git.status.return_value = "On branch main"
    
    tool_call = ToolCall(tool=GitTool.STATUS)
    result = await executor.execute(tool_call)
    
    assert result.success
    assert result.stdout == "On branch main"
    mock_repo.git.status.assert_called_once()

@pytest.mark.asyncio
async def test_execute_commit(mock_config, mock_repo):
    executor = GitExecutor(mock_config)
    mock_repo.git.commit.return_value = "master 1234567"
    
    tool_call = ToolCall(tool=GitTool.COMMIT, params={"message": "test commit"})
    result = await executor.execute(tool_call)
    
    assert result.success
    assert result.stdout == "master 1234567"
    mock_repo.git.commit.assert_called_once_with("-m", "test commit")

@pytest.mark.asyncio
async def test_execute_unknown_tool(mock_config, mock_repo):
    executor = GitExecutor(mock_config)
    # Bypass validation for test
    tool_call = MagicMock()
    tool_call.tool = "unknown_tool"
    tool_call.params = {}
    
    result = await executor.execute(tool_call)
    assert not result.success
    assert "Unknown tool" in result.stderr
