#!/bin/bash

# Build the Samba Configurator package

VERSION="1.0.6"

echo "Starting build process for Samba Configurator version ${VERSION}..."
debbuild -S -sa
echo "Signing the package..."
debsign ../samba-configurator_${VERSION}_source.changes
echo "Uploading the package to PPA..."
dput ppa:samugallo06/software ../samba-configurator_${VERSION}_source.changes
echo "Building package version ${VERSION}..."
dpkg-buildpackage -b -us -uc
echo "Package build and upload complete."