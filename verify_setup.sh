#!/bin/bash
#
# Quick verification script to check if all dependencies are installed
#

echo "=========================================="
echo "  Pluto Setup Verification"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found"
    echo "   Run: python3 -m venv venv"
    exit 1
else
    echo "✓ Virtual environment found"
fi

# Activate virtual environment
source venv/bin/activate

# Check Python packages
echo ""
echo "Checking Python packages..."

packages=("whisper" "yaml" "pyaudio" "numpy")
all_ok=true

for package in "${packages[@]}"; do
    python3 -c "import $package" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "  ✓ $package installed"
    else
        echo "  ❌ $package NOT installed"
        all_ok=false
    fi
done

# Check Piper
echo ""
echo "Checking Piper TTS..."
if command -v piper &> /dev/null || [ -f "$HOME/piper/piper/piper" ]; then
    echo "  ✓ Piper found"
else
    echo "  ❌ Piper NOT found"
    all_ok=false
fi

# Check voice model
echo ""
echo "Checking voice model..."
if [ -f "$HOME/piper/models/en_US-lessac-medium.onnx" ]; then
    echo "  ✓ Voice model found"
else
    echo "  ❌ Voice model NOT found"
    all_ok=false
fi

echo ""
echo "=========================================="
if [ "$all_ok" = true ]; then
    echo "✓ All dependencies are installed!"
    echo ""
    echo "To start Pluto:"
    echo "  source venv/bin/activate"
    echo "  python3 main.py"
else
    echo "❌ Some dependencies are missing"
    echo ""
    echo "To install missing packages:"
    echo "  source venv/bin/activate"
    echo "  pip install openai-whisper PyYAML pyaudio numpy scipy"
fi
echo "=========================================="
