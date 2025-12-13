#!/bin/bash

# Change to the application directory
cd /usr/share/samba-configurator || exit 1

if [ "$EUID" -ne 0 ]; then
  pkexec env DISPLAY="$DISPLAY" \
            XAUTHORITY="$XAUTHORITY" \
            WAYLAND_DISPLAY="$WAYLAND_DISPLAY" \
            XDG_RUNTIME_DIR="$XDG_RUNTIME_DIR" \
            HOME="$HOME" \
            DBUS_SESSION_BUS_ADDRESS="$DBUS_SESSION_BUS_ADDRESS" \
            GTK_THEME="$GTK_THEME" \
            GTK_DATA_PREFIX="$GTK_DATA_PREFIX" \
            /usr/bin/python3 /usr/share/samba-configurator/main.py "$@"
else
  /usr/bin/python3 /usr/share/samba-configurator/main.py "$@"
fi