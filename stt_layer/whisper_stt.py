"""
Speech-to-Text Layer (Whisper)
Converts audio to text using OpenAI Whisper
"""

import whisper
import logging
import yaml
import os


class WhisperSTT:
    """Speech-to-Text using Whisper"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize Whisper STT"""
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        self.whisper_config = config['whisper']
        self.model_size = self.whisper_config['model_size']
        self.language = self.whisper_config['language']
        self.device = self.whisper_config['device']
        
        # Load Whisper model
        self.logger.info(f"Loading Whisper model: {self.model_size}")
        self.model = whisper.load_model(self.model_size, device=self.device)
        self.logger.info("Whisper model loaded successfully")
    
    def transcribe(self, audio_path: str) -> str:
        """
        Transcribe audio file to text
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Transcribed text
        """
        if not os.path.exists(audio_path):
            self.logger.error(f"Audio file not found: {audio_path}")
            return ""
        
        self.logger.info(f"Transcribing audio: {audio_path}")
        
        try:
            # Transcribe using Whisper
            result = self.model.transcribe(
                audio_path,
                language=self.language,
                fp16=False  # Use FP32 for CPU
            )
            
            text = result['text'].strip()
            self.logger.info(f"Transcription: '{text}'")
            
            return text
        
        except Exception as e:
            self.logger.error(f"Transcription error: {e}")
            return ""
    
    def transcribe_raw(self, audio_data: bytes, sample_rate: int = 16000) -> str:
        """
        Transcribe raw audio data (not yet implemented - requires temp file)
        
        Args:
            audio_data: Raw audio bytes
            sample_rate: Audio sample rate
        
        Returns:
            Transcribed text
        """
        # This would require saving to temp file first
        # For now, use transcribe() with saved file
        raise NotImplementedError("Use transcribe() with audio file path")
