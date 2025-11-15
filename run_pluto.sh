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
echo "Checking audio devices..."
sleep 2

# List available audio devices
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
