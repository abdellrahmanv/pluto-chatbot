#!/bin/bash
#
# Audio Test Script - Test microphone recording and levels
#

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "  Pluto Audio Test"
echo "=========================================="
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment not found!"
    exit 1
fi

# Run audio test
python3 - << 'EOF'
import pyaudio
import numpy as np
import yaml
import time

# Load config
with open('config/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

audio_config = config['audio']
sample_rate = audio_config['sample_rate']
channels = audio_config['channels']
chunk_size = audio_config['chunk_size']
silence_threshold = audio_config['silence_threshold']

print("Audio Configuration:")
print(f"  Sample Rate: {sample_rate}")
print(f"  Channels: {channels}")
print(f"  Silence Threshold: {silence_threshold}")
print("")

# List audio devices
audio = pyaudio.PyAudio()
print("Available Audio Devices:")
for i in range(audio.get_device_count()):
    info = audio.get_device_info_by_index(i)
    if info['maxInputChannels'] > 0:
        print(f"  [{i}] {info['name']} - Input channels: {info['maxInputChannels']}")

print("")
print("Testing microphone... Speak now!")
print("Monitoring audio levels for 10 seconds...")
print("")

# Open stream
try:
    stream = audio.open(
        format=pyaudio.paInt16,
        channels=channels,
        rate=sample_rate,
        input=True,
        frames_per_buffer=chunk_size
    )
    
    max_level = 0
    for i in range(int(sample_rate / chunk_size * 10)):  # 10 seconds
        data = stream.read(chunk_size, exception_on_overflow=False)
        audio_data = np.frombuffer(data, dtype=np.int16)
        amplitude = np.abs(audio_data).mean()
        max_level = max(max_level, amplitude)
        
        # Show level every 0.5 seconds
        if i % 8 == 0:
            bar = '#' * int(amplitude / 50)
            status = "SPEECH" if amplitude > silence_threshold else "silence"
            print(f"Level: {amplitude:6.0f} [{bar:20s}] {status}")
    
    stream.stop_stream()
    stream.close()
    
    print("")
    print("=" * 50)
    print(f"Maximum level detected: {max_level:.0f}")
    print(f"Current threshold: {silence_threshold}")
    print("")
    
    if max_level < silence_threshold:
        print("⚠️  WARNING: Your speech level is below the threshold!")
        recommended = int(max_level * 0.5)
        print(f"   Recommended threshold: {recommended}")
        print(f"   Update config.yaml: silence_threshold: {recommended}")
    else:
        print("✓ Speech detection should work!")
    
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    audio.terminate()
EOF

echo ""
echo "Test complete!"
