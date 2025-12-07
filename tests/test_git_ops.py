import pytest
from unittest.mock import patch, AsyncMock
from app.core.tools.git_ops.diff import git_diff
from app.core.tools.git_ops.branch import git_checkout_branch

@pytest.mark.asyncio
async def test_git_diff_defaults():
    with patch("app.core.tools.git_ops.diff.run_git", new_callable=AsyncMock) as mock_run:
        mock_run.return_value = ("diff content", 0)
        
        stdout, code = await git_diff()
        
        assert stdout == "diff content"
        assert code == 0
        
        # Check args passed to run_git
        mock_run.assert_called_once_with(["diff", "HEAD"])

@pytest.mark.asyncio
async def test_git_diff_with_path():
    with patch("app.core.tools.git_ops.diff.run_git", new_callable=AsyncMock) as mock_run:
        mock_run.return_value = ("diff content", 0)
        
        await git_diff(path="app/main.py")
        
        mock_run.assert_called_once_with(["diff", "HEAD", "app/main.py"])

@pytest.mark.asyncio
async def test_git_diff_since_origin():
    with patch("app.core.tools.git_ops.diff.run_git", new_callable=AsyncMock) as mock_run:
        mock_run.return_value = ("diff content", 0)
        
        await git_diff(since_origin_main=True)
        
        mock_run.assert_called_once_with(["diff", "origin/main"])

@pytest.mark.asyncio
async def test_git_checkout_existing():
    with patch("app.core.tools.git_ops.branch.run_git", new_callable=AsyncMock) as mock_run:
        mock_run.return_value = ("Switched to branch 'main'", 0)
        
        stdout, code = await git_checkout_branch("main", create=False)
        
        assert "Switched" in stdout
        assert code == 0
        
        mock_run.assert_called_once_with(["checkout", "main"])

@pytest.mark.asyncio
async def test_git_checkout_new():
    with patch("app.core.tools.git_ops.branch.run_git", new_callable=AsyncMock) as mock_run:
        mock_run.return_value = ("Switched to a new branch 'feature'", 0)
        
        stdout, code = await git_checkout_branch("feature", create=True)
        
        assert code == 0
        
        mock_run.assert_called_once_with(["checkout", "-b", "feature"])
