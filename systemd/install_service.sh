#!/bin/bash
set -e

echo "Installing 2MHDBMRIPS systemd service..."

# Symlink to /opt
if [ ! -L /opt/2mhd-digital-twin ]; then
    echo "Creating symlink to /opt/2mhd-digital-twin..."
    ln -s $(pwd) /opt/2mhd-digital-twin
fi

# Copy service
echo "Copying service file..."
cp systemd/2mhd-digital-twin.service /etc/systemd/system/

echo "Reloading daemon and enabling service..."
systemctl daemon-reload
systemctl enable 2mhd-digital-twin
systemctl start 2mhd-digital-twin

echo "Installation complete."
