# Samba Configurator

[![Made with Python](https://img.shields.io/badge/Made%20with-Python-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![GTK](https://img.shields.io/badge/GTK-4.0-7FE719?logo=gtk&logoColor=white)](https://www.gtk.org/)
[![GNOME App](https://img.shields.io/badge/GNOME%20App-Ready-2EA2FF?logo=gnome&logoColor=white)](https://www.gnome.org/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

A modern GTK4 application for managing Samba shared folders on Linux systems.

## Features

- 📁 Create and manage network shares with a GUI
- 👥 Configure user access permissions
- 🔒 Set read-only and guest access options
- ⚙️ Advanced options for masks and browsing settings
- 📝 Visual smb.conf parser and editor
- 🎨 Native GTK4 interface

## Requirements

- Python 3.10+
- GTK 4.0
- Samba server installed

## Installation

### Auto install script

```bash
git clone https://github.com/SamuGallo-06/zorin-share
cd zorin-share
sudo ./install.sh
```

### Install using .deb package

- Download the latest .deb release package from the release section
- Open a terminal in your downloads folder and run the following command, replacing `x.y.z` with the correct version

```bash
sudo apt install ./samba-configurator_x.y.z_all.deb
```


## Usage

Run the application and use the GUI to add, edit, or remove Samba shares without manually editing configuration files.

### Main Features

- **Add New Shares**: Click "New Shared Folder" to create a new network share
- **Edit Shares**: Click the edit button next to any share to modify its settings
- **Delete Shares**: Remove shares you no longer need
- **User Management**: Add or remove specific users who can access each share
- **Advanced Options**: Configure file masks, directory permissions, and browsing settings

## Project Structure

```
samba-configurator/
├── main.py              # Main application entry point
├── dialogs.py           # Dialog windows (Add/Edit folder)
├── shared_elements.py     # SharedFolder data class
└── utils.py             # Utility functions (smb.conf parser)
```

## Development

This application is built with:
- **Python 3** - Core programming language
- **GTK 4** - Modern UI framework
- **GObject** - Event loop and signals

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Built with ❤️ for easier Samba configuration management
