#!/bin/bash

# Build the Samba Configurator package

VERSION="1.0.6"

debbuild -S -sa
debsign ../samba-configurator_${VERSION}_source.changes
dput ppa:samugallo06/software ../samba-configurator_${VERSION}_source.changes