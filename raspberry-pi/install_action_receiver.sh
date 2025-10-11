#!/bin/bash

# Installation script for Raspberry Pi Action Receiver Service
# This script installs the action receiver as a systemd service on Ubuntu 22.04

set -e

echo "=========================================="
echo "Raspberry Pi Action Receiver Installation"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

# Define installation paths
INSTALL_DIR="/opt/pi-action-receiver"
SERVICE_FILE="pi-action-receiver.service"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing action receiver..."
echo "Installation directory: $INSTALL_DIR"
echo ""

# Create installation directory
echo "1. Creating installation directory..."
mkdir -p "$INSTALL_DIR"

# Copy application files
echo "2. Copying application files..."
cp "$SCRIPT_DIR/action_receiver.py" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/requirements.txt" "$INSTALL_DIR/"

# Make the script executable
chmod +x "$INSTALL_DIR/action_receiver.py"

# Create Python virtual environment
echo "3. Creating Python virtual environment..."
python3 -m venv "$INSTALL_DIR/venv"

# Install dependencies
echo "4. Installing Python dependencies..."
"$INSTALL_DIR/venv/bin/pip" install --upgrade pip
"$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt"

# Create .env file if it doesn't exist
if [ ! -f "$INSTALL_DIR/.env" ]; then
    echo "5. Creating .env configuration file..."
    cp "$SCRIPT_DIR/.env.example" "$INSTALL_DIR/.env"
    echo "   ⚠️  Please edit $INSTALL_DIR/.env with your configuration"
else
    echo "5. .env file already exists, skipping..."
fi

# Set proper ownership
echo "6. Setting file ownership..."
if id "pi" &>/dev/null; then
    chown -R pi:pi "$INSTALL_DIR"
else
    echo "   ⚠️  User 'pi' not found. Please set ownership manually."
fi

# Install systemd service
echo "7. Installing systemd service..."
cp "$SCRIPT_DIR/$SERVICE_FILE" /etc/systemd/system/
systemctl daemon-reload

# Create log file directory
echo "8. Setting up logging..."
touch /var/log/pi-action-receiver.log
if id "pi" &>/dev/null; then
    chown pi:pi /var/log/pi-action-receiver.log
fi
chmod 644 /var/log/pi-action-receiver.log

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit the configuration file:"
echo "   sudo nano $INSTALL_DIR/.env"
echo ""
echo "2. Start the service:"
echo "   sudo systemctl start pi-action-receiver"
echo ""
echo "3. Enable auto-start on boot:"
echo "   sudo systemctl enable pi-action-receiver"
echo ""
echo "4. Check service status:"
echo "   sudo systemctl status pi-action-receiver"
echo ""
echo "5. View logs:"
echo "   sudo journalctl -u pi-action-receiver -f"
echo ""
