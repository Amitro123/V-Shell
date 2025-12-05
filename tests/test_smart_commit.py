import pytest
from unittest.mock import AsyncMock, Mock, MagicMock, patch
from app.core.executor import execute_tool
from app.core.models import AppConfig, ToolCall

@pytest.mark.asyncio
async def test_smart_commit_push_success():
    # Setup mocks
    config = Mock(spec=AppConfig)
    brain = Mock()
    # Mock sync method for brain.generate_commit_message
    brain.generate_commit_message.return_value = "feat: new feature"
    
    with patch('app.core.executor.get_repo') as mock_get_repo, \
         patch('app.core.executor.smart_commit_push') as mock_commit:
        
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo
        
        # We need to simulate the real tool behavior or trust the mock?
        # Since we are mocking `execute_tool` internals or the tool itself?
        # Actually `execute_tool` calls imports `app.core.tools.git.commit_push.smart_commit_push`
        # But we mocked `app.core.executor.smart_commit_push`.
        # So we just need to ensure the result structure is correct.
        
        mock_commit.return_value = ("feat: new feature", "Committed and pushed\n== git status ==\nOn branch main...", 0)
        
        tool_call = ToolCall(tool="git.smart_commit_push", params={})
        result = await execute_tool(tool_call, config=config, brain=brain)
        
        # Verify
        assert result["success"] is True
        assert "Committed and pushed" in result["stdout"]
        mock_commit.assert_called_once()

@pytest.mark.asyncio
async def test_smart_commit_push_no_changes():
    # Setup mocks
    config = Mock(spec=AppConfig)
    brain = Mock()
    
    with patch('app.core.executor.get_repo') as mock_get_repo, \
         patch('app.core.executor.smart_commit_push') as mock_commit:
        
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo
        mock_commit.return_value = ("", "No changes to commit.", 1)
        
        tool_call = ToolCall(tool="git.smart_commit_push", params={})
        result = await execute_tool(tool_call, config=config, brain=brain)
        
        # Verify fails gracefully
        assert result["success"] is False
        assert "No changes to commit" in result["stdout"]
