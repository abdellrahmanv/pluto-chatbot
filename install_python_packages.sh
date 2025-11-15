#!/bin/bash
#
# Quick install script for missing Python packages only
# Use this if setup.sh already ran but Whisper is missing
#

echo "Installing Python packages in virtual environment..."

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Upgrade pip
pip install --upgrade pip

# Install packages
echo "Installing Whisper and dependencies..."
pip install openai-whisper PyYAML pyaudio numpy scipy

echo ""
echo "✓ Python packages installed!"
echo ""
echo "To verify: ./verify_setup.sh"
echo "To start Pluto: source venv/bin/activate && python3 main.py"
