#!/bin/bash
#
# Auto-Start Setup Script for Pluto Chatbot
# This configures Pluto to start automatically on Raspberry Pi boot
#

set -e

echo "=========================================="
echo "  Pluto Auto-Start Setup"
echo "=========================================="
echo ""

# Get the script directory (where pluto-chatbot is located)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
USER=$(whoami)

echo "Configuration:"
echo "  Install directory: $SCRIPT_DIR"
echo "  User: $USER"
echo ""

# Create the systemd service file
echo "Creating systemd service file..."

sudo tee /etc/systemd/system/pluto.service > /dev/null << EOF
[Unit]
Description=Pluto Chatbot Auto-Start
After=network.target sound.target alsa-restore.service
Wants=sound.target

[Service]
Type=simple
ExecStartPre=/bin/sleep 10
ExecStart=/bin/bash -c "cd $SCRIPT_DIR && ./run_pluto.sh"
WorkingDirectory=$SCRIPT_DIR
Restart=on-failure
RestartSec=10
User=$USER
StandardOutput=journal
StandardError=journal
Environment="AUDIODEV=hw:3"
Environment="ALSA_CARD=3"

[Install]
WantedBy=multi-user.target
EOF

echo "✓ Service file created at /etc/systemd/system/pluto.service"
echo ""

# Reload systemd to recognize the new service
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload
echo "✓ Systemd reloaded"
echo ""

# Enable the service to start on boot
echo "Enabling Pluto service to start on boot..."
sudo systemctl enable pluto.service
echo "✓ Pluto service enabled"
echo ""

echo "=========================================="
echo "✓ Auto-Start Setup Complete!"
echo "=========================================="
echo ""
echo "Pluto will now start automatically when you boot your Raspberry Pi!"
echo ""
echo "Useful commands:"
echo "  Start Pluto now:     sudo systemctl start pluto.service"
echo "  Stop Pluto:          sudo systemctl stop pluto.service"
echo "  Restart Pluto:       sudo systemctl restart pluto.service"
echo "  Check status:        sudo systemctl status pluto.service"
echo "  View logs:           sudo journalctl -u pluto.service -f"
echo "  Disable auto-start:  sudo systemctl disable pluto.service"
echo ""
echo "To test it now without rebooting:"
echo "  sudo systemctl start pluto.service"
echo "  sudo journalctl -u pluto.service -f"
echo ""
