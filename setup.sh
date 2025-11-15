#!/bin/bash
#
# Pluto Chatbot Setup Script for Raspberry Pi 4B
# This script installs all dependencies and configures the system
#

set -e  # Exit on any error

echo "=========================================="
echo "  Pluto Chatbot Setup for Raspberry Pi"
echo "=========================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ] || ! grep -q "Raspberry Pi" /proc/device-tree/model; then
    echo -e "${YELLOW}Warning: This doesn't appear to be a Raspberry Pi${NC}"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${GREEN}Step 1: Updating system packages...${NC}"
sudo apt-get update
sudo apt-get upgrade -y

echo ""
echo -e "${GREEN}Step 2: Installing Python 3 and pip...${NC}"
sudo apt-get install -y python3 python3-pip python3-venv

echo ""
echo -e "${GREEN}Step 3: Installing audio tools and libraries...${NC}"
sudo apt-get install -y \
    portaudio19-dev \
    python3-pyaudio \
    alsa-utils \
    libasound2-dev \
    ffmpeg \
    sox \
    libsox-fmt-all

echo ""
echo -e "${GREEN}Step 4: Installing system dependencies for Whisper...${NC}"
sudo apt-get install -y \
    python3-numpy \
    python3-scipy \
    libopenblas-dev \
    liblapack-dev

echo ""
echo -e "${GREEN}Step 5: Creating Python virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

echo ""
echo -e "${GREEN}Step 6: Upgrading pip...${NC}"
pip install --upgrade pip setuptools wheel

echo ""
echo -e "${GREEN}Step 7: Installing Python packages...${NC}"
pip install \
    openai-whisper \
    PyYAML \
    pyaudio \
    numpy \
    scipy

echo ""
echo -e "${GREEN}Step 8: Installing Piper TTS...${NC}"

# Create directory for Piper
mkdir -p ~/piper
cd ~/piper

# Download Piper (ARM64 version for Raspberry Pi 4B)
echo "Downloading Piper TTS..."
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_arm64.tar.gz

# Extract
echo "Extracting Piper..."
tar -xzf piper_arm64.tar.gz

# Make executable
chmod +x piper/piper

# Add to PATH (add to .bashrc for persistence)
export PATH="$HOME/piper/piper:$PATH"
if ! grep -q 'export PATH="$HOME/piper/piper:$PATH"' ~/.bashrc; then
    echo 'export PATH="$HOME/piper/piper:$PATH"' >> ~/.bashrc
fi

echo ""
echo -e "${GREEN}Step 9: Downloading Piper voice model...${NC}"

# Create models directory
mkdir -p ~/piper/models
cd ~/piper/models

# Download English voice model (lessac - good quality, medium size)
echo "Downloading voice model..."
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/en_US-lessac-medium.onnx
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/en_US-lessac-medium.onnx.json

echo ""
echo -e "${GREEN}Step 10: Configuring audio device (Card 3)...${NC}"

# List audio devices
echo "Available audio devices:"
aplay -l

# Create ALSA configuration for USB audio
cat > ~/.asoundrc << EOF
# Default to USB Audio Device (Card 3)
pcm.!default {
    type hw
    card 3
}

ctl.!default {
    type hw
    card 3
}
EOF

echo "ALSA configured to use Card 3 by default"

# Set audio levels
echo "Setting audio levels..."
amixer -c 3 sset 'Speaker' 80% unmute 2>/dev/null || echo "Speaker control not available"
amixer -c 3 sset 'Mic' 80% cap 2>/dev/null || echo "Mic control not available"

echo ""
echo -e "${GREEN}Step 11: Testing audio setup...${NC}"

# Test speaker
echo "Testing speaker output..."
speaker-test -c 2 -t wav -l 1 2>/dev/null || echo "Speaker test not available"

# Test microphone
echo "You can test the microphone with: arecord -D hw:3 -f cd -d 5 test.wav"

echo ""
echo -e "${GREEN}Step 12: Creating logs directory...${NC}"
cd ~/pluto-chatbot  # Assumes setup script is run from project directory
mkdir -p logs
mkdir -p temp

echo ""
echo "=========================================="
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "To start using Pluto:"
echo "  1. Activate virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run Pluto:"
echo "     python3 main.py"
echo ""
echo "  3. To auto-start on boot, add to crontab:"
echo "     @reboot cd ~/pluto-chatbot && source venv/bin/activate && python3 main.py"
echo ""
echo -e "${YELLOW}Note: Make sure your USB audio device is connected to Raspberry Pi!${NC}"
echo ""
