#!/bin/bash
#
# Pluto Launcher Script
# This script ensures the virtual environment is activated before running Pluto
#

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "  Starting Pluto Chatbot"
echo "=========================================="
echo ""
echo "Project directory: $SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Error: Virtual environment not found!"
    echo ""
    echo "Please run setup first:"
    echo "  ./setup.sh"
    echo ""
    echo "Or install Python packages:"
    echo "  ./install_python_packages.sh"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Wait for audio devices to be ready (especially important on boot)
echo "Waiting for audio devices to be ready..."
MAX_WAIT=60
WAIT_COUNT=0

while [ $WAIT_COUNT -lt $MAX_WAIT ]; do
    # Check if card 3 exists
    if aplay -l 2>/dev/null | grep -q "card 3"; then
        echo "✓ Audio device Card 3 found!"
        break
    fi
    
    echo "Waiting for audio device... ($WAIT_COUNT/$MAX_WAIT)"
    sleep 2
    WAIT_COUNT=$((WAIT_COUNT + 2))
done

if [ $WAIT_COUNT -ge $MAX_WAIT ]; then
    echo "⚠️ Warning: Audio device Card 3 not found after ${MAX_WAIT}s, attempting to continue..."
fi

# List available audio devices
echo ""
echo "Available audio devices:"
aplay -l 2>/dev/null || echo "Warning: Could not list audio devices"
echo ""

# Verify critical packages
echo "Checking dependencies..."
python3 -c "import whisper" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Error: Whisper not installed in virtual environment!"
    echo ""
    echo "Please run:"
    echo "  ./install_python_packages.sh"
    exit 1
fi

python3 -c "import yaml, pyaudio, numpy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Error: Required packages not installed!"
    echo ""
    echo "Please run:"
    echo "  ./install_python_packages.sh"
    exit 1
fi

echo "✓ All dependencies found"
echo ""

# Run Pluto
echo "Starting Pluto..."
echo ""
python3 main.py

# Deactivate when done
deactivate
