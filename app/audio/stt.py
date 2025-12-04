import logging
import io
import os
from typing import Union
import numpy as np
from app.core.models import AppConfig, STTResult

logger = logging.getLogger(__name__)

class Transcriber:
    """Handles speech-to-text transcription."""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.provider = config.stt_provider
        self.model_size = config.whisper_model
        self.groq_client = None
        self.whisper_model = None
        
        logger.info(f"Initializing Transcriber with provider: {self.provider}")
        
        if self.provider == "groq":
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=config.groq_api_key)
            except ImportError:
                logger.error("Groq library not installed. Please install 'groq'.")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
                
        elif self.provider == "faster-whisper":
            try:
                from faster_whisper import WhisperModel
                # Use CPU by default for broader compatibility
                device = "cpu" 
                compute_type = "int8"
                logger.info(f"Loading faster-whisper model '{self.model_size}' on {device}...")
                self.whisper_model = WhisperModel(self.model_size, device=device, compute_type=compute_type)
                logger.info("faster-whisper model loaded.")
            except ImportError:
                logger.error("faster-whisper library not installed. Please install 'faster-whisper'.")
            except Exception as e:
                logger.error(f"Failed to initialize faster-whisper: {e}")

    async def transcribe(self, audio_input: Union[str, bytes]) -> STTResult:
        """
        Transcribes audio to text.
        Accepts file path (str) or raw audio bytes.
        Returns STTResult object with .text attribute.
        """
        text = ""
        
        if not audio_input:
            logger.warning("Empty audio input received.")
            return STTResult(text="")

        try:
            if self.provider == "groq" and self.groq_client:
                # Handle file path
                if isinstance(audio_input, str) and os.path.exists(audio_input):
                    with open(audio_input, "rb") as f:
                        transcription = self.groq_client.audio.transcriptions.create(
                            file=(os.path.basename(audio_input), f.read()),
                            model="whisper-large-v3",
                            response_format="text"
                        )
                        text = str(transcription).strip()
                # Handle bytes (legacy/fallback)
                elif isinstance(audio_input, bytes):
                    # Wrap bytes in a named buffer for Groq
                    # Note: Groq might require a valid WAV header
                    import soundfile as sf
                    audio_array = np.frombuffer(audio_input, dtype=np.int16)
                    wav_io = io.BytesIO()
                    sf.write(wav_io, audio_array, self.config.audio.sample_rate, format='WAV')
                    wav_io.seek(0)
                    wav_io.name = "audio.wav"
                    
                    transcription = self.groq_client.audio.transcriptions.create(
                        file=(wav_io.name, wav_io.read()),
                        model="whisper-large-v3",
                        response_format="text"
                    )
                    text = str(transcription).strip()
            
            elif self.provider == "faster-whisper" and self.whisper_model:
                if isinstance(audio_input, str):
                    # faster-whisper accepts file path directly
                    # Enforce English to avoid hallucinations
                    segments, info = self.whisper_model.transcribe(audio_input, beam_size=5, language="en")
                    # Convert segments generator to list for logging
                    segments_list = list(segments)
                    logger.info(f"Raw whisper segments: {segments_list}")
                    text = " ".join([segment.text for segment in segments_list]).strip()
                    language = info.language if hasattr(info, 'language') else 'unknown'
                    language_probability = info.language_probability if hasattr(info, 'language_probability') else 0.0
                    logger.info(f"Final text: {text!r}, language: {language}, probability: {language_probability}")
                elif isinstance(audio_input, bytes):
                    # faster-whisper expects float32 numpy array
                    audio_array = np.frombuffer(audio_input, dtype=np.int16).astype(np.float32) / 32768.0
                    # Enforce English to avoid hallucinations
                    segments, info = self.whisper_model.transcribe(audio_array, beam_size=5, language="en")
                    # Convert segments generator to list for logging
                    segments_list = list(segments)
                    logger.info(f"Raw whisper segments: {segments_list}")
                    text = " ".join([segment.text for segment in segments_list]).strip()
                    language = info.language if hasattr(info, 'language') else 'unknown'
                    language_probability = info.language_probability if hasattr(info, 'language_probability') else 0.0
                    logger.info(f"Final text: {text!r}, language: {language}, probability: {language_probability}")
            
            else:
                logger.error("No valid STT provider configured or initialized.")
                
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            
        return STTResult(text=text)
