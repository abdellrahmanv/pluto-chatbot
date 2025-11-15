#!/bin/bash
#
# Boost Microphone Volume Script
#

echo "=========================================="
echo "  Microphone Volume Boost"
echo "=========================================="
echo ""

# Get the card number
CARD=3

echo "Current microphone settings:"
amixer -c $CARD contents | grep -A 10 -i "capture\|mic"

echo ""
echo "Boosting microphone volume to maximum..."

# Try various common microphone control names
amixer -c $CARD sset 'Mic' 100% cap 2>/dev/null && echo "✓ Mic set to 100%"
amixer -c $CARD sset 'Capture' 100% cap 2>/dev/null && echo "✓ Capture set to 100%"
amixer -c $CARD sset 'Mic Boost' 100% 2>/dev/null && echo "✓ Mic Boost set to 100%"
amixer -c $CARD sset 'Input' 100% cap 2>/dev/null && echo "✓ Input set to 100%"
amixer -c $CARD sset 'Mic Capture' 100% cap 2>/dev/null && echo "✓ Mic Capture set to 100%"

# Try to enable auto gain control if available
amixer -c $CARD sset 'Auto Gain Control' on 2>/dev/null && echo "✓ Auto Gain Control enabled"

echo ""
echo "New microphone settings:"
amixer -c $CARD contents | grep -A 10 -i "capture\|mic"

echo ""
echo "=========================================="
echo "Microphone boost complete!"
echo "Run ./test_audio.sh to verify the levels"
echo "=========================================="
