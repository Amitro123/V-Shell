import pytest
import git
from unittest.mock import Mock, MagicMock
from app.core.models import ToolCall, AppConfig
from app.core.executor import execute_tool

@pytest.fixture
def repo_dir(tmp_path):
    """Create a temporary git repository."""
    d = tmp_path / "repo"
    d.mkdir()
    r = git.Repo.init(d)
    r.config_writer().set_value("user", "name", "Test User").release()
    r.config_writer().set_value("user", "email", "test@example.com").release()
    return d

@pytest.fixture
def mock_brain():
    brain = Mock()
    brain.generate_commit_message.return_value = "chore: test commit"
    return brain

@pytest.fixture
def test_config():
    return AppConfig(
        llm_provider="groq",
        auto_confirm_read_only=True,
        require_confirmation_writes=False 
    )

@pytest.mark.asyncio
async def test_integration_status_diff_add(repo_dir, test_config, mock_brain, monkeypatch):
    """Full flow: Status -> Diff -> Smart Commit."""
    repo = git.Repo(repo_dir)
    
    # Patch executor.get_repo to return our temp repo
    monkeypatch.setattr("app.core.executor.get_repo", lambda: repo)
    
    # 1. Status (Clean)
    tool_call = ToolCall(tool="git.status")
    result = await execute_tool(tool_call, config=test_config, brain=mock_brain)
    
    # Debug print
    if not result["success"]:
        print(f"Status failed: {result.get('stderr')}")
        
    assert result["success"]
    assert "On branch" in result["stdout"]
    
    # 2. Make changes
    test_file = repo_dir / "new_file.txt"
    test_file.write_text("content", encoding="utf-8")
    
    # 3. Status (Untracked)
    result = await execute_tool(tool_call, config=test_config, brain=mock_brain)
    assert "new_file.txt" in result["stdout"] or "Untracked files" in result["stdout"]
    
    # 4. Smart Commit 
    # Must use push=False because we have no remote
    commit_call = ToolCall(tool="git.smart_commit_push", params={"push": False})
    
    result = await execute_tool(commit_call, config=test_config, brain=mock_brain)
    
    if not result["success"]:
        print(f"Commit failed: {result.get('stderr')}")

    assert result["success"]
    assert "Committed: 'chore: test commit'" in result["stdout"]
    
    # Verify file IS committed
    assert not repo.is_dirty()
    last_commit = repo.head.commit
    assert last_commit.message.strip() == "chore: test commit"
    # untracked file 'new_file.txt' should now be in the tree if auto_stage worked (it uses add -u or add .)
    # 'git add -u' does NOT add untracked files. 'git add .' does.
    # Logic in smart_commit_push:
    # if not diff_cached and auto_stage:
    #     repo.git.add("-u")
    #     if not diff_cached:
    #         repo.git.add(".") 
    
    # Since we have only untracked files, 'add -u' does nothing. 'diff --staged' is empty.
    # So it hits 'repo.git.add(".")'. This stages the untracked file. 
    # So it SHOULD be committed.
    
    assert "new_file.txt" in last_commit.tree

@pytest.mark.asyncio
async def test_integration_diff(repo_dir, test_config, monkeypatch):
    repo = git.Repo(repo_dir)
    test_file = repo_dir / "a.txt"
    test_file.write_text("v1", encoding="utf-8")
    repo.index.add(["a.txt"])
    repo.index.commit("init")
    
    test_file.write_text("v2", encoding="utf-8")
    
    monkeypatch.setattr("app.core.executor.get_repo", lambda: repo)
    
    tool_call = ToolCall(tool="git.diff")
    result = await execute_tool(tool_call, config=test_config)
    
    assert result["success"]
    assert "diff --git a/a.txt" in result["stdout"]
    assert "+v2" in result["stdout"]
