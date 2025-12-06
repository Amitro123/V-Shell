import pytest
import logging
import asyncio
from unittest.mock import patch, MagicMock
from app.core.tools.git_ops.reset import git_reset

@pytest.mark.asyncio
async def test_reset_validation():
    # Invalid mode
    with pytest.raises(ValueError, match="Unsupported reset mode"):
        await git_reset(mode="dangerous")
        
    # Invalid steps (too high)
    with pytest.raises(ValueError, match="steps must be between"):
        await git_reset(steps=10)
        
    # Invalid steps (too low)
    with pytest.raises(ValueError, match="steps must be between"):
        await git_reset(steps=0)

@pytest.mark.asyncio
async def test_reset_success():
    with patch("app.core.tools.git_ops.reset.run_git", new_callable=MagicMock) as mock_run_git:
        # Configure the mock to return an awaitable
        future = asyncio.Future()
        future.set_result(("HEAD is now at ...", 0))
        mock_run_git.return_value = future
        
        # Test default
        await git_reset() 
        mock_run_git.assert_called_with(["reset", "--hard", "HEAD~1"])
        
        # Test soft with steps
        await git_reset(mode="soft", steps=2)
        mock_run_git.assert_called_with(["reset", "--soft", "HEAD~2"])
