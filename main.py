#!/usr/bin/env python3
"""
Pluto Chatbot - Main Controller
A simple, smart, human-sounding scenario-based chatbot on Raspberry Pi 4B
"""

import os
import sys
import signal
import tempfile
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import setup_logger, Humanizer
from audio_layer import AudioManager
from stt_layer import WhisperSTT
from intent_layer import IntentDetector
from scenario_layer import ScenarioManager
from tts_layer import PiperTTS


class PlutoChatbot:
    """Main controller for Pluto chatbot"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize Pluto chatbot"""
        # Setup logging first
        setup_logger(config_path)
        self.logger = logging.getLogger(__name__)
        self.logger.info("=" * 60)
        self.logger.info("Initializing Pluto Chatbot")
        self.logger.info("=" * 60)
        
        self.config_path = config_path
        self.running = False
        
        # Create temp directory for audio files
        self.temp_dir = "temp"
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
        
        # Initialize all components
        try:
            self.logger.info("Loading components...")
            
            self.audio_manager = AudioManager(config_path)
            self.logger.info("✓ Audio Manager loaded")
            
            self.stt = WhisperSTT(config_path)
            self.logger.info("✓ Whisper STT loaded")
            
            self.intent_detector = IntentDetector(config_path)
            self.logger.info("✓ Intent Detector loaded")
            
            self.scenario_manager = ScenarioManager(config_path)
            self.logger.info("✓ Scenario Manager loaded")
            
            self.tts = PiperTTS(config_path)
            self.logger.info("✓ Piper TTS loaded")
            
            self.humanizer = Humanizer(config_path)
            self.logger.info("✓ Humanizer loaded")
            
            self.logger.info("All components initialized successfully!")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            raise
    
    def speak(self, text: str):
        """Speak text through TTS"""
        self.logger.info(f"Speaking: {text}")
        
        # Humanize the text
        humanized_text = self.humanizer.humanize(text)
        
        # Synthesize and play
        self.tts.speak(humanized_text, self.audio_manager)
    
    def process_audio(self, audio_path: str) -> str:
        """
        Process audio file through the full pipeline
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Response text
        """
        # 1. Speech to Text (Whisper)
        self.logger.info("Step 1: Transcribing audio...")
        transcription = self.stt.transcribe(audio_path)
        
        if not transcription:
            self.logger.warning("Empty transcription")
            return self.scenario_manager.get_response('unknown')
        
        # 2. Intent Detection
        self.logger.info("Step 2: Detecting intent...")
        intent = self.intent_detector.detect(transcription)
        
        # 3. Generate Response (Scenario)
        self.logger.info("Step 3: Generating response...")
        response = self.scenario_manager.get_response(intent)
        
        return response
    
    def listen_and_respond(self):
        """Listen to user, process, and respond"""
        temp_audio = None
        
        try:
            # Record audio - use fixed duration instead of silence detection
            self.logger.info("\n🎤 Listening... (speak now, 3.5 seconds)")
            audio_data = self.audio_manager.record_audio(duration=3.5, stop_on_silence=False)
            
            # If no audio detected at all, share a fun fact
            if audio_data is None or len(audio_data) == 0:
                self.logger.info("No audio detected, sharing a fun fact...")
                response = self.scenario_manager.get_response("fun_fact")
                self.speak(response)
                return
            
            # Save to temporary file
            temp_audio = os.path.join(self.temp_dir, "input.wav")
            self.audio_manager.save_audio(audio_data, temp_audio)
            
            # Process through pipeline
            response = self.process_audio(temp_audio)
            
            # Speak response
            self.speak(response)
            
        except KeyboardInterrupt:
            raise
        
        except Exception as e:
            self.logger.error(f"Error during listen/respond cycle: {e}")
            self.speak("Sorry, I encountered an error. Please try again.")
        
        finally:
            # Clean up temp file
            if temp_audio and os.path.exists(temp_audio):
                try:
                    os.remove(temp_audio)
                except:
                    pass
    
    def start(self):
        """Start the chatbot main loop"""
        self.running = True
        
        # Say startup message
        startup_msg = self.scenario_manager.get_startup_message()
        self.speak(startup_msg)
        
        self.logger.info("\n" + "=" * 60)
        self.logger.info("Pluto is ready! Press Ctrl+C to stop.")
        self.logger.info("=" * 60 + "\n")
        
        # Main loop
        try:
            while self.running:
                self.listen_and_respond()
        
        except KeyboardInterrupt:
            self.logger.info("\nShutdown signal received")
            self.stop()
    
    def stop(self):
        """Stop the chatbot"""
        self.logger.info("Shutting down Pluto...")
        self.running = False
        
        # Say goodbye
        try:
            shutdown_msg = self.scenario_manager.get_shutdown_message()
            self.speak(shutdown_msg)
        except:
            pass
        
        # Cleanup
        try:
            self.audio_manager.cleanup()
        except:
            pass
        
        self.logger.info("Pluto stopped. Goodbye!")


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\nInterrupted by user")
    sys.exit(0)


def main():
    """Main entry point"""
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create and start Pluto
    try:
        pluto = PlutoChatbot()
        pluto.start()
    
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
