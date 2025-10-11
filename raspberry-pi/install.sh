#!/bin/bash
#
# Installation script for Raspberry Pi Telemetry Receiver
# This script sets up the telemetry receiver service on Ubuntu 22.04
#

set -e

echo "======================================"
echo "Raspberry Pi Telemetry Receiver Setup"
echo "======================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Variables
INSTALL_DIR="/opt/pi-telemetry-receiver"
SERVICE_NAME="pi-telemetry-receiver"
USER="pi"

# Create installation directory
echo "Creating installation directory..."
mkdir -p "$INSTALL_DIR"

# Copy application files
echo "Copying application files..."
cp telemetry_receiver.py "$INSTALL_DIR/"
cp requirements.txt "$INSTALL_DIR/"
cp .env.example "$INSTALL_DIR/"

# Create .env file if it doesn't exist
if [ ! -f "$INSTALL_DIR/.env" ]; then
    echo "Creating .env file from example..."
    cp "$INSTALL_DIR/.env.example" "$INSTALL_DIR/.env"
    echo ""
    echo "⚠️  IMPORTANT: Edit $INSTALL_DIR/.env with your Azure Service Bus configuration"
    echo ""
fi

# Install Python dependencies
echo "Installing Python dependencies..."
apt-get update
apt-get install -y python3 python3-pip python3-venv

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv "$INSTALL_DIR/venv"

# Install Python packages
echo "Installing Python packages..."
"$INSTALL_DIR/venv/bin/pip" install --upgrade pip
"$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt"

# Create log file directory
echo "Creating log directory..."
mkdir -p /var/log
touch /var/log/pi-telemetry-receiver.log

# Set permissions
echo "Setting permissions..."
chown -R "$USER:$USER" "$INSTALL_DIR"
chown "$USER:$USER" /var/log/pi-telemetry-receiver.log

# Install systemd service
echo "Installing systemd service..."
cp "$SERVICE_NAME.service" "/etc/systemd/system/$SERVICE_NAME.service"

# Reload systemd
echo "Reloading systemd..."
systemctl daemon-reload

echo ""
echo "======================================"
echo "Installation Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Edit the configuration file: $INSTALL_DIR/.env"
echo "2. Start the service: sudo systemctl start $SERVICE_NAME"
echo "3. Enable auto-start on boot: sudo systemctl enable $SERVICE_NAME"
echo "4. Check service status: sudo systemctl status $SERVICE_NAME"
echo "5. View logs: sudo journalctl -u $SERVICE_NAME -f"
echo ""
