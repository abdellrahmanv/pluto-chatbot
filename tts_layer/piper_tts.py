"""
Text-to-Speech Layer (Piper)
Converts text to natural speech using Piper TTS
"""

import subprocess
import logging
import yaml
import os


class PiperTTS:
    """Text-to-Speech using Piper"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize Piper TTS"""
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        self.piper_config = config['piper']
        self.model_path = self.piper_config['model_path']
        self.config_path = self.piper_config['config_path']
        self.speaker_id = self.piper_config.get('speaker_id', 0)
        self.noise_scale = self.piper_config.get('noise_scale', 0.667)
        self.length_scale = self.piper_config.get('length_scale', 1.0)
        
        # Check if Piper is installed
        self._check_piper_installation()
        
        self.logger.info("Piper TTS initialized")
    
    def _check_piper_installation(self):
        """Check if Piper is installed and accessible"""
        try:
            result = subprocess.run(
                ['piper', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            self.logger.info(f"Piper version: {result.stdout.strip()}")
        except FileNotFoundError:
            self.logger.warning("Piper not found in PATH. Make sure it's installed.")
        except Exception as e:
            self.logger.warning(f"Could not check Piper installation: {e}")
    
    def synthesize(self, text: str, output_path: str) -> bool:
        """
        Convert text to speech and save to file
        
        Args:
            text: Text to convert to speech
            output_path: Path to save audio file
        
        Returns:
            True if successful, False otherwise
        """
        if not text:
            self.logger.warning("Empty text provided for synthesis")
            return False
        
        self.logger.info(f"Synthesizing speech: '{text[:50]}...'")
        
        try:
            # Build Piper command
            cmd = [
                'piper',
                '--model', self.model_path,
                '--config', self.config_path,
                '--output_file', output_path,
            ]
            
            # Add optional parameters
            if self.speaker_id is not None:
                cmd.extend(['--speaker', str(self.speaker_id)])
            
            # Run Piper
            result = subprocess.run(
                cmd,
                input=text,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.logger.info(f"Speech synthesized successfully: {output_path}")
                return True
            else:
                self.logger.error(f"Piper error: {result.stderr}")
                return False
        
        except FileNotFoundError:
            self.logger.error("Piper executable not found. Please install Piper TTS.")
            return False
        
        except subprocess.TimeoutExpired:
            self.logger.error("Piper synthesis timeout")
            return False
        
        except Exception as e:
            self.logger.error(f"Synthesis error: {e}")
            return False
    
    def speak(self, text: str, audio_player) -> bool:
        """
        Synthesize and play speech
        
        Args:
            text: Text to speak
            audio_player: Audio player instance with play_audio() method
        
        Returns:
            True if successful, False otherwise
        """
        import tempfile
        
        # Create temporary output file
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        temp_path = temp_file.name
        temp_file.close()
        
        try:
            # Synthesize
            if self.synthesize(text, temp_path):
                # Play audio
                audio_player.play_audio(temp_path)
                return True
            return False
        
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
