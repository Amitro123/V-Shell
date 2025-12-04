import logging
import time
import uuid
import os
from pathlib import Path
import sounddevice as sd
import soundfile as sf
from app.core.models import AppConfig

logger = logging.getLogger(__name__)

class AudioRecorder:
    """Handles audio recording."""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.audio_config = config.audio
        self.sample_rate = self.audio_config.sample_rate
        self.channels = self.audio_config.channels
        
        # Create temp directory for audio files
        self.tmp_dir = Path(".tmp_audio")
        self.tmp_dir.mkdir(exist_ok=True)

    def record_once(self, duration: int = None) -> str:
        """
        Records audio for a specified duration.
        Saves to a WAV file and returns the path.
        """
        if duration is None:
            duration = self.audio_config.duration
            
        logger.info(f"Recording command for {duration} seconds...")
        
        recording = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype='float32', # soundfile expects float32 usually
            blocking=True
        )
        
        logger.info("Recording complete.")
        
        # Save to file
        filename = f"cmd_{uuid.uuid4()}.wav"
        filepath = self.tmp_dir / filename
        
        sf.write(str(filepath), recording, self.sample_rate)
        logger.info(f"Saved audio to {filepath}")
        
        return str(filepath)
