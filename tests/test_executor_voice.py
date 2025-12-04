import pytest
from unittest.mock import AsyncMock, Mock, patch
from app.core.executor import GitExecutor
from app.core.models import AppConfig, CommandResult

@pytest.mark.asyncio
async def test_smart_commit_push_full_flow():
    # Setup mocks
    config = Mock(spec=AppConfig)
    brain = Mock()
    brain.generate_commit_message.return_value = "feat: new feature"
    
    recorder = Mock()
    transcriber = Mock()
    console = Mock()
    
    # Mock voice confirmation to always return True
    with patch('app.core.executor.get_voice_confirmation', new_callable=AsyncMock) as mock_confirm:
        mock_confirm.return_value = True
        
        # Mock Git Repo
        with patch('app.core.executor.git.Repo') as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.git.status.return_value = "M file.txt"
            mock_repo.git.diff.return_value = "diff content"
            mock_repo.active_branch.name = "main"
            
            executor = GitExecutor(config, brain, recorder, transcriber, console)
            
            # Execute
            result = await executor._smart_commit_push()
            
            # Verify
            assert result.success is True
            assert "Committed and pushed" in result.stdout
            
            # Verify flow
            # 1. Status check
            mock_repo.git.status.assert_called_with("-sb")
            # 2. Add
            mock_repo.git.add.assert_called_with(".")
            # 3. Diff
            mock_repo.git.diff.assert_called_with("--staged")
            # 4. Generate message
            brain.generate_commit_message.assert_called()
            # 5. Commit
            mock_repo.git.commit.assert_called_with("-m", "feat: new feature")
            # 6. Push
            mock_repo.git.push.assert_called_with("origin", "main")
            
            # Verify voice confirmations were asked
            assert mock_confirm.call_count == 3 # Stage, Message, Push

@pytest.mark.asyncio
async def test_smart_commit_push_cancel_stage():
    # Setup mocks
    config = Mock(spec=AppConfig)
    brain = Mock()
    recorder = Mock()
    transcriber = Mock()
    console = Mock()
    
    with patch('app.core.executor.get_voice_confirmation', new_callable=AsyncMock) as mock_confirm:
        # Say NO to staging
        mock_confirm.return_value = False
        
        with patch('app.core.executor.git.Repo') as MockRepo:
            mock_repo = MockRepo.return_value
            executor = GitExecutor(config, brain, recorder, transcriber, console)
            
            result = await executor._smart_commit_push()
            
            assert result.success is False
            assert "Cancelled by user at staging" in result.stderr
            mock_repo.git.add.assert_not_called()

@pytest.mark.asyncio
async def test_smart_commit_push_cancel_push():
    # Setup mocks
    config = Mock(spec=AppConfig)
    brain = Mock()
    brain.generate_commit_message.return_value = "feat: new feature"
    recorder = Mock()
    transcriber = Mock()
    console = Mock()
    
    with patch('app.core.executor.get_voice_confirmation', new_callable=AsyncMock) as mock_confirm:
        # Yes to Stage, Yes to Message, NO to Push
        mock_confirm.side_effect = [True, True, False]
        
        with patch('app.core.executor.git.Repo') as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.git.diff.return_value = "diff"
            mock_repo.active_branch.name = "main"
            
            executor = GitExecutor(config, brain, recorder, transcriber, console)
            
            result = await executor._smart_commit_push()
            
            assert result.success is True
            assert "did NOT push" in result.stdout
            mock_repo.git.commit.assert_called()
            mock_repo.git.push.assert_not_called()
