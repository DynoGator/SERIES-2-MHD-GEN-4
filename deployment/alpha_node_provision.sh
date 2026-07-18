#!/usr/bin/env bash
# One-shot CM5 provisioning for Penrose, CO
set -euo pipefail

DRY_RUN=0
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=1
    echo "=== DRY-RUN MODE ACTIVATED ==="
fi

run_cmd() {
    if [[ $DRY_RUN -eq 1 ]]; then
        echo "[DRY-RUN] $*"
    else
        echo "[LIVE] $*"
        "$@"
    fi
}

echo "Provisioning CM5 Alpha Node..."

# 1. Hostname
run_cmd hostnamectl set-hostname alpha

# 2. System dependencies
run_cmd apt-get update
run_cmd apt-get install -y python3 python3-pip python3-venv git hdf5-tools gpsd chrony

# 3. Clone and setup venv
run_cmd mkdir -p /opt/2mhd
run_cmd git clone https://github.com/DynoGator/SERIES-2-MHD-GEN-4.git /opt/2mhd/repo
run_cmd python3 -m venv /opt/2mhd/venv
run_cmd /opt/2mhd/venv/bin/pip install -r /opt/2mhd/repo/requirements.txt

# 4. Configure GPSDO LBE-1421
# Placeholder for hardware specific udev rules or gpsd config
run_cmd systemctl enable gpsd
run_cmd systemctl restart gpsd

# 5. Systemd service for node agent
cat << 'EOF' > /tmp/2mhd-node.service
[Unit]
Description=2MHD Node Agent
After=network.target gpsd.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/2mhd/repo
ExecStart=/opt/2mhd/venv/bin/python scripts/run_node_agent.py --node alpha --config config/deployment.yaml
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

run_cmd mv /tmp/2mhd-node.service /etc/systemd/system/2mhd-node.service
run_cmd systemctl daemon-reload
run_cmd systemctl enable 2mhd-node.service
run_cmd systemctl restart 2mhd-node.service

echo "Provisioning complete."
