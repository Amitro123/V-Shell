import pytest
from unittest.mock import AsyncMock, Mock, patch
from app.core.executor import GitExecutor
from app.core.models import AppConfig, CommandResult

@pytest.mark.asyncio
async def test_smart_commit_push_success():
    # Setup mocks
    config = Mock(spec=AppConfig)
    brain = Mock()
    brain.generate_commit_message.return_value = "feat: new feature"
    console = Mock()
    
    # Mock Git Repo
    with patch('app.core.executor.git.Repo') as MockRepo:
        mock_repo = MockRepo.return_value
        mock_repo.git.status.return_value = "M file.txt"
        mock_repo.git.diff.return_value = "diff content"
        mock_repo.active_branch.name = "main"
        
        executor = GitExecutor(config, brain, console=console)
        
        # Execute
        result = await executor._smart_commit_push()
        
        # Verify
        assert result.success is True
        assert "Committed and pushed" in result.stdout
        
        # Verify flow
        mock_repo.git.status.assert_called_with("-sb")
        mock_repo.git.add.assert_called_with(".")
        mock_repo.git.diff.assert_called_with("--staged")
        brain.generate_commit_message.assert_called()
        mock_repo.git.commit.assert_called_with("-m", "feat: new feature")
        mock_repo.git.push.assert_called_with("origin", "main")

@pytest.mark.asyncio
async def test_smart_commit_push_no_changes():
    # Setup mocks
    config = Mock(spec=AppConfig)
    brain = Mock()
    console = Mock()
    
    with patch('app.core.executor.git.Repo') as MockRepo:
        mock_repo = MockRepo.return_value
        mock_repo.git.diff.return_value = "" # No staged changes
        
        executor = GitExecutor(config, brain, console=console)
        
        result = await executor._smart_commit_push()
        
        # Verify fails gracefully
        assert result.success is False
        assert "No changes to commit" in result.stderr
        mock_repo.git.commit.assert_not_called()
