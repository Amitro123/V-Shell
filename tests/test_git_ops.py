import pytest
from unittest.mock import patch, MagicMock
from app.core.tools.git_ops.diff import git_diff
from app.core.tools.git_ops.branch import git_checkout_branch

@pytest.mark.asyncio
async def test_git_diff_defaults():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="diff content", stderr="", returncode=0)
        
        stdout, code = await git_diff()
        
        assert stdout == "diff content"
        assert code == 0
        
        # Check default args
        args = mock_run.call_args[0][0]
        assert args == ["git", "diff", "HEAD"]

@pytest.mark.asyncio
async def test_git_diff_with_path():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="diff content", stderr="", returncode=0)
        
        await git_diff(path="app/main.py")
        
        args = mock_run.call_args[0][0]
        assert args == ["git", "diff", "HEAD", "app/main.py"]

@pytest.mark.asyncio
async def test_git_diff_since_origin():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="diff content", stderr="", returncode=0)
        
        await git_diff(since_origin_main=True)
        
        args = mock_run.call_args[0][0]
        assert args == ["git", "diff", "origin/main"]

@pytest.mark.asyncio
async def test_git_checkout_existing():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="Switched to branch 'main'", stderr="", returncode=0)
        
        stdout, code = await git_checkout_branch("main", create=False)
        
        assert "Switched" in stdout
        assert code == 0
        
        args = mock_run.call_args[0][0]
        assert args == ["git", "checkout", "main"]

@pytest.mark.asyncio
async def test_git_checkout_new():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="Switched to a new branch 'feature'", stderr="", returncode=0)
        
        stdout, code = await git_checkout_branch("feature", create=True)
        
        assert code == 0
        
        args = mock_run.call_args[0][0]
        assert args == ["git", "checkout", "-b", "feature"]
