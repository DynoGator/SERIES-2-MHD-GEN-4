#!/bin/bash
set -e

echo "Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Installing dependencies..."
pip install -e .
pip install PyQt6 pyqtgraph h5py numpy scipy

echo "Creating desktop entry..."
mkdir -p ~/.local/share/applications
cat > ~/.local/share/applications/2mhd-digital-twin.desktop <<EOF
[Desktop Entry]
Name=2MHDBMRIPS Digital Twin
Comment=GEN-4.0-PRA MHD Validation Platform
Exec=$(pwd)/venv/bin/python $(pwd)/gui/main.py
Icon=$(pwd)/gui/assets/icons/app_icon.svg
Type=Application
Categories=Science;Engineering;Physics;
Terminal=false
StartupNotify=true
EOF

update-desktop-database ~/.local/share/applications || true
echo "Installation complete!"
