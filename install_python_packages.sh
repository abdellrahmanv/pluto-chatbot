#!/bin/bash
#
# Quick install script for missing Python packages only
# Use this if setup.sh already ran but Whisper is missing
#

echo "Installing Python packages in virtual environment..."

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"
echo "Working in: $SCRIPT_DIR"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ Virtual environment activated"
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✓ Virtual environment created and activated"
fi

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install packages
echo "Installing Whisper and dependencies..."
echo "This may take 10-15 minutes on Raspberry Pi..."
pip install openai-whisper PyYAML pyaudio numpy scipy

# Verify installation
echo ""
echo "Verifying Whisper installation..."
python3 -c "import whisper; print(f'✓ Whisper version: {whisper.__version__}')" && echo "" || echo "❌ Whisper import failed"

echo ""
echo "✓ Python packages installed!"
echo ""
echo "To verify all components: ./verify_setup.sh"
echo "To start Pluto: source venv/bin/activate && python3 main.py"
