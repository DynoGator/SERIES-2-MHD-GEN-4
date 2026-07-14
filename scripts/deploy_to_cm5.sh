#!/bin/bash
set -e

CM5_IP=${1:-"192.168.1.50"}
USER="dynogator"

echo "Deploying to CM5 at $CM5_IP..."

# Rsync
rsync -avz --exclude-from='.gitignore' ./ $USER@$CM5_IP:/opt/2mhd-digital-twin/

# Install service
ssh $USER@$CM5_IP "sudo bash /opt/2mhd-digital-twin/systemd/install_service.sh"

echo "Deployment complete."
