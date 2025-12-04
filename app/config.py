# Application configuration
"""Configuration management for GitVoice."""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from app.core.models import AppConfig, AudioConfig
def load_config(config_path: Optional[Path] = None) -> AppConfig:
    """Load configuration from environment variables and .env file."""
    
    # Load .env file
    if config_path:
        load_dotenv(config_path)
    else:
        load_dotenv()
    
    # Audio configuration
    audio_config = AudioConfig(
        sample_rate=int(os.getenv("AUDIO_SAMPLE_RATE", "16000")),
        channels=int(os.getenv("AUDIO_CHANNELS", "1")),
        duration=int(os.getenv("RECORDING_DURATION", "10")),
        wake_word=os.getenv("WAKE_WORD", "hey git"),
    )
    
    # Main configuration
    config = AppConfig(
        llm_provider=os.getenv("LLM_PROVIDER", "groq"),
        groq_api_key=os.getenv("GROQ_API_KEY"),
        gemini_api_key=os.getenv("GEMINI_API_KEY"),
        groq_model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
        stt_provider=os.getenv("STT_PROVIDER", "faster-whisper"),
        whisper_model=os.getenv("WHISPER_MODEL", "base"),
        audio=audio_config,
        auto_confirm_read_only=os.getenv("AUTO_CONFIRM_READ_ONLY", "true").lower() == "true",
        require_confirmation_writes=os.getenv("REQUIRE_CONFIRMATION_WRITES", "true").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )
    
    return config
