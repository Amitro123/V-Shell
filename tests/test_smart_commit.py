import pytest
from unittest.mock import AsyncMock, Mock, MagicMock, patch
from app.core.executor import execute_tool
from app.core.models import AppConfig, ToolCall

@pytest.mark.asyncio
async def test_smart_commit_push_success():
    config = Mock(spec=AppConfig)
    brain = Mock()
    brain.generate_commit_message.return_value = "feat: new feature"
    
    mock_commit = AsyncMock()
    mock_commit.return_value = ("feat: new feature", "Committed and pushed\n== git status ==\nOn branch main...", 0)
    
    # Patch TOOL_REGISTRY directly
    with patch.dict("app.core.executor.TOOL_REGISTRY", {"git.smart_commit_push": mock_commit}):
        
        tool_call = ToolCall(tool="git.smart_commit_push", params={})
        result = await execute_tool(tool_call, config=config, brain=brain)
        
        assert result["success"] is True
        assert "Committed and pushed" in result["stdout"]
        mock_commit.assert_called_once()
        assert mock_commit.call_args[1]["brain"] == brain

@pytest.mark.asyncio
async def test_smart_commit_push_no_changes():
    config = Mock(spec=AppConfig)
    brain = Mock()
    
    mock_commit = AsyncMock()
    mock_commit.return_value = ("", "No changes to commit.", 1)
    
    with patch.dict("app.core.executor.TOOL_REGISTRY", {"git.smart_commit_push": mock_commit}):
        
        tool_call = ToolCall(tool="git.smart_commit_push", params={})
        result = await execute_tool(tool_call, config=config, brain=brain)
        
        assert result["success"] is False
        assert "No changes to commit" in result["stdout"]
