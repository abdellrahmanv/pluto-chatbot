"""
Audio Handler Layer
Manages audio input/output using USB Audio Device (Card 3)
"""

import pyaudio
import wave
import numpy as np
import logging
from typing import Optional
import yaml


class AudioManager:
    """Handles audio recording and playback through USB audio device"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize audio manager with configuration"""
        self.logger = logging.getLogger(__name__)
        
        # Suppress ALSA warnings
        import os
        os.environ['ALSA_CARD'] = 'default'
        
        # Load configuration
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        self.audio_config = config['audio']
        self.sample_rate = self.audio_config['sample_rate']
        self.channels = self.audio_config['channels']
        self.chunk_size = self.audio_config['chunk_size']
        self.card_index = self.audio_config['card_index']
        self.silence_threshold = self.audio_config['silence_threshold']
        self.silence_duration = self.audio_config['silence_duration']
        
        # Redirect ALSA errors to /dev/null
        try:
            from ctypes import CFUNCTYPE, c_char_p, c_int, cdll
            ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
            def py_error_handler(filename, line, function, err, fmt):
                pass
            c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
            asound = cdll.LoadLibrary('libasound.so.2')
            asound.snd_lib_error_set_handler(c_error_handler)
        except:
            pass  # If suppression fails, continue anyway
        
        self.audio = pyaudio.PyAudio()
        self.device_index = self._find_usb_device()
        
        if self.device_index is None:
            self.logger.warning(f"USB device Card {self.card_index} not found, using default device")
    
    def _find_usb_device(self) -> Optional[int]:
        """Find the USB audio device by card index"""
        device_count = self.audio.get_device_count()
        
        for i in range(device_count):
            try:
                device_info = self.audio.get_device_info_by_index(i)
                device_name = device_info.get('name', '')
                max_input = device_info.get('maxInputChannels', 0)
                max_output = device_info.get('maxOutputChannels', 0)
                
                # Check if this is our USB device and has audio channels
                if ('usb' in device_name.lower() or str(self.card_index) in device_name):
                    if max_input > 0 or max_output > 0:
                        self.logger.info(f"Found USB audio device: {device_name} at index {i}")
                        return i
            except Exception as e:
                self.logger.debug(f"Error checking device {i}: {e}")
                continue
        
        # If not found, try to find any device with both input and output
        self.logger.warning(f"USB device Card {self.card_index} not found, searching for any usable device...")
        for i in range(device_count):
            try:
                device_info = self.audio.get_device_info_by_index(i)
                if device_info.get('maxInputChannels', 0) > 0 and device_info.get('maxOutputChannels', 0) > 0:
                    self.logger.info(f"Using device: {device_info.get('name')} at index {i}")
                    return i
            except:
                continue
        
        return None
    
    def list_audio_devices(self):
        """List all available audio devices for debugging"""
        device_count = self.audio.get_device_count()
        self.logger.info("Available audio devices:")
        
        for i in range(device_count):
            device_info = self.audio.get_device_info_by_index(i)
            self.logger.info(f"  [{i}] {device_info['name']} - "
                           f"Inputs: {device_info['maxInputChannels']}, "
                           f"Outputs: {device_info['maxOutputChannels']}")
    
    def record_audio(self, duration: Optional[float] = None, 
                     stop_on_silence: bool = True) -> bytes:
        """
        Record audio from the microphone
        
        Args:
            duration: Recording duration in seconds (None for voice-activated)
            stop_on_silence: Stop recording after detecting silence
        
        Returns:
            Raw audio data as bytes
        """
        frames = []
        
        # Open stream with error handling
        try:
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=self.device_index,
                frames_per_buffer=self.chunk_size,
                stream_callback=None
            )
        except Exception as e:
            self.logger.error(f"Failed to open audio stream: {e}")
            self.logger.info("Trying with default device...")
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
        
        self.logger.info("Recording started...")
        
        if duration:
            # Fixed duration recording
            num_chunks = int(self.sample_rate / self.chunk_size * duration)
            for _ in range(num_chunks):
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                frames.append(data)
        else:
            # Voice-activated recording with silence detection
            silence_chunks = 0
            max_silence_chunks = int(self.silence_duration * self.sample_rate / self.chunk_size)
            speech_detected = False
            min_speech_chunks = 5  # Minimum chunks before checking for silence
            
            self.logger.info("Listening for speech...")
            
            while True:
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                frames.append(data)
                
                # Check audio level
                audio_data = np.frombuffer(data, dtype=np.int16)
                amplitude = np.abs(audio_data).mean()
                
                # Debug: show audio level every 10 chunks
                if len(frames) % 10 == 0:
                    self.logger.debug(f"Audio level: {amplitude:.0f} (threshold: {self.silence_threshold})")
                
                # Detect speech
                if amplitude > self.silence_threshold:
                    speech_detected = True
                    silence_chunks = 0
                    if len(frames) == 1:
                        self.logger.info("Speech detected!")
                elif speech_detected and len(frames) > min_speech_chunks:
                    # Only count silence after speech has been detected
                    silence_chunks += 1
                    if silence_chunks >= max_silence_chunks:
                        self.logger.info("Silence detected, stopping recording")
                        break
                
                # Safety limit: max 4.5 seconds
                if len(frames) > self.sample_rate / self.chunk_size * 4.5:
                    self.logger.info("Maximum recording time (4.5s) reached")
                    break
        
        stream.stop_stream()
        stream.close()
        
        self.logger.info("Recording stopped")
        
        return b''.join(frames)
    
    def save_audio(self, audio_data: bytes, filepath: str):
        """Save audio data to WAV file"""
        with wave.open(filepath, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_data)
        
        self.logger.info(f"Audio saved to {filepath}")
    
    def play_audio(self, filepath: str):
        """Play audio file through speakers"""
        import subprocess
        
        # Try using aplay directly (more reliable on Raspberry Pi)
        try:
            self.logger.info(f"Playing audio with aplay: {filepath}")
            result = subprocess.run(
                ['aplay', filepath],
                capture_output=True,
                timeout=30
            )
            if result.returncode == 0:
                self.logger.info("Playback finished")
                return
            else:
                self.logger.warning(f"aplay failed: {result.stderr.decode()}")
        except Exception as e:
            self.logger.warning(f"aplay not available: {e}")
        
        # Fallback to PyAudio
        try:
            with wave.open(filepath, 'rb') as wf:
                # Get file parameters
                file_channels = wf.getnchannels()
                file_rate = wf.getframerate()
                file_width = wf.getsampwidth()
                
                self.logger.info(f"Playing audio with PyAudio: {filepath} (channels: {file_channels}, rate: {file_rate})")
                
                try:
                    stream = self.audio.open(
                        format=self.audio.get_format_from_width(file_width),
                        channels=file_channels,  # Use file's channel count
                        rate=file_rate,  # Use file's sample rate
                        output=True,
                        output_device_index=self.device_index
                    )
                except Exception as e:
                    self.logger.warning(f"Failed to open output stream with device index: {e}")
                    self.logger.info("Trying default output device...")
                    stream = self.audio.open(
                        format=self.audio.get_format_from_width(file_width),
                        channels=file_channels,
                        rate=file_rate,
                        output=True
                    )
                
                # Read and play audio in chunks
                data = wf.readframes(self.chunk_size)
                while data:
                    stream.write(data)
                    data = wf.readframes(self.chunk_size)
                
                stream.stop_stream()
                stream.close()
                
                self.logger.info("Playback finished")
        
        except Exception as e:
            self.logger.error(f"Error playing audio: {e}")
    
    def cleanup(self):
        """Clean up audio resources"""
        self.audio.terminate()
        self.logger.info("Audio manager cleaned up")
