import pytest
from unittest.mock import MagicMock, patch
from app.core.models import AppConfig, ToolCall, GitTool
from app.core.executor import GitExecutor

@pytest.fixture
def mock_config():
    return AppConfig()

@pytest.fixture
def mock_repo():
    with patch("git.Repo") as mock:
        repo_instance = MagicMock()
        mock.return_value = repo_instance
        yield repo_instance

def test_executor_init(mock_config, mock_repo):
    executor = GitExecutor(mock_config)
    assert executor.repo is not None

def test_execute_status(mock_config, mock_repo):
    executor = GitExecutor(mock_config)
    mock_repo.git.status.return_value = "On branch main"
    
    tool_call = ToolCall(tool=GitTool.STATUS)
    result = executor.execute(tool_call)
    
    assert result.success
    assert "On branch main" in result.stdout
    mock_repo.git.status.assert_called_once()

def test_execute_commit(mock_config, mock_repo):
    executor = GitExecutor(mock_config)
    mock_repo.git.commit.return_value = "master 1234567"
    
    tool_call = ToolCall(tool=GitTool.COMMIT, params={"message": "test commit"})
    result = executor.execute(tool_call)
    
    assert result.success
    mock_repo.git.commit.assert_called_with("-m", "test commit")

def test_execute_unknown_tool(mock_config, mock_repo):
    executor = GitExecutor(mock_config)
    # Bypass validation for test
    tool_call = MagicMock()
    tool_call.tool = "unknown_tool"
    tool_call.params = {}
    
    result = executor.execute(tool_call)
    assert not result.success
    assert "Unknown tool" in result.stderr
