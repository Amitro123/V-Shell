# Data models
"""Pydantic models for GitVoice."""
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field
class GitTool(str, Enum):
    """Available Git tools."""
    
    STATUS = "git_status"
    LOG = "git_log"
    DIFF = "git_diff"
    ADD_ALL = "git_add_all"
    COMMIT = "git_commit"
    PUSH = "git_push"
    RESET = "git_reset"
    CHECKOUT_BRANCH = "git_checkout_branch"
    CREATE_BRANCH = "git_create_branch"
    HELP = "help"
class ToolCall(BaseModel):
    """Parsed intent as a structured tool call."""
    
    tool: GitTool
    params: dict[str, Any] = Field(default_factory=dict)
    confirmation_required: bool = False
    explanation: Optional[str] = None  # Human-readable explanation of what will happen
class Intent(BaseModel):
    """User's transcribed command with metadata."""
    
    text: str
    confidence: float = 1.0
    timestamp: Optional[str] = None
class CommandResult(BaseModel):
    """Result of executing a Git command."""
    
    success: bool
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    command: Optional[str] = None
class STTResult(BaseModel):
    """Result of speech-to-text transcription."""
    text: str

class AudioConfig(BaseModel):
    """Audio recording configuration."""
    
    sample_rate: int = 16000
    channels: int = 1
    duration: int = 10  # seconds
    wake_word: str = "hey git"
class AppConfig(BaseModel):
    """Main application configuration."""
    
    # LLM settings
    llm_provider: str = "groq"  # groq, gemini, ollama
    groq_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    groq_model: str = "llama-3.1-8b-instant"
    gemini_model: str = "gemini-1.5-flash"
    
    # STT settings
    stt_provider: str = "faster-whisper"  # faster-whisper, groq
    whisper_model: str = "base"  # tiny, base, small, medium, large-v2, large-v3
    
    # Audio settings
    audio: AudioConfig = Field(default_factory=AudioConfig)
    
    # Safety settings
    auto_confirm_read_only: bool = True
    require_confirmation_writes: bool = True
    
    # Logging
    log_level: str = "INFO"
