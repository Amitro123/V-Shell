import pytest
from unittest.mock import AsyncMock, Mock
from app.core.voice_flow import get_voice_confirmation
from app.core.models import STTResult

@pytest.mark.asyncio
async def test_get_voice_confirmation_yes():
    # Setup mocks
    recorder = Mock()
    recorder.record_once.return_value = "dummy_path.wav"
    
    transcriber = AsyncMock()
    transcriber.transcribe.return_value = STTResult(text="yes please")
    
    console = Mock()
    
    # Execute
    result = await get_voice_confirmation("Are you sure?", recorder, transcriber, console)
    
    # Verify
    assert result is True
    recorder.record_once.assert_called_once()
    transcriber.transcribe.assert_called_once_with("dummy_path.wav")

@pytest.mark.asyncio
async def test_get_voice_confirmation_no():
    # Setup mocks
    recorder = Mock()
    recorder.record_once.return_value = "dummy_path.wav"
    
    transcriber = AsyncMock()
    transcriber.transcribe.return_value = STTResult(text="no way")
    
    console = Mock()
    
    # Execute
    result = await get_voice_confirmation("Are you sure?", recorder, transcriber, console)
    
    # Verify
    assert result is False

@pytest.mark.asyncio
async def test_get_voice_confirmation_retry_success():
    # Setup mocks
    recorder = Mock()
    recorder.record_once.return_value = "dummy_path.wav"
    
    transcriber = AsyncMock()
    # First attempt unclear, second attempt yes
    transcriber.transcribe.side_effect = [
        STTResult(text="mumble mumble"),
        STTResult(text="yes do it")
    ]
    
    console = Mock()
    
    # Execute
    result = await get_voice_confirmation("Are you sure?", recorder, transcriber, console)
    
    # Verify
    assert result is True
    assert recorder.record_once.call_count == 2

@pytest.mark.asyncio
async def test_get_voice_confirmation_max_retries_fail():
    # Setup mocks
    recorder = Mock()
    recorder.record_once.return_value = "dummy_path.wav"
    
    transcriber = AsyncMock()
    # All attempts unclear
    transcriber.transcribe.return_value = STTResult(text="mumble")
    
    console = Mock()
    
    # Execute
    result = await get_voice_confirmation("Are you sure?", recorder, transcriber, console, retries=1)
    
    # Verify
    assert result is False
    assert recorder.record_once.call_count == 2 # Initial + 1 retry
