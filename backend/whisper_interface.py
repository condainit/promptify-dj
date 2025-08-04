"""
Whisper interface for audio transcription.
Handles audio file processing and transcription using OpenAI's Whisper model.
"""

import os
import tempfile
from typing import Tuple
from loguru import logger
import whisper
import librosa
import soundfile as sf
from config import Config


class WhisperInterface:
    """Interface for OpenAI Whisper audio transcription."""
    
    def __init__(self, model_name: str = "tiny"):
        self.model_name = model_name
        self.model = None
        logger.info(f"Initializing Whisper interface with model: {model_name}")
    
    def load_model(self):
        """Load Whisper model."""
        try:
            logger.info("Loading Whisper model...")
            self.model = whisper.load_model(self.model_name)
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model '{self.model_name}': {e}")
            logger.error(f"Available models: tiny, base, small, medium, large")
            raise
    
    def _trim_and_resample(self, y, sr: int) -> Tuple:
        """Trim audio to MAX_AUDIO_DURATION and ensure 16kHz sampling."""
        if len(y) / sr > Config.MAX_AUDIO_DURATION:
            logger.warning("Audio exceeds max duration. Trimming.")
            max_samples = int(Config.MAX_AUDIO_DURATION * sr)
            y = y[:max_samples]
        return y, sr

    def _transcribe_and_return(self, audio_input) -> Tuple[str, dict]:
        """Run Whisper transcription and extract metadata."""
        if not audio_input:
            raise ValueError("Audio input is required")
            
        result = self.model.transcribe(audio_input)
        transcript = result.get("text", "").strip()
        
        if not transcript:
            logger.warning("Transcription resulted in empty text")
            
        metadata = {
            "language": result.get("language", "unknown"),
            "segments": len(result.get("segments", [])),
            "duration": result.get("segments", [{}])[-1].get("end", 0) if result.get("segments") else 0
        }
        logger.info(f"Transcription completed. Length: {len(transcript)} chars")
        logger.debug(f"Transcript: {transcript}")
        return transcript, metadata

    def preprocess_audio(self, audio_path: str) -> str:
        """Preprocess audio from file path for Whisper transcription."""
        try:
            logger.info(f"Preprocessing audio file: {audio_path}")
            y, sr = librosa.load(audio_path, sr=16000)
            y, sr = self._trim_and_resample(y, sr)

            temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            sf.write(temp_file.name, y, sr)
            return temp_file.name
        except Exception as e:
            logger.error(f"Failed to preprocess audio file '{audio_path}': {e}")
            logger.error(f"File exists: {os.path.exists(audio_path)}")
            raise
    
    def transcribe(self, audio_path: str) -> Tuple[str, dict]:
        """Transcribe audio file from path."""
        try:
            if self.model is None:
                self.load_model()
            
            processed_audio_path = self.preprocess_audio(audio_path)
            transcript, metadata = self._transcribe_and_return(processed_audio_path)
        finally:
            try:
                os.unlink(processed_audio_path)
            except Exception:
                pass
            return transcript, metadata
    
    def transcribe_from_bytes(self, audio_bytes: bytes, file_extension: str = ".wav") -> Tuple[str, dict]:
        """Transcribe audio from bytes using temporary files."""
        if self.model is None:
            self.load_model()

        raw_path = None
        processed_path = None

        try:
            # Write raw audio to temp file
            raw_temp_file = tempfile.NamedTemporaryFile(suffix=file_extension, delete=False)
            raw_path = raw_temp_file.name
            raw_temp_file.write(audio_bytes)
            raw_temp_file.close()
            
            logger.info(f"Processing {len(audio_bytes)} bytes")

            # Load and process audio
            y, sr = librosa.load(raw_path, sr=16000)
            y, sr = self._trim_and_resample(y, sr)

            # Write processed audio to temp file
            processed_temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            processed_path = processed_temp_file.name
            processed_temp_file.close()
            sf.write(processed_path, y, sr)

            return self._transcribe_and_return(processed_path)
        finally:
            # Clean up temp files
            for path in [raw_path, processed_path]:
                try:
                    if path and os.path.exists(path):
                        os.unlink(path)
                except Exception:
                    pass 
