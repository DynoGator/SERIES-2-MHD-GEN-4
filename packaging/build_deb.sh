#!/bin/bash
set -e

# 1. Run tests
source venv/bin/activate
export PYTHONPATH=.
pytest tests/ -v

# 2. PyInstaller
pyinstaller --onefile --windowed --name=2mhd-digital-twin gui/main.py

# 3. Assemble DEB tree
DEB_DIR="packaging/2mhd-digital-twin_1.0.0_amd64"
rm -rf ${DEB_DIR}
mkdir -p ${DEB_DIR}/DEBIAN
mkdir -p ${DEB_DIR}/opt/2mhd-digital-twin
mkdir -p ${DEB_DIR}/usr/share/applications

# Copy control files
cp packaging/debian/control ${DEB_DIR}/DEBIAN/
cp packaging/debian/postinst ${DEB_DIR}/DEBIAN/
cp packaging/debian/prerm ${DEB_DIR}/DEBIAN/
chmod 755 ${DEB_DIR}/DEBIAN/postinst ${DEB_DIR}/DEBIAN/prerm

# Copy binary and assets
cp dist/2mhd-digital-twin ${DEB_DIR}/opt/2mhd-digital-twin/
cp -r gui/assets ${DEB_DIR}/opt/2mhd-digital-twin/

# Copy desktop file
cp packaging/2mhd-digital-twin.desktop ${DEB_DIR}/usr/share/applications/

# 4. Build DEB
dpkg-deb --build ${DEB_DIR}

echo "DEB built at packaging/2mhd-digital-twin_1.0.0_amd64.deb"
