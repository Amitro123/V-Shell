import pytest
from unittest.mock import AsyncMock, Mock, patch, PropertyMock
from app.llm.router import Brain, GitTool, ToolCall

# Mock Data
MOCK_TEXT = "git status"
MOCK_CONFIG = Mock()
MOCK_CONFIG.llm_provider = "groq"
MOCK_CONFIG.groq_api_key = "dummy"
MOCK_CONFIG.groq_model = "llama3-70b"

@pytest.fixture
def brain():
    # We patch groq.Groq assuming the library is installed.
    # If it's not installed, we might need a mock module, but requirements says it is.
    with patch("groq.Groq") as mock_groq:
        mock_client = Mock()
        mock_groq.return_value = mock_client
        b = Brain(MOCK_CONFIG)
        b.groq_client = mock_client
        yield b

@pytest.mark.asyncio
async def test_process_empty_text(brain):
    result = await brain.process("")
    assert result.tool == GitTool.HELP
    assert "didn't hear anything" in result.explanation

@pytest.mark.asyncio
async def test_process_setfit_confidence_high(brain):
    # Mock SetFit classifier
    with patch("app.intent.setfit_router.SetFitIntentClassifier") as mock_cls:
        classifier_instance = Mock()
        classifier_instance.predict_intent.return_value = ("git_status", 0.95)
        # Mock lazy loading
        brain._classifier = classifier_instance
        
        result = await brain.process("status")
        
        assert result.tool == GitTool.STATUS
        assert result.confirmation_required is False
        classifier_instance.predict_intent.assert_called_with("status")

@pytest.mark.asyncio
async def test_process_setfit_confidence_low_fallback(brain):
    # Mock SetFit to return low confidence
    with patch("app.intent.setfit_router.SetFitIntentClassifier") as mock_cls:
        classifier_instance = Mock()
        classifier_instance.predict_intent.return_value = ("help", 0.4)
        brain._classifier = classifier_instance
        
        # Mock LLM fallback
        brain._process_llm = AsyncMock(return_value=ToolCall(tool=GitTool.LOG, params={"n": 5}))
        
        result = await brain.process("show logs")
        
        assert result.tool == GitTool.LOG
        brain._process_llm.assert_called_with("show logs")

@pytest.mark.asyncio
async def test_process_setfit_smart_commit_conf_required(brain):
    # Smart commit should require confirmation even if high confidence
    with patch("app.intent.setfit_router.SetFitIntentClassifier") as mock_cls:
        classifier_instance = Mock()
        classifier_instance.predict_intent.return_value = ("smart_commit_push", 0.9)
        brain._classifier = classifier_instance
        
        result = await brain.process("commit this")
        
        assert result.tool == GitTool.SMART_COMMIT_PUSH
        assert result.confirmation_required is True

@patch("app.llm.router.with_retries")
@pytest.mark.asyncio
async def test_process_llm_safety_override(mock_with_retries, brain):
    # Test that dangerous words force confirmation
    brain.provider = "groq"
    
    # Mock inner call to return a tool call WITHOUT confirmation initially
    unsafe_call = ToolCall(tool=GitTool.PUSH, params={}, confirmation_required=False)
    
    # Mock with_retries to return our payload
    mock_with_retries.return_value = unsafe_call
    
    result = await brain._process_llm("force push origin")
    
    # "push" is a dangerous keyword, so it should flip to True
    assert result.confirmation_required is True
