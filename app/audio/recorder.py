import logging
import time
import uuid
import os
from pathlib import Path
import sounddevice as sd
import soundfile as sf
from app.core.models import AppConfig
import numpy as np

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
        
        self._stream = None
        self._frames = []

    def start_recording(self):
        """Starts recording audio in the background."""
        if self._stream:
            self.stop_recording()
            
        self._frames = []
        
        def callback(indata, frames, time, status):
            if status:
                logger.warning(status)
            self._frames.append(indata.copy())

        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            callback=callback
        )
        self._stream.start()
        logger.info("Recording started...")

    def stop_recording(self) -> str:
        """Stops recording and saves to file."""
        if not self._stream:
            return ""
            
        self._stream.stop()
        self._stream.close()
        self._stream = None
        logger.info("Recording stopped.")
        
        if not self._frames:
            logger.warning("No audio recorded.")
            return ""

        # Concatenate all blocks
        recording = np.concatenate(self._frames, axis=0)
        
        # Save to file
        filename = f"cmd_{uuid.uuid4()}.wav"
        filepath = self.tmp_dir / filename
        
        sf.write(str(filepath), recording, self.sample_rate)
        logger.info(f"Saved audio to {filepath}")
        
        return str(filepath)
